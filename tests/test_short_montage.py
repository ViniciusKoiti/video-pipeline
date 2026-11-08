"""RF7: `vp short tempos | sfx | juntar | boca` e a mixagem; WAVs e kit pequenos, ffmpeg real, sem rede."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.media.loudness import integrated_lufs
from app.media.probe import duration_ms
from app.media.short_mix import MixError, has_audio, mix_audio, mix_filter
from app.pipeline.motion_inputs import MotionInputError, load_narration

# --- o filtro do ffmpeg ------------------------------------------------------------------------------------


def test_the_filter_delays_each_line_until_its_scene_and_closes_on_the_target() -> None:
    text = mix_filter([0, 2000], 8.2)
    assert "[1:a]aformat=sample_rates=48000:channel_layouts=mono,adelay=0|0[v0]" in text
    assert "[2:a]aformat=sample_rates=48000:channel_layouts=mono,adelay=2000|2000[v1]" in text
    assert "[v0][v1]amix=inputs=2:normalize=0" in text
    assert "apad=whole_dur=8.200" in text and "loudnorm=I=-14" in text
    assert text.endswith(",aresample=48000[voz]")


def test_the_filter_mixes_the_render_audio_when_it_exists() -> None:
    text = mix_filter([0, 2000], 8.2, video_audio=True)
    assert "[0:a]aformat=sample_rates=48000:channel_layouts=mono[v0a]" in text
    assert "[v0a][v0][v1]amix=inputs=3:normalize=0" in text
    assert "amix=inputs=2" in mix_filter([0, 2000], 8.2)


def test_the_filter_cuts_each_line_to_the_spoken_part() -> None:
    text = mix_filter([0, 2000], 8.2, trims=[(0.3, 2.7), (0.0, 1.2)])
    assert "[1:a]atrim=0.300:2.700,asetpts=PTS-STARTPTS,aformat=" in text
    assert "[2:a]atrim=0.000:1.200,asetpts=PTS-STARTPTS,aformat=" in text


def test_the_narration_is_read_with_neutral_delivery_by_default(tmp_path: Path) -> None:
    path = tmp_path / "narracao.pt.json"
    lines = [{"scene": "gancho", "text": " Oi. "}, {"scene": None, "text": "Fora."}]
    path.write_text(json.dumps({"language": "pt-BR", "lines": lines}))
    narration = load_narration(path)
    assert narration.language == "pt-BR"
    assert [(x.scene, x.text, x.delivery) for x in narration.lines] == [
        ("gancho", "Oi.", None),
        (None, "Fora.", None),
    ]
    path.write_text(json.dumps({"language": "pt-BR", "lines": []}))
    with pytest.raises(MotionInputError, match="lines"):
        load_narration(path)
    path.write_text(json.dumps({"lines": [{"text": "Oi."}]}))
    with pytest.raises(MotionInputError, match="language"):
        load_narration(path)


# --- uma pasta de produção pequena -------------------------------------------------------------------------


def write_wav(path: Path, seconds: float, rate: int = 24000, amplitude: int = 9000) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        samples = (
            int(amplitude * math.sin(2 * math.pi * 220 * i / rate)) for i in range(int(rate * seconds))
        )
        out.writeframes(b"".join(struct.pack("<h", s) for s in samples))


NARRATION = {
    "language": "pt-BR",
    "lines": [
        {"scene": "gancho", "text": "Uma lista ligada."},
        {"scene": None, "text": "Fora do JSON."},
        {"scene": "fecho", "text": "Até a próxima, pessoal."},
    ],
}
CONTENT = {
    "fps": 30,
    "scenes": [
        {"id": "gancho", "type": "title", "durationSec": 2.0},
        {"id": "fecho", "type": "title", "durationSec": 1.0},
    ],
}
SPEECH = {"gancho": 1.5, "fora-1": 0.8, "fecho": 1.4}  # a fala do fecho passa de 1 s: `tempos` estica


class Production:
    def __init__(self, root: Path) -> None:
        self.folder = root / "episodes" / "short-x"
        (self.folder / "voice").mkdir(parents=True)
        self.narration = self.folder / "narracao.json"
        self.narration.write_text(json.dumps(NARRATION), encoding="utf-8")
        self.content = self.folder / "content.json"
        self.content.write_text(json.dumps(CONTENT), encoding="utf-8")
        entries = []
        for line, (name, seconds) in zip(NARRATION["lines"], SPEECH.items(), strict=True):
            write_wav(
                self.folder / "voice" / f"{name}.wav", seconds, amplitude=2500 if name == "fecho" else 9000
            )
            entries.append(
                {
                    "scene": line["scene"],
                    "text": line["text"],
                    "delivery": "neutral",
                    "wav": f"voice/{name}.wav",
                    "seconds": seconds,
                    "speech": [0.1, seconds - 0.1],
                }
            )
        record = {"language": "pt-BR", "provider": "x", "lines": entries}
        (self.folder / "narracao.voz.json").write_text(json.dumps(record), encoding="utf-8")
        self.data = root / "data"
        self.context = SimpleNamespace(settings=SimpleNamespace(data_dir=self.data))

    def run(self, *argv: str) -> int:
        args = build_parser().parse_args(["short", *argv])
        return handled("vp short", lambda: HANDLERS["short"](args, self.context))  # type: ignore[arg-type]

    def silent_video(self, seconds: float = 3.0, sound: bool = False) -> Path:
        out = self.folder / ("com-som.mp4" if sound else "mudo.mp4")
        import subprocess

        audio = (
            ["-f", "lavfi", "-i", f"sine=frequency=330:duration={seconds}", "-c:a", "aac"] if sound else []
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s=64x64:d={seconds}:r=30",
                *audio,
                "-pix_fmt",
                "yuv420p",
                str(out),
            ],
            check=True,
        )
        return out


@pytest.fixture
def prod(tmp_path: Path) -> Production:
    return Production(tmp_path)


def args_for(prod: Production, *rest: str) -> list[str]:
    return [str(prod.folder), *rest]


# --- tempos ------------------------------------------------------------------------------------------------


def test_tempos_stretch_only_the_scenes_whose_speech_does_not_fit(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    assert prod.run("tempos", *args_for(prod, str(prod.content), str(prod.narration))) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("gancho") and "2.0 →  2.0 s" in out[0] and "←" not in out[0]
    assert out[1].startswith("fecho") and "1.0 →" in out[1] and out[1].endswith("←")
    fitted = json.loads((prod.folder / "content.voz.json").read_text(encoding="utf-8"))
    assert [s["durationSec"] for s in fitted["scenes"]] == [2.0, 1.5]
    assert out[-1] == "tempos: 3.5 s no JSON (3.0 s antes); escrito content.voz.json"
    assert json.loads(prod.content.read_text()) == CONTENT  # o original não muda


def test_tempos_without_the_voice_record_ask_for_voz(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    (prod.folder / "narracao.voz.json").unlink()
    assert prod.run("tempos", *args_for(prod, str(prod.content), str(prod.narration))) == 1
    assert "falta narracao.voz.json: rode `voz` antes" in capsys.readouterr().err


# --- juntar ------------------------------------------------------------------------------------------------


def fit(prod: Production) -> Path:
    assert prod.run("tempos", *args_for(prod, str(prod.content), str(prod.narration))) == 0
    return prod.folder / "content.voz.json"


def test_juntar_puts_each_line_at_the_start_of_its_scene_in_stereo_at_the_target(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    fitted = fit(prod)
    video, out = prod.silent_video(3.5), prod.folder / "out" / "final.mp4"
    capsys.readouterr()
    argv = ("juntar", *args_for(prod, str(video), str(fitted), str(prod.narration)), "--saida", str(out))
    assert prod.run(*argv) == 0
    line = capsys.readouterr().out.splitlines()[-1]
    assert line.startswith(f"juntar: {out} (3.5 s), 2 fala(s); volume ") and not line.startswith(
        "juntar: ... "
    )
    assert abs(integrated_lufs(out) - (-14.0)) < 1.5 and has_audio(out)
    assert not has_audio(video)  # o MP4 de entrada continua mudo
    assert abs(duration_ms(out) - 3500) < 100


def test_juntar_refuses_a_speech_that_does_not_fit_its_scene(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    video = prod.silent_video()
    argv = (
        "juntar",
        *args_for(prod, str(video), str(prod.content), str(prod.narration)),
        "--saida",
        str(prod.folder / "o.mp4"),
    )
    assert prod.run(*argv) == 1
    assert "a fala de fecho (1.20 s) passa do fim da cena: rode `tempos`" in capsys.readouterr().err
    assert not (prod.folder / "o.mp4").exists()


def test_juntar_refuses_a_speech_of_a_scene_that_is_not_in_the_json(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    other = {"fps": 30, "scenes": [CONTENT["scenes"][0]]}
    content = prod.folder / "so-gancho.json"
    content.write_text(json.dumps(other), encoding="utf-8")
    argv = (
        "juntar",
        *args_for(prod, str(prod.silent_video()), str(content), str(prod.narration)),
        "--saida",
        str(prod.folder / "o.mp4"),
    )
    assert prod.run(*argv) == 1
    assert "falas de cenas que não existem no JSON: fecho" in capsys.readouterr().err


def test_juntar_reports_a_failed_ffmpeg_as_a_project_error(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    fitted = fit(prod)
    broken = prod.folder / "quebrado.mp4"
    broken.write_bytes(b"nao e video")
    argv = (
        "juntar",
        *args_for(prod, str(broken), str(fitted), str(prod.narration)),
        "--saida",
        str(prod.folder / "o.mp4"),
    )
    assert prod.run(*argv) == 1
    assert "vp short:" in capsys.readouterr().err
    with pytest.raises(MixError, match="ffmpeg falhou na junção"):
        mix_audio(["ffmpeg", "-v", "error", "-i", str(broken), "-f", "null", "-"])


# --- sfx ---------------------------------------------------------------------------------------------------


def make_kit(prod: Production, covers_speech: bool = False) -> None:
    kit = prod.data / "sfx" / "kit"
    (kit / "sounds" / "pops").mkdir(parents=True)
    wav = kit / "sounds" / "pops" / "pop.wav"
    write_wav(wav, 0.4)
    record = {
        "id": "pop",
        "name": "pop",
        "category": "pops",
        "file": "sounds/pops/pop.wav",
        "description": "",
        "use_for": [],
        "avoid_for": ["On top of speech: masks the voice"] if covers_speech else [],
        "tags": [],
        "duration": 0.4,
        "channels": 1,
        "sync": {"at": 0.1, "meets": "instant", "how": ""},
        "timing": {"audible_start": 0, "onset": 0.05, "peak": 0.1, "body_end": 0.3, "audible_end": 0.4},
        "fits_seconds": None,
        "level": {"lufs": -20, "true_peak_dbtp": -3, "tier": "medium"},
        "under_voiceover_db": -2,
        "adapt": {"rate": [1, 1], "notes": ""},
        "sha256": hashlib.sha256(wav.read_bytes()).hexdigest(),
    }
    (kit / "sounds.json").write_text(json.dumps({"license": "CC0-1.0", "sounds": [record]}), encoding="utf-8")


def plan(prod: Production, *cues: dict) -> Path:
    path = prod.folder / "sfx.json"
    path.write_text(json.dumps({"cues": list(cues)}), encoding="utf-8")
    return path


def test_sfx_lists_where_each_sound_falls_and_changes_nothing(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    make_kit(prod)
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "pop", "scene": "fecho", "offset_s": 0.5})
    capsys.readouterr()
    before = sorted(p.name for p in prod.folder.rglob("*"))
    assert prod.run("sfx", *args_for(prod, str(fitted), str(prod.narration), str(sfx))) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("voz medida: ") and out[0].endswith("LUFS (o kit assume −16)")
    assert out[1].split()[0] == "2.50" and "pop" in out[1] and "começa em   2.40 s" in out[1]
    assert out[-1] == "sfx: 1 efeito(s), sem erro"
    assert sorted(p.name for p in prod.folder.rglob("*")) == before


def test_sfx_stops_at_the_plan_errors_and_prints_the_warnings_first(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    make_kit(prod)
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "nada", "scene": "fecho"}, {"sound": "pop", "scene": "sumiu"})
    capsys.readouterr()
    assert prod.run("sfx", *args_for(prod, str(fitted), str(prod.narration), str(sfx))) == 1
    err = capsys.readouterr().err
    assert "vp short: sfx: sfx.json, efeito 1 (nada em fecho): som fora do kit" in err
    assert "sfx: sfx.json, efeito 2 (pop em sumiu): a cena não existe no vídeo" in err


def test_sfx_without_the_kit_is_an_error(prod: Production, capsys: pytest.CaptureFixture[str]) -> None:
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "pop", "scene": "fecho"})
    capsys.readouterr()
    assert prod.run("sfx", *args_for(prod, str(fitted), str(prod.narration), str(sfx))) == 1
    assert "falta o SFX Kit" in capsys.readouterr().err


def test_juntar_with_sfx_mixes_the_effects_too(prod: Production, capsys: pytest.CaptureFixture[str]) -> None:
    make_kit(prod)
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "pop", "scene": "fecho", "offset_s": 0.5})
    out = prod.folder / "sfx.mp4"
    capsys.readouterr()
    argv = (
        "juntar",
        *args_for(prod, str(prod.silent_video(3.5)), str(fitted), str(prod.narration)),
        "--saida",
        str(out),
        "--sfx",
        str(sfx),
    )
    assert prod.run(*argv) == 0
    assert " + 1 efeito(s); volume " in capsys.readouterr().out.splitlines()[-1] and out.is_file()


# --- boca --------------------------------------------------------------------------------------------------


def test_boca_writes_the_beats_and_the_mouth_envelope_for_the_whole_video(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    fitted = fit(prod)
    manifest, text = prod.folder / "sprites.json", prod.folder / "texto.txt"
    manifest.write_text('{"skin": "dono"}', encoding="utf-8")
    text.write_text("linha um é\nlinha dois\n", encoding="utf-8")
    out = prod.folder / "out" / "boca.json"
    capsys.readouterr()
    argv = (
        "boca",
        *args_for(prod, str(fitted), str(prod.narration)),
        "--saida",
        str(out),
        "--manifesto",
        str(manifest),
        "--texto",
        str(text),
    )
    assert prod.run(*argv) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["fps"] == 30 and len(data["levels"]) == 60 + 45  # 2,0 s + 1,5 s em 30 fps
    assert [(b["id"], b["from"], b["duration"]) for b in data["beats"]] == [
        ("gancho", 0, 60),
        ("fecho", 60, 45),
    ]
    assert data["beats"][0]["speech"] == [0, round(1.4 * 30) - round(0.1 * 30)]
    assert data["manifest"] == {"skin": "dono"} and data["json"] == ["linha um é", "linha dois"]
    assert data["recordings"] == {} and any(level > 0 for level in data["levels"][:45])
    assert data["levels"][39:60] == [0.0] * 21  # depois da fala (39 quadros do gancho), a boca fecha
    assert all(level > 0 for level in data["levels"][61:94])  # a fala do fecho começa no começo da cena
    assert "linha um é" in out.read_text(encoding="utf-8")  # acentos legíveis
    last = capsys.readouterr().out.splitlines()[-1]
    spoken = sum(1 for level in data["levels"] if level > 0)
    assert last == f"boca: 2 batida(s), 105 frames, fala em {spoken} ({spoken / 30:.1f} s); escrito {out}"


def test_boca_without_manifest_or_text_has_only_the_timing(prod: Production) -> None:
    fitted = fit(prod)
    out = prod.folder / "boca.json"
    argv = ("boca", *args_for(prod, str(fitted), str(prod.narration)), "--saida", str(out))
    assert prod.run(*argv) == 0
    assert set(json.loads(out.read_text(encoding="utf-8"))) == {"fps", "beats", "levels", "recordings"}


def test_sfx_prints_the_warnings_and_still_succeeds(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    make_kit(prod, covers_speech=True)
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "pop", "scene": "gancho", "offset_s": 0.5})  # sobre a fala da cena
    capsys.readouterr()
    assert prod.run("sfx", *args_for(prod, str(fitted), str(prod.narration), str(sfx))) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("sfx: alerta: ") and "cobre a voz" in out[0]
    assert out[1].startswith("voz medida: ") and out[-1] == "sfx: 1 efeito(s), sem erro"
    assert out[2].endswith("dB sob a fala")


def test_sfx_reports_the_average_loudness_of_the_scene_speeches(
    prod: Production, capsys: pytest.CaptureFixture[str]
) -> None:
    make_kit(prod)
    fitted = fit(prod)
    sfx = plan(prod, {"sound": "pop", "scene": "fecho"})
    capsys.readouterr()
    assert prod.run("sfx", *args_for(prod, str(fitted), str(prod.narration), str(sfx))) == 0
    measured = [
        integrated_lufs(prod.folder / "voice" / f"{name}.wav") for name in ("gancho", "fecho")
    ]  # sem a fala "fora"
    assert abs(measured[0] - measured[1]) > 3  # as duas falas têm volumes diferentes
    expected = sum(measured) / 2
    assert f"voz medida: {expected:.1f} LUFS" in capsys.readouterr().out


def video_md5(path: Path) -> str:
    import subprocess

    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-c", "copy", "-f", "md5", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_juntar_copies_the_video_stream_untouched(prod: Production) -> None:
    fitted = fit(prod)
    video, out = prod.silent_video(3.5), prod.folder / "copia.mp4"
    argv = ("juntar", *args_for(prod, str(video), str(fitted), str(prod.narration)), "--saida", str(out))
    assert prod.run(*argv) == 0
    assert video_md5(out) == video_md5(video)


def test_the_join_command_lists_the_voices_in_scene_order_each_at_its_scene_start(prod: Production) -> None:
    from app.media.probe import duration_ms as measure
    from app.pipeline.motion_inputs import load_content
    from app.pipeline.short_join import join_command, ordered_speech
    from app.pipeline.short_timing import voiced

    content = load_content(fit(prod))
    wavs = voiced(prod.folder, prod.narration)
    ordered = ordered_speech(content, wavs)
    assert ordered == ["gancho", "fecho"]  # a fala sem cena não entra
    video = prod.silent_video(3.5)
    command = join_command(
        video, prod.folder / "o.mp4", content, wavs, ordered, [], measure(video) / 1000, False
    )
    inputs = [command[i + 1] for i, arg in enumerate(command) if arg == "-i"]
    assert inputs == [
        str(video),
        str(prod.folder / "voice" / "gancho.wav"),
        str(prod.folder / "voice" / "fecho.wav"),
    ]
    graph = command[command.index("-filter_complex") + 1]
    assert "adelay=0|0[v0]" in graph and "adelay=2000|2000[v1]" in graph
    assert "atrim=0.100:1.400" in graph  # o trecho falado do gancho
    assert command[-1] == str(prod.folder / "o.mp4") and "-shortest" in command
    assert command[command.index("-c:v") + 1] == "copy"


def test_boca_does_not_overflow_when_the_speech_passes_the_scene_of_a_content_not_fitted(
    prod: Production,
) -> None:
    out = prod.folder / "boca.json"
    argv = ("boca", *args_for(prod, str(prod.content), str(prod.narration)), "--saida", str(out))
    assert prod.run(*argv) == 0  # a fala do fecho (1,2 s) passa da cena de 1,0 s, a última do vídeo
    assert len(json.loads(out.read_text(encoding="utf-8"))["levels"]) == 90


def test_juntar_says_when_the_render_already_had_sound_and_when_the_volume_is_off_target(
    prod: Production, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fitted = fit(prod)
    video, out = prod.silent_video(3.5, sound=True), prod.folder / "som.mp4"
    capsys.readouterr()
    argv = ("juntar", *args_for(prod, str(video), str(fitted), str(prod.narration)), "--saida", str(out))
    assert prod.run(*argv) == 0
    line = capsys.readouterr().out.splitlines()[-1]
    assert ", 2 fala(s) + o áudio do render; volume " in line and line.endswith(" ok")
    monkeypatch.setattr("app.commands.short_juntar.loudness_problem", lambda lufs: "volume fora do alvo")
    assert prod.run(*argv) == 0
    assert capsys.readouterr().out.splitlines()[-1].endswith("— alerta: volume fora do alvo")


def test_the_join_command_adds_each_effect_as_an_input_and_in_the_mix(prod: Production) -> None:
    from app.media.probe import duration_ms as measure
    from app.pipeline.motion_inputs import load_content
    from app.pipeline.short_join import join_command, ordered_speech
    from app.pipeline.short_timing import resolve_effects, voiced

    make_kit(prod)
    content = load_content(fit(prod))
    wavs = voiced(prod.folder, prod.narration)
    sfx = plan(prod, {"sound": "pop", "scene": "fecho", "offset_s": 0.5})
    effects, _ = resolve_effects(prod.data, content, prod.narration, sfx, wavs, print)
    video = prod.silent_video(3.5)
    ordered = ordered_speech(content, wavs)
    command = join_command(
        video, prod.folder / "o.mp4", content, wavs, ordered, effects, measure(video) / 1000, False
    )
    inputs = [command[i + 1] for i, arg in enumerate(command) if arg == "-i"]
    assert len(inputs) == 4 and inputs[-1].endswith("pop.wav")
    graph = command[command.index("-filter_complex") + 1]
    assert (
        "[3:a]aformat=sample_rates=48000:channel_layouts=mono,volume=" in graph
        and "adelay=2400|2400[e0]" in graph
    )
    assert "[v0][v1][e0]amix=inputs=3:" in graph
