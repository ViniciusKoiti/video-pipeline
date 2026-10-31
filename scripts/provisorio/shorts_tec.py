"""Short de tecnologia com o vídeo por JSON do motion-kit e a voz clonada do dono (skill `shorts-tec`;
provisório até virar comando `vp`).

Uso: `.venv/bin/python scripts/provisorio/shorts_tec.py <verbo> ...`
- `voz <pasta> <narracao.json> [--voz=<nome>]`: uma fala por linha da narração, em
  `<pasta>/voice/<cena>-<provedor>-<hash>.wav`. A voz padrão é a do vídeo final (`tts_final`, a clonada do
  dono no Modal, ADR 024); `--voz=kokoro` para um rascunho local. O hash cobre o texto, o provedor, o modelo,
  a gravação de referência e a entrega: a fala só é gerada de novo quando um deles muda. Com um
  `<pasta>/voice/glossary.json` (§9, `app/media/pronunciation.py`), a voz lê a grafia do glossário ("JSON" →
  "jêison") e o hash cobre esse texto; a tela e a legenda ficam com a grafia da narração.
- `tempos <pasta> <content.json> <narracao.json>`: escreve `<content>.voz.json` com a duração de cada cena
  esticada até a fala dela caber (`max(duração do JSON, fala + folga)`), sem encurtar nenhuma, e, nas cenas
  com a janela do apresentador, `host.speaking` com o trecho da fala, para a boca parar quando a voz para.
- `juntar <pasta> <video.mp4> <content.voz.json> <narracao.json> --saida=<mp4> [--sfx=<sfx.json>]`: põe
  cada fala no começo da cena dela, sobre o MP4 silencioso do `motion-video render`, com o volume no alvo do
  projeto (−14 LUFS). Com `--sfx`, mistura também os efeitos do plano (ADR 035, `app/pipeline/sfx.py`): cada
  um no momento da cena menos o `sync.at` do kit, abaixado onde cai sobre a fala.
- `sfx <pasta> <content.voz.json> <narracao.json> <sfx.json>`: confere o plano de efeitos e lista onde cada
  som cai, sem misturar nada.
- `gate <mp4> <post.json> --episodio=<id>`: a pasta de gate do Short em `data/episodes/<id>/`
  (`renders/final.mp4` e `legenda-post.txt` com título e legenda do post), para o dono carimbar o gate 4 com
  `vp approve <id> --step preview` e o `vp postiz pacote --episode <id>` conferir a aprovação, como num
  episódio (CLAUDE.md §5). Um id por idioma (`-pt`, `-en`): cada MP4 tem o seu gate.
- `boca <pasta> <content.voz.json> <narracao.json> --saida=<json> [--manifesto=<sprites.json>]
  [--texto=<arquivo>]`: os dados de uma montagem em TSX com o kit: as batidas (cena, frame inicial, duração,
  trecho da fala), o envelope da boca por frame do vídeo inteiro (`app/media/envelope.py`, o mesmo do
  apresentador do auto-play), o manifesto da pele e, com `--texto`, as linhas de um arquivo para a tela.

`narracao.json`: `{"language": "pt-BR", "lines": [{"scene": "gancho", "text": "...", "delivery": "hook"},
...]}`. `scene` é o `id` de uma cena do JSON do motion-video; `null` marca uma fala de um plano fora do JSON
(gravação de tela, troca de estilos), gerada para a montagem final e ignorada por `tempos` e `juntar`.
`delivery` é a entrega da ADR 022 (`hook`, `turn`, `calm`, `invite`; sem ela, neutra).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media.loudness import TARGET_LUFS, integrated_lufs, loudness_problem  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.media.pronunciation import load_glossary, respell  # noqa: E402
from app.providers.errors import ProviderError  # noqa: E402
from app.providers.tts.base import SpeechRequest  # noqa: E402

PAD_SEC = 0.3  # folga depois da fala, antes do corte
HOST_HIDDEN_TYPES = ("hook", "end_card", "presenter")  # cenas sem a janela do apresentador (motion-video)
CLONED = ("chatterbox", "chatterbox_modal")
# A voz clonada devolve silêncio nas pontas do WAV (até 1 s antes da fala, em 2026-10-25): a fala é o trecho
# entre os silêncios das pontas, com uma respiração de cada lado.
NOISE_DB = -35
EDGE_SILENCE_S = 0.15
BREATH_S = 0.08


@dataclass(frozen=True)
class Line:
    scene: str | None
    text: str
    delivery: str = "neutral"

    @property
    def stem(self) -> str:
        return self.scene or "fora"


def load_lines(path: Path) -> tuple[str, list[Line]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        Line(item.get("scene"), item["text"].strip(), item.get("delivery") or "neutral")
        for item in data["lines"]
    ]
    if not lines:
        raise SystemExit(f"{path.name}: sem linhas de narração")
    return data.get("language", "pt-BR"), lines


def wav_name(
    line: Line,
    index: int,
    provider: str,
    fingerprint: str,
    language: str = "pt-BR",
    spoken: str | None = None,
) -> str:
    """O nome do WAV da fala: a cena (ou `fora-N`), o provedor, o idioma e o hash do que muda a fala. O idioma
    no nome separa as falas das duas línguas de uma mesma cena: sem ele, gerar uma apagava a outra. `spoken` é
    o texto que a voz lê (com o glossário); sem termo do glossário, é o da narração e o nome não muda."""
    delivery = f"|entrega:{line.delivery}" if provider in CLONED and line.delivery != "neutral" else ""
    key = hashlib.sha256(f"{fingerprint}{delivery}|{spoken or line.text}".encode()).hexdigest()[:10]
    stem = line.stem if line.scene else f"fora-{index}"
    return f"{stem}-{provider}-{language.lower().replace('-', '')}-{key}.wav"


def bounds_from_log(log: str, total: float, breath: float = BREATH_S) -> tuple[float, float]:
    """Onde a fala começa e termina, pelo `silencedetect` do ffmpeg: um silêncio que começa no zero adianta o
    começo; um que termina no fim do arquivo antecipa o fim. Sem silêncio nas pontas, o arquivo inteiro."""
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    begin, end = 0.0, total
    for s, e in zip(starts, ends, strict=False):
        if s <= 0.05:
            begin = max(0.0, e - breath)
        if e >= total - 0.05:
            end = min(total, s + breath)
    if len(starts) > len(ends) and starts[-1] > begin:  # silêncio aberto até o fim do arquivo
        end = min(total, starts[-1] + breath)
    return (begin, end) if end > begin else (0.0, total)


def speech_bounds(path: Path) -> tuple[float, float]:
    """A fala de um WAV, em segundos desde o início: `(começo, fim)`."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            f"silencedetect=noise={NOISE_DB}dB:d={EDGE_SILENCE_S}",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg não leu {path.name}: {result.stderr.strip()[-200:]}")
    return bounds_from_log(result.stderr, duration_ms(path) / 1000)


