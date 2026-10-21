"""Trilha sonora (ADR 030): catálogo, plano do diretor musical, tempo pelos WAVs, mistura e loudness."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.media.loudness import TARGET_LUFS, integrated_lufs, intensity, loudness_problem
from app.media.probe import duration_ms, probe_streams
from app.pipeline.check import check_episode
from app.pipeline.music import load_music_catalog, plan_problems, resolve_music
from app.pipeline.schemas import (
    AUDIO_LIBRARY_LICENSE,
    Asset,
    EpisodeFormat,
    EpisodeManifest,
    EpisodeMusic,
    EpisodeScene,
    MusicCatalog,
    MusicCue,
    MusicPlan,
    MusicTrack,
    Provider,
    ScenesManifest,
    Status,
    VideoSpec,
)
from app.render.ffmpeg import assemble
from app.storage.json_files import JsonFileStore

V1 = {"visual_need": "contextual_stock", "search_query": "papel"}
NARRATIONS = [
    "Quando eu vi a série pela primeira vez, eu torci pelo vilão.",
    "Mas no último episódio ele perde. E quem conta a história é quem ganhou.",
    "Pra mim, a história é contada pelos vencedores.",
]


def track(asset_id: str = "ytal-noite", **changes: Any) -> MusicTrack:
    data = {"asset_id": asset_id, "title": "Noite", "file": f"{asset_id}.mp3", "duration_ms": 120_000,
            "moods": ["dark"], "intensity": 2, "vocals": False, **changes}
    return MusicTrack.model_validate(data)


def cue(start: tuple[str, str | None], end: tuple[str, str | None], **changes: Any) -> MusicCue:
    data = {"role": "bed", "track": "ytal-noite", "why": "clima da abertura",
            "start": {"scene": start[0], "text": start[1]}, "end": {"scene": end[0], "text": end[1]},
            **changes}
    return MusicCue.model_validate(data)


def scenes() -> ScenesManifest:
    rows = [{"id": f"S{i:02d}", "narration": text, **V1} for i, text in enumerate(NARRATIONS, start=1)]
    return ScenesManifest.model_validate({"episode_id": "ep", "language": "pt-BR", "scenes": rows})


def episode(durations: tuple[int, ...] = (4000, 5000, 3000), music: list[EpisodeMusic] | None = None,
            fmt: EpisodeFormat = EpisodeFormat.EXPLAINER) -> EpisodeManifest:
    rows, cursor = [], 0
    for i, (text, ms) in enumerate(zip(NARRATIONS, durations, strict=True), start=1):
        rows.append(EpisodeScene(id=f"S{i:02d}", start_ms=cursor, duration_ms=ms, narration=text,
                                 audio=f"voice/S{i:02d}.wav", asset_id="a", image="assets/a.png"))
        cursor += ms
    return EpisodeManifest(episode_id="ep", title="Ep", language="pt-BR", format=fmt, scenes=rows,
                           music=music or [])


def bed(start_ms: int, end_ms: int, **changes: Any) -> EpisodeMusic:
    data = {"asset_id": "ytal-noite", "media": "assets/ytal-noite.mp3", "role": "bed", "start_ms": start_ms,
            "end_ms": end_ms, "gain_db": -24.0, **changes}
    return EpisodeMusic.model_validate(data)


# --- licença e catálogo -------------------------------------------------------------------------


def library_asset(**changes: Any) -> dict[str, Any]:
    return {"id": "ytal-noite", "provider": "youtube_audio_library", "provider_id": "Noite",
            "page_url": "https://www.youtube.com/audiolibrary", "license_id": AUDIO_LIBRARY_LICENSE,
            "usage_notes": "Só YouTube; sem voz cantada.", "retrieved_at": datetime.now(UTC).isoformat(),
            "sha256": "a" * 64, "review_status": Status.APPROVED, **changes}


def test_audio_library_track_is_approved_with_its_own_license() -> None:
    assert Asset.model_validate(library_asset()).provider is Provider.YOUTUBE_AUDIO_LIBRARY


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"provider": "pexels", "author": "x", "attribution_text": "x"}, "Audio Library só com provider"),
        ({"license_id": "Pexels"}, "YouTube-Audio-Library ou a CC-BY"),
        ({"usage_notes": ""}, "exige usage_notes"),
    ],
)
def test_audio_library_license_stays_with_the_library(changes: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Asset.model_validate(library_asset(**changes))


def test_catalog_ids_are_unique_and_load_from_data_dir(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="faixas do catálogo"):
        MusicCatalog(tracks=[track(), track()])
    assert load_music_catalog(tmp_path) is None
    (tmp_path / "music").mkdir()
    (tmp_path / "music" / "catalog.json").write_text(MusicCatalog(tracks=[track()]).model_dump_json())
    catalog = load_music_catalog(tmp_path)
    assert catalog is not None and list(catalog.by_id()) == ["ytal-noite"]


def test_silence_has_no_track_and_bed_needs_one() -> None:
    with pytest.raises(ValidationError, match="silêncio não tem faixa"):
        cue(("S01", None), ("S01", None), role="silence")
    with pytest.raises(ValidationError, match="silêncio não tem faixa"):
        cue(("S01", None), ("S01", None), track=None)


def test_intensity_steps_and_loudness_alert() -> None:
    assert [intensity(v) for v in (-40, -27, -20, -16, -10)] == [1, 2, 3, 4, 5]
    assert loudness_problem(TARGET_LUFS - 1) is None
    assert "alvo" in (loudness_problem(-20.0) or "")


# --- plano (vp check) ---------------------------------------------------------------------------


def problems(*cues: MusicCue, catalog: MusicCatalog | None = None, minutes: float = 1.0) -> list[str]:
    plan = MusicPlan(episode_id="ep", cues=list(cues))
    errors, _ = plan_problems(plan, scenes().scenes, catalog or MusicCatalog(tracks=[track()]), minutes)
    return errors


def test_a_good_plan_has_no_problems() -> None:
    assert problems(cue(("S01", None), ("S02", "E quem conta"))) == []


def test_anchor_must_exist_and_end_after_start() -> None:
    assert "não aparece na narração de S01" in problems(cue(("S01", "dragão"), ("S02", None)))[0]
    assert "cena S09 não existe" in problems(cue(("S09", None), ("S02", None)))[0]
    assert "saída vem antes" in problems(cue(("S02", None), ("S01", None)))[0]


def test_track_must_be_in_the_catalog_and_without_singing() -> None:
    assert "fora do catálogo" in problems(cue(("S01", None), ("S02", None), track="ytal-outra"))[0]
    singing = MusicCatalog(tracks=[track(vocals=True)])
    assert "voz cantada" in problems(cue(("S01", None), ("S02", None)), catalog=singing)[0]


def test_beds_do_not_overlap_nor_play_inside_a_silence() -> None:
    first, second = cue(("S01", None), ("S02", "E quem conta")), cue(("S02", "Mas no último"), ("S03", None))
    assert "fundos sobrepostos" in problems(first, second, minutes=3)[0]
    quiet = cue(("S03", None), ("S03", None), role="silence", track=None)
    assert "dentro de um silêncio" in problems(cue(("S01", None), ("S03", "contada")), quiet)[0]


def test_bed_changes_only_at_the_turns() -> None:
    beds = [cue((f"S0{i}", None), (f"S0{i}", None)) for i in (1, 2, 3)]
    assert "troca de faixa só nas viradas" in problems(*beds, minutes=1)[0]
    assert problems(*beds, minutes=2) == []


def test_vp_check_reads_music_json_with_the_catalog(tmp_path: Path) -> None:
    folder = tmp_path / "ep"
    folder.mkdir()
    (folder / "scenes.json").write_text(scenes().model_dump_json())
    plan = MusicPlan(episode_id="ep", cues=[cue(("S01", None), ("S03", None))])
    (folder / "music.json").write_text(plan.model_dump_json())
    store = JsonFileStore(tmp_path)
    report = check_episode(store, "ep", music_catalog=MusicCatalog(tracks=[track()]))
    assert "trilha: 1 entrada(s), 1 faixa(s)" in report.checked
    assert any("ainda sem cópia no episódio" in w for w in report.warnings)
    assert any("sem catálogo" in e for e in check_episode(store, "ep").errors)


# --- tempo e contrato ---------------------------------------------------------------------------


def test_cues_get_their_time_from_the_real_wavs() -> None:
    plan = MusicPlan(episode_id="ep", cues=[
        cue(("S01", None), ("S02", "E quem conta"), fade_in_ms=1000, fade_out_ms=1000),
        cue(("S03", None), ("S03", None), role="silence", track=None),
    ])
    (resolved,) = resolve_music(plan, episode(), MusicCatalog(tracks=[track()]), lambda a: f"assets/{a}.mp3")
    spoken = NARRATIONS[1]
    expected_end = 4000 + round(spoken.find("E quem conta") / len(spoken) * 5000)
    assert (resolved.start_ms, resolved.end_ms) == (0, expected_end)
    assert resolved.gain_db == -24.0 and not resolved.loop
    assert resolved.media == "assets/ytal-noite.mp3"


def test_short_track_loops_and_short_cue_scales_the_fades() -> None:
    plan = MusicPlan(episode_id="ep", cues=[cue(("S01", None), ("S01", None), fade_in_ms=3000,
                                                fade_out_ms=3000, level="mid")])
    catalog = MusicCatalog(tracks=[track(duration_ms=2000)])
    (resolved,) = resolve_music(plan, episode(), catalog, lambda a: f"assets/{a}.mp3")
    assert resolved.loop and resolved.gain_db == -18.0
    assert resolved.fade_in_ms + resolved.fade_out_ms <= 4000


def test_episode_music_rules() -> None:
    assert episode(music=[bed(0, 3000), bed(3000, 9000)]).music
    with pytest.raises(ValidationError, match="fundos sobrepostos"):
        episode(music=[bed(0, 5000), bed(4000, 9000)])
    with pytest.raises(ValidationError, match="só existe no formato explainer"):
        episode(music=[bed(0, 3000)], fmt=EpisodeFormat.ARCHIVAL_DOCUMENTARY)
    with pytest.raises(ValidationError, match="depois do fim do vídeo"):
        episode(music=[bed(0, 13_000)])
    with pytest.raises(ValidationError):
        bed(0, 3000, gain_db=-3.0)  # a voz fica sempre acima da trilha


# --- mistura (ffmpeg real) ----------------------------------------------------------------------


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def test_assemble_mixes_the_bed_under_the_voice_at_the_target_loudness(tmp_path: Path) -> None:
    root = tmp_path / "ep"
    (root / "voice").mkdir(parents=True)
    (root / "assets").mkdir()
    ms = (1500, 1500, 1000)
    for i, length in enumerate(ms, start=1):  # voz: tom a −30 dBFS, bem abaixo do alvo
        ffmpeg("-f", "lavfi", "-i", f"sine=frequency=220:duration={length / 1000}", "-af", "volume=-30dB",
               "-ar", "24000", "-ac", "1", str(root / "voice" / f"S{i:02d}.wav"))
    ffmpeg("-f", "lavfi", "-i", "sine=frequency=660:duration=1", str(root / "assets" / "ytal-noite.mp3"))
    segments = []
    for i, length in enumerate(ms, start=1):
        segment = tmp_path / f"S{i:02d}.mp4"
        ffmpeg("-f", "lavfi", "-i", f"color=c=black:s=320x180:r=10:d={length / 1000}", "-c:v", "libx264",
               "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(segment))
        segments.append(segment)
    music = [bed(0, 3500, fade_in_ms=500, fade_out_ms=500, loop=True)]  # a faixa de 1 s recomeça
    manifest = episode(ms, music=music)
    out = tmp_path / "out" / "final.mp4"
    out.parent.mkdir()
    assemble(manifest, root, segments, VideoSpec(width=320, height=180, fps=10), out)
    audio = next(s for s in probe_streams(out) if s["codec_type"] == "audio")
    assert (audio["codec_name"], audio["channels"]) == ("aac", 2)
    assert abs(duration_ms(out) - 4000) <= 150
    assert abs(integrated_lufs(out) - TARGET_LUFS) <= 2.0
    assert not list(out.parent.glob(".*.txt"))  # as listas do concat foram apagadas


def test_episode_json_without_music_keeps_its_shape() -> None:
    dumped = json.loads(episode().model_dump_json())
    assert dumped["music"] == []
