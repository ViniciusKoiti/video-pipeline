"""RF7: o `episode.json` nasce do roteiro e das falas: tempo em sequência, mídia achada, trilha resolvida."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.pipeline.episode_build import (
    EpisodeBuildError,
    build_episode,
    build_scenes,
    media_path,
    music_segments,
    with_music,
)
from app.pipeline.schemas import EpisodeFormat, MusicPlan, ScenesManifest
from tests.test_music import NARRATIONS, cue, episode, track

DURATIONS = {"S01": 4000, "S02": 5000, "S03": 3000}


def folder(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir(parents=True)
    (tmp_path / "assets" / "a.png").write_bytes(b"png")
    return tmp_path


def roteiro(**changes: object) -> ScenesManifest:
    rows = [
        {
            "id": f"S0{i}",
            "narration": text,
            "visual_need": "contextual_stock",
            "search_query": "x",
            "chosen_asset_id": "a",
            **changes,
        }
        for i, text in enumerate(NARRATIONS, start=1)
    ]
    return ScenesManifest.model_validate({"episode_id": "ep", "language": "pt-BR", "scenes": rows})


def wavs(tmp_path: Path) -> dict[str, Path]:
    return {key: tmp_path / f"voice/{key}-fake-x.wav" for key in DURATIONS}


def test_media_is_found_by_any_accepted_extension_and_a_missing_one_says_which(tmp_path: Path) -> None:
    where = folder(tmp_path)
    (where / "assets" / "v.webm").write_bytes(b"v")
    assert media_path(where, "a") == "assets/a.png" and media_path(where, "v") == "assets/v.webm"
    with pytest.raises(EpisodeBuildError, match="ativo z sem arquivo de mídia em assets/"):
        media_path(where, "z")


def test_scenes_follow_one_another_with_the_real_duration_and_keep_what_the_script_says(
    tmp_path: Path,
) -> None:
    where = folder(tmp_path)
    script = roteiro(delivery="turn", host_corner="top-left")
    built = build_scenes(script, wavs(where), where, None, lambda wav: DURATIONS[wav.name[:3]])
    assert [(s.id, s.start_ms, s.duration_ms) for s in built] == [
        ("S01", 0, 4000),
        ("S02", 4000, 5000),
        ("S03", 9000, 3000),
    ]
    assert built[0].audio == "voice/S01-fake-x.wav" and built[0].narration == NARRATIONS[0]
    assert built[0].delivery == "turn" and built[0].host_corner == "top-left"
    assert built[0].shots[0].media == "assets/a.png"  # a forma v1: um plano de foto com o ativo escolhido


def test_a_photo_without_a_chosen_asset_is_an_error_that_says_so(tmp_path: Path) -> None:
    where = folder(tmp_path)
    script = roteiro()
    script.scenes[1].chosen_asset_id = None
    with pytest.raises(EpisodeBuildError, match="plano photo sem asset_id: escolha o ativo no gate 3"):
        build_scenes(script, wavs(where), where, None, lambda wav: 1000)


def test_the_episode_is_a_draft_explainer_with_the_video_of_the_script_orientation(tmp_path: Path) -> None:
    where = folder(tmp_path)
    built = build_scenes(roteiro(), wavs(where), where, None, lambda wav: 1000)
    episode_json = build_episode(roteiro(), built)
    assert (episode_json.title, episode_json.format, episode_json.schema_version) == (
        "ep (rascunho)",
        EpisodeFormat.EXPLAINER,
        2,
    )
    assert episode_json.captions == "captions.srt" and episode_json.video.width == 1920
    vertical = ScenesManifest.model_validate({**roteiro().model_dump(), "orientation": "portrait"})
    assert build_episode(vertical, built).video.width == 1080


def plan_file(where: Path) -> None:
    plan = MusicPlan(episode_id="ep", cues=[cue(("S01", None), ("S02", None))])
    (where / "music.json").write_text(plan.model_dump_json())


def catalog_file(data_dir: Path) -> None:
    from app.pipeline.schemas import MusicCatalog

    (data_dir / "music").mkdir(parents=True)
    (data_dir / "music" / "catalog.json").write_text(MusicCatalog(tracks=[track()]).model_dump_json())


def test_without_a_music_plan_there_is_no_music_and_the_episode_is_the_same_object(tmp_path: Path) -> None:
    where = folder(tmp_path)
    base = episode()
    assert music_segments(tmp_path / "data", where, base) == []
    assert with_music(base, []) is base


def test_a_music_plan_needs_the_catalog_the_asset_and_the_audio_file(tmp_path: Path) -> None:
    where, data = folder(tmp_path / "ep"), tmp_path / "data"
    plan_file(where)
    with pytest.raises(EpisodeBuildError, match="music.json sem catálogo de faixas"):
        music_segments(data, where, episode())
    catalog_file(data)
    with pytest.raises(EpisodeBuildError, match="faixa ytal-noite sem ativo no episódio .vp music usar."):
        music_segments(data, where, episode())
    (where / "assets" / "ytal-noite.json").write_text("{}")
    with pytest.raises(EpisodeBuildError, match="faixa ytal-noite sem arquivo de áudio em assets/"):
        music_segments(data, where, episode())


def test_the_music_gets_its_time_from_the_scenes_and_goes_into_the_episode(tmp_path: Path) -> None:
    where, data = folder(tmp_path / "ep"), tmp_path / "data"
    plan_file(where)
    catalog_file(data)
    (where / "assets" / "ytal-noite.json").write_text("{}")
    (where / "assets" / "ytal-noite.mp3").write_bytes(b"mp3")
    tracks = music_segments(data, where, episode())
    assert [(t.asset_id, t.media, t.start_ms, t.end_ms) for t in tracks] == [
        ("ytal-noite", "assets/ytal-noite.mp3", 0, 9000)  # do começo de S01 ao fim de S02
    ]
    joined = with_music(episode(), tracks)
    assert [t.asset_id for t in joined.music] == ["ytal-noite"]
    assert [s.id for s in joined.scenes] == ["S01", "S02", "S03"]  # o resto do episódio não muda