def fit_durations(
    content: dict[str, Any], seconds: dict[str, float], pad: float = PAD_SEC
) -> list[tuple[str, float, float]]:
    """Estica cada cena até a fala caber: `max(duração do JSON, fala + folga)`, no décimo de segundo acima.
    Cena sem fala fica como está. Devolve `(id, antes, depois)` e altera `content` no lugar."""
    rows = []
    windowed = content.get("host") is not None
    for scene in content["scenes"]:
        before = float(scene["durationSec"])
        after = before
        if scene["id"] in seconds:
            after = max(before, math.ceil((seconds[scene["id"]] + pad) * 10 - 1e-9) / 10)
            scene["durationSec"] = after
            # A fala entra no começo da cena (`juntar`): a boca da janela fala só nesse trecho.
            if windowed and scene.get("host") is not False and scene["type"] not in HOST_HIDDEN_TYPES:
                scene["host"] = {
                    **(scene.get("host") or {}),
                    "speaking": [0.0, round(seconds[scene["id"]], 2)],
                }
        rows.append((scene["id"], before, after))
    return rows


def scene_starts(content: dict[str, Any]) -> dict[str, float]:
    """O começo de cada cena em segundos, com a mesma conta do motion-video: frames inteiros por cena."""
    fps = int(content.get("fps", 30))
    starts, frame = {}, 0
    for scene in content["scenes"]:
        starts[scene["id"]] = frame / fps
        frame += round(float(scene["durationSec"]) * fps)
    return starts


