"""Lista de planos por cena (ADR 008): contrato, tempo, ritmo e integrações."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from app.pipeline.format_decision import decide_from_scenes
from app.pipeline.schemas import (
    Asset,
    EpisodeFormat,
    EpisodeManifest,
    Provider,
    Scene,
    ScenesManifest,
    Shot,
    SourcesManifest,
    effective_shots,
    unknown_source_refs,
    visual_need_violations,
)
from app.pipeline.shots import episode_shots, pacing_warnings, shot_bounds
from app.providers.errors import ModelUnavailable
from app.providers.tts.base import SpeechRequest
from app.providers.tts.kokoro import KokoroTTS
from app.render.ffmpeg import RenderError, scene_image

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"
SHOT = TypeAdapter(Shot)
CLAIM = {"text": "fato de teste", "source_ids": ["source-01"]}
NARRATION = (
    "Em 1918, um banco falido foi vendido. Junto veio uma fábrica de tecidos. "
    "Sete anos depois, chegou o genro."
)


def photo(anchor: str, **extra: Any) -> dict[str, Any]:
    return {
        "kind": "photo",
        "anchor": anchor,
        "visual_need": "historical_exact",
        "search_query": "fábrica",
        **extra,
    }


def scene(shots: list[dict[str, Any]], narration: str = NARRATION) -> Scene:
    return Scene.model_validate({"id": "S01", "narration": narration, "shots": shots})


def v2_shots() -> list[dict[str, Any]]:
    return [
        {"kind": "stamp", "anchor": "Em 1918", "date": "1918", "place": "Sorocaba", "claims": [CLAIM]},
        {
            "kind": "quote",
            "anchor": "um banco falido",
            "text": "Massa falida",
            "attribution": "fonte",
            "claims": [CLAIM],
        },
        photo("uma fábrica de tecidos", crop={"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.5}),
        {
            "kind": "lower_third",
            "anchor": "o genro",
            "name": "Genro",
            "role": "engenheiro",
            "claims": [CLAIM],
        },
    ]


# --- Contrato dos planos ------------------------------------------------------------------------


def test_shots_are_parsed_by_kind() -> None:
    parsed = scene(v2_shots()).shots
    assert [s.kind for s in parsed] == ["stamp", "quote", "photo", "lower_third"]
    chart = SHOT.validate_python(
        {
            "kind": "chart",
            "anchor": "x",
            "title": "Operários",
            "claims": [CLAIM],
            "points": [{"label": "1918", "value": 1500}, {"label": "1926", "value": 3000}],
        }
    )
    assert chart.kind == "chart"


@pytest.mark.parametrize(
    "kind_fields",
    [
        {"kind": "number", "value": "1.500", "label": "operários"},
        {"kind": "stamp", "date": "1918"},
        {"kind": "quote", "text": "t", "attribution": "a"},
        {"kind": "lower_third", "name": "n", "role": "r"},
    ],
)
def test_what_appears_on_screen_needs_a_source(kind_fields: dict[str, Any]) -> None:
    with pytest.raises(ValidationError, match="claims"):
        SHOT.validate_python({"anchor": "x", **kind_fields})  # §2.2 vale para a tela


def test_crop_and_family_tree_are_checked() -> None:
    with pytest.raises(ValidationError, match="recorte sai da imagem"):
        SHOT.validate_python(photo("x", crop={"x": 0.8, "y": 0, "width": 0.5, "height": 0.5}))
    with pytest.raises(ValidationError, match="pais inexistentes"):
        SHOT.validate_python(
            {
                "kind": "family_tree",
                "anchor": "x",
                "claims": [CLAIM],
                "people": [
                    {"id": "jose", "name": "José"},
                    {"id": "antonio", "name": "Antônio", "parent_ids": ["maria"]},
                ],
            }
        )


def test_anchors_must_appear_in_order() -> None:
    shots = v2_shots()
    with pytest.raises(ValidationError, match="não aparece"):
        scene([shots[2], shots[0]])  # "Em 1918" vem antes de "uma fábrica"
    with pytest.raises(ValidationError, match="não aparece"):
        scene([photo("texto que não existe")])


def test_v1_scene_becomes_a_single_photo_shot() -> None:
    v1 = ScenesManifest.model_validate_json((FIXTURE / "scenes.json").read_text()).scenes[0]
    (only,) = effective_shots(v1)
    assert (only.kind, only.anchor, only.asset_id) == ("photo", v1.narration, v1.chosen_asset_id)
    with pytest.raises(ValidationError, match="visual_need e search_query"):
        Scene.model_validate({"id": "S01", "narration": "texto"})


# --- Tempo e ritmo ------------------------------------------------------------------------------


def test_shot_times_follow_anchor_positions() -> None:
    shots = scene(v2_shots()).shots
    bounds = shot_bounds(NARRATION, shots, 10_000)
    assert bounds[0][0] == 0 and sum(d for _, d in bounds) == 10_000
    starts = [s for s, _ in bounds]
    assert starts == sorted(starts)
    assert starts[2] == round(NARRATION.find("uma fábrica de tecidos") / len(NARRATION) * 10_000)


def test_episode_v2_is_contiguous_and_media_goes_where_needed() -> None:
    sc = scene(v2_shots())
    shots = episode_shots(sc, 9_000, media_for=lambda shot: "assets/fabrica.jpg")
    assert [s.media for s in shots] == [None, None, "assets/fabrica.jpg", None]
    episode = EpisodeManifest.model_validate(
        {
            "schema_version": 2,
            "episode_id": "votorantim-fatia",
            "title": "Fatia",
            "language": "pt-BR",
            "format": "explainer",
            "scenes": [
                {
                    "id": "S01",
                    "start_ms": 0,
                    "duration_ms": 9_000,
                    "narration": NARRATION,
                    "audio": "voice/S01.wav",
                    "shots": [s.model_dump() for s in shots],
                }
            ],
        }
    )
    assert episode.language == "pt-BR" and len(episode.scenes[0].shots) == 4


def v2_episode(**scene_changes: Any) -> dict[str, Any]:
    shots = [s.model_dump() for s in episode_shots(scene(v2_shots()), 9_000, lambda shot: "assets/f.jpg")]
    return {
        "schema_version": 2,
        "episode_id": "fatia",
        "title": "Fatia",
        "language": "pt-BR",
        "format": "explainer",
        "scenes": [
            {
                "id": "S01",
                "start_ms": 0,
                "duration_ms": 9_000,
                "narration": NARRATION,
                "audio": "voice/S01.wav",
                "shots": shots,
                **scene_changes,
            }
        ],
    }


def test_episode_v2_rejects_gaps_and_mixed_forms() -> None:
    raw = v2_episode()
    raw["scenes"][0]["shots"][1]["start_ms"] += 10
    with pytest.raises(ValidationError, match="buraco ou sobreposição"):
        EpisodeManifest.model_validate(raw)
    with pytest.raises(ValidationError, match="não os dois"):
        EpisodeManifest.model_validate(v2_episode(image="assets/f.jpg", asset_id="f"))
    with pytest.raises(ValidationError, match="schema_version 1 não tem planos"):
        EpisodeManifest.model_validate({**v2_episode(), "schema_version": 1})


def test_pacing_is_a_warning_per_format() -> None:
    episode = EpisodeManifest.model_validate(v2_episode())
    # 4 planos em 9 s (média 2,25 s, dentro de 2–4 s), mas as duas primeiras âncoras estão próximas demais
    assert pacing_warnings(episode) == ["S01: 2 plano(s) com menos de 1.5 s"]
    documentary = episode.model_copy(update={"format": EpisodeFormat.ARCHIVAL_DOCUMENTARY})
    assert any("fora da faixa 4–6 s" in w for w in pacing_warnings(documentary))


# --- Integrações --------------------------------------------------------------------------------


def test_on_screen_claims_are_checked_against_sources() -> None:
    sources = SourcesManifest.model_validate_json((FIXTURE / "sources.json").read_text())
    shots = v2_shots()
    shots[0]["claims"] = [{"text": "data", "source_ids": ["source-09"]}]
    manifest = ScenesManifest(episode_id="fatia", language="pt-BR", scenes=[scene(shots)])
    assert unknown_source_refs(manifest, sources) == ["S01: fonte source-09 não está em sources.json"]


def test_stock_broll_cannot_be_a_historical_record() -> None:
    asset = Asset.model_validate_json((FIXTURE / "assets" / "commons-111-sc-91135.json").read_text())
    stock = asset.model_copy(update={"provider": Provider.PEXELS, "id": "pexels-1"})
    broll = {
        "kind": "broll",
        "anchor": "uma fábrica",
        "visual_need": "historical_exact",
        "search_query": "loom",
        "asset_id": "pexels-1",
    }
    manifest = ScenesManifest(episode_id="fatia", language="pt-BR", scenes=[scene([broll])])
    assert visual_need_violations(manifest, {"pexels-1": stock}) == [
        "S01: historical_exact não pode usar pexels"
    ]


def test_decision_counts_shots_not_scenes() -> None:
    manifest = ScenesManifest(episode_id="fatia", language="pt-BR", scenes=[scene(v2_shots())])
    decision = decide_from_scenes(manifest, now=datetime(2026, 9, 26, tzinfo=UTC))
    assert decision.recommended is EpisodeFormat.EXPLAINER  # 3 de 4 planos são gráficos


def test_ffmpeg_accepts_v2_only_with_a_single_photo_shot() -> None:
    single = EpisodeManifest.model_validate(
        v2_episode(
            shots=[{"start_ms": 0, "duration_ms": 9_000, "spec": photo(NARRATION), "media": "assets/f.jpg"}]
        )
    )
    assert scene_image(single.scenes[0]) == "assets/f.jpg"
    with pytest.raises(RenderError, match="vários planos"):
        scene_image(EpisodeManifest.model_validate(v2_episode()).scenes[0])


def test_kokoro_picks_voice_and_accent_by_language(tmp_path: Path) -> None:
    tts = KokoroTTS({"en": "am_michael", "pt-BR": "pm_alex"})
    out = tmp_path / "x.wav"
    assert tts.voice_for(SpeechRequest(text="t", out_path=out)) == ("a", "am_michael")
    assert tts.voice_for(SpeechRequest(text="t", out_path=out, language="pt-BR")) == ("p", "pm_alex")
    assert tts.voice_for(SpeechRequest(text="t", out_path=out, language="pt-BR", voice="pf_dora")) == (
        "p",
        "pf_dora",
    )
    with pytest.raises(ModelUnavailable, match="es"):
        tts.voice_for(SpeechRequest(text="t", out_path=out, language="es"))
