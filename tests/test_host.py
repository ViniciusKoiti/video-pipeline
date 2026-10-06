"""Apresentador em janela flutuante (ADR 013): contrato, cantos, envelope e props do motor. Sem Node."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.media.envelope import mouth_levels
from app.media.host import blocked_corners, host_corners
from app.pipeline.schemas import (
    EpisodeFormat,
    EpisodeManifest,
    EpisodeScene,
    EpisodeShot,
    HostSpec,
    VideoSpec,
)
from app.render.remotion import RemotionEngine
from tests.test_remotion_props import FIXTURE
from tests.test_shots import v2_episode

HOST = {"identity": {"hair": "variant07", "outfit": "variant10", "nose": "variant07"}, "width": 0.16}


def write_wav(path: Path, seconds: float, loud: bool = True, rate: int = 24_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        n = int(seconds * rate)
        amp = 12_000 if loud else 0
        out.writeframes(b"".join(struct.pack("<h", int(amp * math.sin(i / 7))) for i in range(n)))


CLAIM = [{"text": "t", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E1"]}]


def shot(kind: str, start: int, ms: int, source: str | None = None) -> EpisodeShot:
    specs: dict[str, dict[str, Any]] = {
        "photo": {"kind": "photo", "anchor": "a", "visual_need": "contextual_stock", "search_query": "q"},
        "broll": {"kind": "broll", "anchor": "a", "visual_need": "contextual_stock", "search_query": "q"},
        "number": {"kind": "number", "anchor": "a", "value": "5", "label": "x", "claims": CLAIM},
        "stamp": {"kind": "stamp", "anchor": "a", "date": "1918", "claims": CLAIM},
        "lower_third": {"kind": "lower_third", "anchor": "a", "name": "N", "role": "R", "claims": CLAIM},
        "compare": {
            "kind": "compare", "anchor": "a", "claims": CLAIM,
            "left": {"value": "1", "label": "a"}, "right": {"value": "2", "label": "b"},
        },
        "chart": {
            "kind": "chart", "anchor": "a", "title": "t", "claims": CLAIM,
            "points": [{"label": "a", "value": 1}, {"label": "b", "value": 2}],
        },
    }
    return EpisodeShot.model_validate({
        "start_ms": start, "duration_ms": ms, "spec": specs[kind], "source": source,
        "media": "assets/f.jpg" if kind in ("photo", "broll") else None,
    })


def scene(sid: str, kinds: list[tuple[str, str | None]], corner: str | None = None) -> EpisodeScene:
    shots = [shot(k, i * 1000, 1000, s) for i, (k, s) in enumerate(kinds)]
    return EpisodeScene.model_validate({
        "id": sid, "start_ms": 0, "duration_ms": 1000 * len(shots), "narration": "n", "audio": "voice/x.wav",
        "shots": [s.model_dump() for s in shots], "host_corner": corner,
    })


# --- contrato -------------------------------------------------------------------------------------


def test_host_only_in_the_explainer_format() -> None:
    assert EpisodeManifest.model_validate({**v2_episode(), "host": HOST}).host is not None
    with pytest.raises(ValidationError, match="só existe no formato explainer"):
        EpisodeManifest.model_validate(
            {**v2_episode(), "host": HOST, "format": EpisodeFormat.ARCHIVAL_DOCUMENTARY.value}
        )


def test_host_spec_is_strict() -> None:
    assert HostSpec.model_validate(HOST).identity.eyes == "variant05"
    for bad in ({"hair": "longo", "outfit": "variant10"}, {"hair": "variant07", "outfit": "variant1"}):
        with pytest.raises(ValidationError):
            HostSpec.model_validate({"identity": bad})
    with pytest.raises(ValidationError):
        HostSpec.model_validate({**HOST, "width": 0.9})
    with pytest.raises(ValidationError):
        HostSpec.model_validate({**HOST, "extra": 1})
    with pytest.raises(ValidationError, match="Input should be"):
        scene("S01", [("photo", None)], corner="middle")


# --- cantos ---------------------------------------------------------------------------------------


def test_what_the_template_occupies_blocks_corners() -> None:
    fonte = "Fonte: x"
    assert blocked_corners(scene("S01", [("number", fonte)])) == {"top-right"}  # tela cheia: fonte em cima
    over_photo = scene("S01", [("photo", None), ("number", fonte)])
    assert blocked_corners(over_photo) == {"bottom-left", "bottom-right"}
    assert blocked_corners(scene("S01", [("lower_third", None)])) == {"bottom-left"}
    assert blocked_corners(scene("S01", [("chart", fonte)])) == {"top-left", "top-right"}
    assert blocked_corners(scene("S01", [("compare", None)])) == {"bottom-left", "bottom-right"}
    assert blocked_corners(scene("S01", [("photo", None)])) == set()


def test_corners_rotate_clockwise_and_avoid_blocked_ones() -> None:
    free = [scene(f"S0{i}", [("stamp", None)]) for i in range(1, 6)]
    assert host_corners(free) == ["top-left", "top-right", "bottom-right", "bottom-left", "top-left"]
    # só o canto de cima à esquerda está livre: a janela fica onde estava em vez de ir para um ocupado
    crowded = scene("S02", [("compare", "Fonte: x")])
    assert host_corners([free[0], crowded]) == ["top-left", "top-left"]


def test_scene_override_wins_and_sets_the_next_start() -> None:
    scenes = [scene("S01", [("stamp", None)], corner="bottom-left"), scene("S02", [("stamp", None)])]
    assert host_corners(scenes) == ["bottom-left", "top-left"]


# --- envelope -------------------------------------------------------------------------------------


def test_mouth_levels_follow_the_speech(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    write_wav(wav, 1.0)
    levels = mouth_levels(wav, 30, 30)
    assert len(levels) == 30 and max(levels) == 1.0 and min(levels) > 0.9  # tom constante
    assert len(mouth_levels(wav, 30, 40)) == 40 and mouth_levels(wav, 30, 40)[-1] == 0.0  # completa com 0
    assert len(mouth_levels(wav, 30, 10)) == 10  # corta
    silent = tmp_path / "s.wav"
    write_wav(silent, 1.0, loud=False)
    assert mouth_levels(silent, 30, 30) == [0.0] * 30


def test_mouth_levels_refuse_non_16_bit_wav(tmp_path: Path) -> None:
    wav = tmp_path / "b.wav"
    with wave.open(str(wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(1)
        out.setframerate(8_000)
        out.writeframes(b"\x80" * 800)
    with pytest.raises(ValueError, match="16 bits"):
        mouth_levels(wav, 30, 3)


# --- props do motor -------------------------------------------------------------------------------


def test_scene_props_carry_the_host_only_when_the_episode_has_one(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    photo = FIXTURE / "assets" / "commons-lc-usz62-136192.jpg"
    (tmp_path / "assets" / "f.jpg").write_bytes(photo.read_bytes())
    write_wav(tmp_path / "voice" / "S01.wav", 9.0)
    plain = EpisodeManifest.model_validate(v2_episode())
    (without,) = RemotionEngine().scene_props(plain, tmp_path, preview=True)
    assert "host" not in without  # sem apresentador as props (e o cache) não mudam

    with_host = EpisodeManifest.model_validate({**v2_episode(), "host": HOST})
    (props,) = RemotionEngine().scene_props(with_host, tmp_path, preview=True)
    host = props["host"]
    assert host["identity"] == {
        "skin": "notionists", "hair": "variant07", "outfit": "variant10", "eyes": "variant05",
        "extras": {"nose": "variant07"},
    }
    assert (host["width"], host["fromCorner"]) == (0.16, None)
    assert host["corner"] in {"top-left", "top-right", "bottom-left", "bottom-right"}
    assert len(host["levels"]) == props["frames"] and max(host["levels"]) <= 1.0
    assert {k: v for k, v in props.items() if k != "host"} == without


# --- perfil vertical (ADR 014) --------------------------------------------------------------------

PORTRAIT_VIDEO = {"width": 1080, "height": 1920}


def portrait_episode(**changes: Any) -> dict[str, Any]:
    """O episódio de teste v2 sem o plano `quote` (não cabe em retrato), em 1080×1920."""
    raw = v2_episode()
    raw["scenes"][0]["shots"][1]["spec"] = {
        "kind": "number", "anchor": "um banco falido", "value": "5", "label": "x", "claims": CLAIM,
    }
    return {**raw, "video": PORTRAIT_VIDEO, **changes}


def test_portrait_video_only_in_the_explainer_with_portrait_shots() -> None:
    ok = EpisodeManifest.model_validate(portrait_episode())
    assert ok.video.portrait and VideoSpec.for_orientation("portrait") == ok.video
    assert VideoSpec.for_orientation("landscape") == VideoSpec()
    with pytest.raises(ValidationError, match="só existe no formato explainer"):
        EpisodeManifest.model_validate(portrait_episode(format=EpisodeFormat.ARCHIVAL_DOCUMENTARY.value))
    raw = portrait_episode()
    raw["scenes"][0]["shots"][0]["spec"] = {
        "kind": "map", "anchor": "a", "places": [{"name": "X", "lat": 0, "lon": 0}], "claims": CLAIM,
    }
    with pytest.raises(ValidationError, match="S01: plano map não cabe em retrato"):
        EpisodeManifest.model_validate(raw)


def scenes_json(orientation: str, kind: str) -> dict[str, Any]:
    shots = {
        "number": {"kind": "number", "anchor": "cinco", "value": "5", "label": "x", "claims": CLAIM},
        "network": {
            "kind": "network", "anchor": "cinco", "root": "a", "claims": CLAIM,
            "nodes": [
                {"id": "a", "label": "A", "kind": "company"},
                {"id": "b", "label": "B", "kind": "bank"},
            ],
            "edges": [{"from": "a", "to": "b", "claims": CLAIM}],
            "steps": [{"anchor": "cinco", "nodes": ["b"]}],
        },
    }
    return {
        "episode_id": "t", "language": "pt-BR", "orientation": orientation,
        "scenes": [{"id": "S01", "narration": "Foram cinco mil.", "shots": [shots[kind]]}],
    }


def test_scenes_manifest_checks_portrait_shots() -> None:
    from app.pipeline.schemas import ScenesManifest

    assert ScenesManifest.model_validate(scenes_json("portrait", "number")).orientation == "portrait"
    assert ScenesManifest.model_validate(scenes_json("landscape", "network"))  # em paisagem a rede vale
    with pytest.raises(ValidationError, match="plano network não cabe em retrato"):
        ScenesManifest.model_validate(scenes_json("portrait", "network"))


def test_preview_and_host_width_follow_the_orientation() -> None:
    from app.render.base import target_spec

    land = EpisodeManifest.model_validate(v2_episode())
    port = EpisodeManifest.model_validate(portrait_episode(host=HOST))
    assert (target_spec(land, preview=True).width, target_spec(land, preview=True).height) == (1280, 720)
    assert (target_spec(port, preview=True).width, target_spec(port, preview=True).height) == (720, 1280)
    assert target_spec(port, preview=False).height == 1920
    spec = HostSpec.model_validate({"identity": HOST["identity"]})
    assert (spec.width_for(portrait=False), spec.width_for(portrait=True)) == (0.16, 0.28)
    assert HostSpec.model_validate(HOST).width_for(portrait=True) == 0.16  # a largura dada vale nos dois


def test_portrait_burns_captions_in_the_final_and_widens_the_window(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    photo = FIXTURE / "assets" / "commons-lc-usz62-136192.jpg"
    (tmp_path / "assets" / "f.jpg").write_bytes(photo.read_bytes())
    write_wav(tmp_path / "voice" / "S01.wav", 9.0)
    (tmp_path / "captions.srt").write_text("1\n00:00:00,500 --> 00:00:02,000\nlegenda\n")
    extra = {"host": {"identity": HOST["identity"]}, "captions": "captions.srt"}
    (land,) = RemotionEngine().scene_props(
        EpisodeManifest.model_validate({**v2_episode(), **extra}), tmp_path, preview=False
    )
    (port,) = RemotionEngine().scene_props(
        EpisodeManifest.model_validate(portrait_episode(**extra)), tmp_path, preview=False
    )
    assert land["cues"] == [] and land["host"]["width"] == 0.16
    assert [c["text"] for c in port["cues"]] == ["legenda"] and port["host"]["width"] == 0.28
    assert (port["width"], port["height"]) == (1080, 1920)


def test_portrait_corner_table_follows_the_vertical_layout() -> None:
    fonte = "Fonte: x"
    # só os cantos de cima são livres (a faixa de baixo é a base segura); a fonte fica acima da janela
    over_photo = scene("S01", [("photo", None), ("number", fonte)])
    assert blocked_corners(over_photo, portrait=True) == {"bottom-left", "bottom-right"}
    assert blocked_corners(over_photo) == {"bottom-left", "bottom-right"}
    compare = scene("S01", [("compare", None)])
    assert blocked_corners(compare, portrait=True) == {"top-right", "bottom-left", "bottom-right"}
    # o gráfico ocupa o topo; o selo no canto toma o de cima à esquerda
    # o gráfico fica alinhado ao topo: numa cena só de gráficos os cantos de baixo ficam livres
    assert blocked_corners(scene("S01", [("chart", None)]), portrait=True) == {"top-left", "top-right"}
    mixed = scene("S01", [("chart", None), ("number", None)])
    assert blocked_corners(mixed, portrait=True) == {"top-left", "top-right", "bottom-left", "bottom-right"}
    over_stamp = scene("S01", [("photo", None), ("stamp", None)])
    assert blocked_corners(over_stamp, portrait=True) == {"top-left", "bottom-left", "bottom-right"}
    scenes = [scene(f"S0{i}", [("stamp", fonte)]) for i in range(1, 5)]
    assert host_corners(scenes, portrait=True) == ["top-left", "top-right", "top-left", "top-right"]