def mix_filter(
    starts_ms: list[int],
    video_sec: float,
    target_lufs: float = TARGET_LUFS,
    trims: list[tuple[float, float]] | None = None,
    video_audio: bool = False,
    effects: list[tuple[int, float, float]] | None = None,
) -> str:
    """O filtro do ffmpeg: cada fala (entradas 1..N) cortada no trecho falado, reamostrada, atrasada até o
    começo da cena dela, somadas sem normalizar (com o áudio que o render já traz, se `video_audio`, e com os
    efeitos, entradas N+1.., cada um `(início em ms, corte do começo em s, ganho em dB)`), com silêncio até o
    fim do vídeo, o volume no alvo e 48 kHz (o loudnorm sobe a taxa de amostragem; sem o aresample o AAC sai
    em 96 kHz)."""
    parts = []
    if video_audio:
        parts.append("[0:a]aformat=sample_rates=48000:channel_layouts=mono[v0a]")
    for i, ms in enumerate(starts_ms):
        trim = f"atrim={trims[i][0]:.3f}:{trims[i][1]:.3f},asetpts=PTS-STARTPTS," if trims else ""
        parts.append(
            f"[{i + 1}:a]{trim}aformat=sample_rates=48000:channel_layouts=mono,adelay={ms}|{ms}[v{i}]"
        )
    for j, (ms, trim_s, gain_db) in enumerate(effects or []):
        trim = f"atrim=start={trim_s:.3f},asetpts=PTS-STARTPTS," if trim_s > 0 else ""
        parts.append(
            f"[{len(starts_ms) + 1 + j}:a]{trim}aformat=sample_rates=48000:channel_layouts=mono,"
            f"volume={gain_db:.1f}dB,adelay={ms}|{ms}[e{j}]"
        )
    inputs = (
        ("[v0a]" if video_audio else "")
        + "".join(f"[v{i}]" for i in range(len(starts_ms)))
        + "".join(f"[e{j}]" for j in range(len(effects or [])))
    )
    count = len(starts_ms) + (1 if video_audio else 0) + len(effects or [])
    parts.append(
        f"{inputs}amix=inputs={count}:normalize=0:dropout_transition=0,apad=whole_dur={video_sec:.3f},"
        f"loudnorm=I={target_lufs:.0f}:TP=-1.5:LRA=11,aresample=48000[voz]"
    )
    return ";".join(parts)


