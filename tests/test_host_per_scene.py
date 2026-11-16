"""Apresentador por cena (ADR 056): contrato, `vp check`, cantos e props do motor. Sem Node."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.media.host import host_corners
from app.media.host_scenes import scene_corners
from app.pipeline.check import check_episode
from app.pipeline.episode_build import build_scenes
from app.pipeline.schemas import EpisodeManifest, EpisodeScene, HostSpec, ScenesManifest
from app.render.remotion import RemotionEngine
from tests.test_episode_build import DURATIONS, folder, roteiro, wavs
from tests.test_host import HOST, scene, write_wav
from tests.test_remotion_props import FIXTURE
from tests.test_research import EP, episode, facts_file, scenes
from tests.test_shots import v2_episode

OLD_EPISODE = json.loads((FIXTURE / "episode.json").read_text())


def episode_with(marks: list[bool | None], host: dict[str, Any] | None = None) -> EpisodeManifest:
    """Um episódio com uma cena por marca (cada uma de um plano `stamp`, que não bloqueia canto)."""
    built = []
    for i, mark in enumerate(marks, start=1):
        row = scene(f"S{i:02d}", [("stamp", None)]).model_dump()
        built.append({**row, "start_ms": (i - 1) * 1000, "host": mark})
    raw = {**v2_episode(), "scenes": built, "host": host}
    return EpisodeManifest.model_validate(raw)


# --- contrato -------------------------------------------------------------------------------------


def test_host_spec_shows_by_scene_mark_or_by_mode() -> None:
    everyone, marked = HostSpec.model_validate(HOST), HostSpec.model_validate({**HOST, "show": "marked"})
    assert [everyone.shows(m) for m in (None, True, False)] == [True, True, False]
    assert [marked.shows(m) for m in (None, True, False)] == [False, True, False]
    with pytest.raises(ValidationError):
        HostSpec.model_validate({**HOST, "show": "sometimes"})


def test_episode_json_without_the_new_fields_is_written_as_before() -> None:
    manifest = EpisodeManifest.model_validate(OLD_EPISODE)
    dumped = json.loads(manifest.model_dump_json())
    assert all(set(s) == set(EpisodeScene.model_fields) - {"host"} for s in dumped["scenes"])
    with_host = EpisodeManifest.model_validate({**v2_episode(), "host": HOST})
    assert "show" not in json.loads(with_host.model_dump_json())["host"]


def test_marks_are_written_when_set_and_survive_the_round_trip() -> None:
    manifest = episode_with([True, None, False], {**HOST, "show": "marked"})
    dumped = json.loads(manifest.model_dump_json())
    assert dumped["host"]["show"] == "marked"
    assert [s.get("host", "-") for s in dumped["scenes"]] == [True, "-", False]
    assert EpisodeManifest.model_validate_json(manifest.model_dump_json()) == manifest


def test_a_hidden_scene_has_no_corner() -> None:
    with pytest.raises(ValidationError, match="host_corner numa cena com o apresentador escondido"):
        corner = scene("S01", [("stamp", None)], corner="top-left").model_dump()
        EpisodeScene.model_validate({**corner, "host": False})
    raw = {"id": "S01", "narration": "n", "visual_need": "contextual_stock", "search_query": "q"}
    with pytest.raises(ValidationError, match="apresentador escondido"):
        ScenesManifest.model_validate(
            {"episode_id": "ep", "language": "pt-BR",
             "scenes": [{**raw, "host_corner": "top-left", "host": False}]}
        )


def test_episode_and_script_refuse_marks_without_a_host_or_without_a_scene_that_shows_it() -> None:
    with pytest.raises(ValidationError, match="host: true, mas o episódio não tem host"):
        episode_with([True, None], None)
    with pytest.raises(ValidationError, match="show=marked sem nenhuma cena com host: true"):
        episode_with([None, False], {**HOST, "show": "marked"})
    with pytest.raises(ValidationError, match="todas as cenas com host: false"):
        episode_with([False, False], HOST)
    assert episode_with([False, None], None).host is None  # false sem host não diz nada
    row = {"narration": "n", "visual_need": "contextual_stock", "search_query": "q"}
    rows = [{"id": "S01", **row, "host": True}, {"id": "S02", **row}]
    base = {"episode_id": "ep", "language": "pt-BR", "scenes": rows}
    with pytest.raises(ValidationError, match="S01: host: true, mas o episódio não tem host"):
        ScenesManifest.model_validate(base)
    assert ScenesManifest.model_validate({**base, "host": {**HOST, "show": "marked"}}).scenes[0].host is True
    with pytest.raises(ValidationError, match="show=marked sem nenhuma cena"):
        ScenesManifest.model_validate({**base, "scenes": [rows[1]], "host": {**HOST, "show": "marked"}})


def test_vp_check_reports_the_host_problems(tmp_path: Path) -> None:
    raw = scenes()
    raw["host"] = {**HOST, "show": "marked"}
    store = episode(tmp_path, facts=facts_file(), scenes_json=raw)
    report = check_episode(store, EP)
    assert any("show=marked sem nenhuma cena com host: true" in e for e in report.errors)
    raw["scenes"][0]["host"] = True
    fixed = episode(tmp_path / "ok", facts=facts_file(), scenes_json=raw)
    assert not any("host" in e for e in check_episode(fixed, EP).errors)


def test_the_script_mark_reaches_the_episode(tmp_path: Path) -> None:
    where = folder(tmp_path)
    marked = ScenesManifest.model_validate({
        **roteiro().model_dump(),
        "host": {**HOST, "show": "marked"},
        "scenes": [{**s.model_dump(), "host": s.id == "S02"} for s in roteiro().scenes],
    })
    built = build_scenes(marked, wavs(where), where, None, lambda wav: DURATIONS[wav.name[:3]])
    assert [s.host for s in built] == [False, True, False]
    plain = build_scenes(roteiro(), wavs(where), where, None, lambda wav: DURATIONS[wav.name[:3]])
    assert [s.host for s in plain] == [None, None, None]


# --- cantos ---------------------------------------------------------------------------------------


def test_corners_advance_clockwise_only_between_scenes_with_the_host() -> None:
    manifest = episode_with([True, None, True, True, None], {**HOST, "show": "marked"})
    assert scene_corners(manifest) == ["top-left", None, "top-right", "bottom-right", None]
    everyone = episode_with([None, None, None], HOST)
    assert scene_corners(everyone) == host_corners(everyone.scenes)  # sem marcas: a regra de sempre
    assert scene_corners(episode_with([None], None)) == [None]


def test_a_hidden_scene_does_not_reserve_a_corner() -> None:
    manifest = episode_with([None, False, None], HOST)
    assert scene_corners(manifest) == ["top-left", None, "top-right"]


# --- props do motor -------------------------------------------------------------------------------


def three_scene_folder(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    photo = FIXTURE / "assets" / "commons-lc-usz62-136192.jpg"
    (tmp_path / "assets" / "f.jpg").write_bytes(photo.read_bytes())
    write_wav(tmp_path / "voice" / "x.wav", 1.0)  # a fala que `scene()` aponta, para as três cenas
    return tmp_path


def props_for(manifest: EpisodeManifest, where: Path) -> list[dict[str, Any]]:
    return RemotionEngine().scene_props(manifest, where, preview=True)


def test_props_have_host_only_in_the_scenes_that_show_it(tmp_path: Path) -> None:
    where = three_scene_folder(tmp_path)
    manifest = episode_with([True, None, True], {**HOST, "show": "marked"})
    first, middle, last = props_for(manifest, where)
    assert "host" not in middle
    assert (first["host"]["corner"], first["host"]["fromCorner"]) == ("top-left", None)
    # volta depois de uma cena sem ele: entra, não vem arrastado do canto anterior
    assert (last["host"]["corner"], last["host"]["fromCorner"]) == ("top-right", None)


def test_consecutive_scenes_with_the_host_drag_from_the_previous_corner(tmp_path: Path) -> None:
    where = three_scene_folder(tmp_path)
    manifest = episode_with([None, True, True], {**HOST, "show": "marked"})
    _, second, third = props_for(manifest, where)
    assert second["host"]["fromCorner"] is None
    assert third["host"]["fromCorner"] == second["host"]["corner"] == "top-left"


def test_without_the_new_fields_the_props_are_the_same_as_before(tmp_path: Path) -> None:
    where = three_scene_folder(tmp_path)
    before = props_for(episode_with([None, None, None], HOST), where)
    explicit = props_for(episode_with([True, True, True], HOST), where)
    assert before == explicit  # `show: all` + toda cena marcada = o comportamento de sempre
    assert all("host" in p for p in before)
    assert [p["host"]["corner"] for p in before] == host_corners(episode_with([None] * 3, HOST).scenes)
    # o episódio antigo não ganha chave nenhuma: o mesmo JSON de props, byte a byte
    old = EpisodeManifest.model_validate(copy.deepcopy(OLD_EPISODE))
    again = EpisodeManifest.model_validate_json(old.model_dump_json())
    engine = RemotionEngine()
    old_props = engine.scene_props(old, FIXTURE, preview=False)
    assert json.dumps(old_props, sort_keys=True) == json.dumps(
        engine.scene_props(again, FIXTURE, preview=False), sort_keys=True
    )
    assert all("host" not in p for p in old_props)