def cmd_voz(folder: Path, narration: Path, named: str | None) -> None:
    from app.bootstrap import build_context
    from scripts.provisorio.montar_episodio import voice_fingerprint

    context = build_context(ROOT)
    settings = context.settings
    language, lines = load_lines(narration)
    if named:
        provider, tts = named, context.tts_named(named)
    else:
        provider, tts = settings.providers.tts_final or settings.providers.tts, context.tts_final
    fingerprint = voice_fingerprint(settings, provider, language)
    voice_dir = folder / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    glossary = load_glossary(folder)
    started = time.monotonic()
    manifest = []
    try:
        for index, line in enumerate(lines):
            spoken = respell(line.text, glossary)
            wav = voice_dir / wav_name(line, index, provider, fingerprint, language, spoken)
            if not wav.exists():
                # Só as versões antigas desta fala, neste idioma: cena, provedor e idioma vêm antes do hash.
                for stale in voice_dir.glob(f"{wav.name.rsplit('-', 1)[0]}-*.wav"):
                    stale.unlink()
                try:
                    tts.synthesize_speech(
                        SpeechRequest(text=spoken, out_path=wav, language=language, delivery=line.delivery)
                    )
                except ProviderError as error:
                    raise SystemExit(
                        f"{wav.name}: {error.reason}: {error}. As falas já geradas ficam; rode de novo."
                    ) from error
            seconds = duration_ms(wav) / 1000
            begin, end = speech_bounds(wav)
            manifest.append(
                {
                    "scene": line.scene,
                    "text": line.text,
                    "delivery": line.delivery,
                    "wav": f"voice/{wav.name}",
                    "seconds": seconds,
                    "speech": [round(begin, 3), round(end, 3)],
                }
            )
            print(f"{line.stem:16s} {seconds:5.2f} s (fala {begin:.2f}–{end:.2f})  {wav.name}")
    finally:
        close = getattr(tts, "close", None)
        if close:
            close()
    out = folder / f"{narration.stem}.voz.json"
    out.write_text(
        json.dumps(
            {"language": language, "provider": provider, "lines": manifest}, ensure_ascii=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    total = sum(item["speech"][1] - item["speech"][0] for item in manifest)
    print(
        f"voz: {len(lines)} fala(s), {total:.1f} s de fala, {time.monotonic() - started:.0f} s; "
        f"registro em {out.name}"
    )


@dataclass(frozen=True)
class Speech:
    wav: Path
    begin: float
    end: float

    @property
    def seconds(self) -> float:
        return self.end - self.begin


def voiced(folder: Path, narration: Path) -> dict[str, Speech]:
    """As falas de cena (WAV e o trecho falado), pelo registro que `voz` escreveu."""
    record = folder / f"{narration.stem}.voz.json"
    if not record.is_file():
        raise SystemExit(f"falta {record.name}: rode `voz` antes")
    data = json.loads(record.read_text(encoding="utf-8"))
    return {
        item["scene"]: Speech(folder / item["wav"], *item["speech"])
        for item in data["lines"]
        if item["scene"]
    }


def cmd_tempos(folder: Path, content_file: Path, narration: Path) -> None:
    content = json.loads(content_file.read_text(encoding="utf-8"))
    wavs = voiced(folder, narration)
    ids = {scene["id"] for scene in content["scenes"]}
    unknown = sorted(set(wavs) - ids)
    if unknown:
        raise SystemExit(f"falas de cenas que não existem no JSON: {', '.join(unknown)}")
    seconds = {scene_id: speech.seconds for scene_id, speech in wavs.items()}
    rows = fit_durations(content, seconds)
    out = content_file.with_name(content_file.name.replace(".json", ".voz.json"))
    out.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for scene_id, before, after in rows:
        fala = f"fala {seconds[scene_id]:.2f} s" if scene_id in seconds else "sem fala"
        mark = " ←" if after != before else ""
        print(f"{scene_id:16s} {before:4.1f} → {after:4.1f} s  ({fala}){mark}")
    print(
        f"tempos: {sum(r[2] for r in rows):.1f} s no JSON ({sum(r[1] for r in rows):.1f} s antes); "
        f"escrito {out.name}"
    )


def sfx_placed(
    folder: Path, content: dict[str, Any], narration: Path, plan_file: Path, wavs: dict[str, Speech]
):
    """O plano de efeitos conferido e resolvido sobre as cenas e as falas; para no primeiro erro."""
    from app.bootstrap import build_context
    from app.pipeline import sfx as sfxmod

    kit = sfxmod.load_kit(build_context(ROOT).settings.data_dir)
    plan = sfxmod.SfxPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    _, lines = load_lines(narration)
    narrations = {line.scene: line.text for line in lines if line.scene}
    speeches = {scene_id: sfxmod.Speech(seconds=speech.seconds) for scene_id, speech in wavs.items()}
    starts = scene_starts(content)
    durations = {s["id"]: float(s["durationSec"]) for s in content["scenes"]}
    errors, warnings = sfxmod.plan_problems(plan, kit, starts, durations, narrations, speeches)
    for warning in warnings:
        print(f"sfx: alerta: {warning}")
    if errors:
        raise SystemExit("\n".join(f"sfx: {e}" for e in errors))
    assert kit is not None
    voice = [integrated_lufs(speech.wav) for speech in wavs.values()]
    voice_lufs = sum(voice) / len(voice) if voice else None
    placed = sfxmod.resolve_sfx(plan, kit, starts, narrations, speeches, voice_lufs)
    return placed, voice_lufs


def cmd_sfx(folder: Path, content_file: Path, narration: Path, plan_file: Path) -> None:
    content = json.loads(content_file.read_text(encoding="utf-8"))
    placed, voice_lufs = sfx_placed(folder, content, narration, plan_file, voiced(folder, narration))
    print(f"voz medida: {voice_lufs:.1f} LUFS (o kit assume −16)" if voice_lufs is not None else "sem voz")
    for p in placed:
        under = " sob a fala" if p.under_speech else ""
        print(f"  {p.moment_s:6.2f} s  {p.sound:32} começa em {p.start_s:6.2f} s  {p.gain_db:+.1f} dB{under}")
    print(f"sfx: {len(placed)} efeito(s), sem erro")


def cmd_juntar(
    folder: Path, video: Path, content_file: Path, narration: Path, out: Path, plan_file: Path | None = None
) -> None:
    content = json.loads(content_file.read_text(encoding="utf-8"))
    wavs = voiced(folder, narration)
    starts = scene_starts(content)
    missing = sorted(set(wavs) - set(starts))
    if missing:
        raise SystemExit(f"falas de cenas que não existem no JSON: {', '.join(missing)}")
    video_sec = duration_ms(video) / 1000
    ordered = [scene_id for scene_id in starts if scene_id in wavs]
    for scene_id in ordered:
        end = starts[scene_id] + wavs[scene_id].seconds
        limit = starts[scene_id] + float(
            next(s["durationSec"] for s in content["scenes"] if s["id"] == scene_id)
        )
        if end > limit + 0.05:
            raise SystemExit(
                f"a fala de {scene_id} ({end - starts[scene_id]:.2f} s) passa do fim da cena: "
                "rode `tempos` e renderize de novo"
            )
    starts_ms = [round(starts[scene_id] * 1000) for scene_id in ordered]
    effects = sfx_placed(folder, content, narration, plan_file, wavs)[0] if plan_file else []
    # Um render com som dentro (um vídeo tocando na montagem) entra na mistura; sem áudio, só as falas.
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    has_audio = "audio" in probe.stdout
    command = ["ffmpeg", "-y", "-v", "error", "-i", str(video)]
    for scene_id in ordered:
        command += ["-i", str(wavs[scene_id].wav)]
    for effect in effects:
        command += ["-i", str(effect.file)]
    command += [
        "-filter_complex",
        mix_filter(
            starts_ms,
            video_sec,
            trims=[(wavs[s].begin, wavs[s].end) for s in ordered],
            video_audio=has_audio,
            effects=[(round(e.start_s * 1000), e.trim_s, e.gain_db) for e in effects],
        ),
        "-map",
        "0:v:0",
        "-map",
        "[voz]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(out),
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    lufs = integrated_lufs(out)
    problem = loudness_problem(lufs)
    print(
        f"juntar: {out} ({duration_ms(out) / 1000:.1f} s), {len(ordered)} fala(s)"
        f"{' + o áudio do render' if has_audio else ''}"
        f"{f' + {len(effects)} efeito(s)' if effects else ''}; volume {lufs:.1f} LUFS",
        f"— alerta: {problem}" if problem else "ok",
    )


def cmd_boca(
    folder: Path, content_file: Path, narration: Path, out: Path, manifest: Path | None, text: Path | None
) -> None:
    from app.media.envelope import mouth_levels

    content = json.loads(content_file.read_text(encoding="utf-8"))
    fps = int(content.get("fps", 30))
    wavs = voiced(folder, narration)
    starts = scene_starts(content)
    total = sum(round(float(s["durationSec"]) * fps) for s in content["scenes"])
    levels = [0.0] * total
    beats = []
    for scene in content["scenes"]:
        start = round(starts[scene["id"]] * fps)
        duration = round(float(scene["durationSec"]) * fps)
        beat: dict[str, Any] = {"id": scene["id"], "from": start, "duration": duration}
        speech = wavs.get(scene["id"])
        if speech:
            begin, end = round(speech.begin * fps), round(speech.end * fps)
            whole = mouth_levels(speech.wav, fps, end)
            for i, level in enumerate(whole[begin:end]):
                if start + i < total:
                    levels[start + i] = level
            beat["speech"] = [0, end - begin]
        beats.append(beat)
    data: dict[str, Any] = {"fps": fps, "beats": beats, "levels": levels, "recordings": {}}
    if manifest:
        data["manifest"] = json.loads(manifest.read_text(encoding="utf-8"))
    if text:
        data["json"] = text.read_text(encoding="utf-8").splitlines()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    spoken = sum(1 for level in levels if level > 0)
    print(
        f"boca: {len(beats)} batida(s), {total} frames, fala em {spoken} ({spoken / fps:.1f} s); "
        f"escrito {out}"
    )


def cmd_gate(video: Path, post: Path, episode_id: str) -> None:
    import shutil

    from app.bootstrap import build_context

    settings = build_context(ROOT).settings
    folder = settings.data_dir / "episodes" / episode_id
    (folder / "renders").mkdir(parents=True, exist_ok=True)
    final = folder / "renders" / "final.mp4"
    shutil.copyfile(video, final)
    data = json.loads(post.read_text(encoding="utf-8"))
    entry = data["posts"][0]
    title = entry.get("settings", {}).get("title")
    caption = entry["value"][0]["content"]
    (folder / "legenda-post.txt").write_text(
        (f"{title}\n\n" if title else "") + caption + "\n", encoding="utf-8"
    )
    print(f"gate: {final} ({duration_ms(final) / 1000:.1f} s) e legenda-post.txt; carimbe com:")
    print(f'  vp approve {episode_id} --step preview --notes "assisti"')
    print(f"  vp postiz pacote {post} --episode {episode_id}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {
        a.split("=", 1)[0]: (a.split("=", 1)[1] if "=" in a else True)
        for a in sys.argv[1:]
        if a.startswith("--")
    }
    if not args:
        raise SystemExit(__doc__)
    verb, rest = args[0], args[1:]
    if verb == "voz" and len(rest) == 2:
        cmd_voz(
            Path(rest[0]), Path(rest[1]), flags.get("--voz") if isinstance(flags.get("--voz"), str) else None
        )
    elif verb == "tempos" and len(rest) == 3:
        cmd_tempos(Path(rest[0]), Path(rest[1]), Path(rest[2]))
    elif verb == "juntar" and len(rest) == 4 and isinstance(flags.get("--saida"), str):
        plan = flags.get("--sfx")
        cmd_juntar(
            Path(rest[0]), Path(rest[1]), Path(rest[2]), Path(rest[3]), Path(flags["--saida"]),
            Path(plan) if isinstance(plan, str) else None,
        )
    elif verb == "sfx" and len(rest) == 4:
        cmd_sfx(Path(rest[0]), Path(rest[1]), Path(rest[2]), Path(rest[3]))
    elif verb == "gate" and len(rest) == 2 and isinstance(flags.get("--episodio"), str):
        cmd_gate(Path(rest[0]), Path(rest[1]), flags["--episodio"])
    elif verb == "boca" and len(rest) == 3 and isinstance(flags.get("--saida"), str):
        manifest = flags.get("--manifesto")
        text = flags.get("--texto")
        cmd_boca(
            Path(rest[0]),
            Path(rest[1]),
            Path(rest[2]),
            Path(flags["--saida"]),
            Path(manifest) if isinstance(manifest, str) else None,
            Path(text) if isinstance(text, str) else None,
        )
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
