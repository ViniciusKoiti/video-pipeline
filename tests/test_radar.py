"""Resumo do reels-radar no roteiro (ADR 018): leitura do contrato e alertas de forma. Dados sintéticos."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.check import check_episode
from app.pipeline.radar import (
    BRIEF_FILE,
    RadarBrief,
    brief_summary,
    form_warnings,
    opening_sentence,
    unmeasured_patterns,
)
from app.pipeline.schemas import ScenesManifest
from app.storage.json_files import JsonFileStore

SP = "<short pause>"


def guidance(
    trait: str, advice: str = "use", strength: str = "pattern", about: str = "form"
) -> dict[str, Any]:
    return {
        "about": about, "trait": trait, "advice": advice, "strength": strength,
        "share_rate_with": 0.0227, "share_rate_without": 0.0115, "n_with": 17, "n_without": 17,
        "chance": 0.03, "evidence": ["ig-exemplo"],
    }


def brief(*items: dict[str, Any], **changes: Any) -> RadarBrief:
    raw = {
        "schema": "script_brief.v1", "niche": "exemplo", "generated_at": "2026-10-12T03:21:19+00:00",
        "analysed": 34, "guidance": list(items), "themes": [guidance("celular", about="theme")],
        "thresholds": {
            "long_video_above_s": 72.0, "long_opening_above_words": 9.0, "long_caption_above_words": 150,
        },
        "caveats": ["Observation, not experiment."], "campo_novo_do_radar": {"qualquer": 1},
        **changes,
    }
    return RadarBrief.model_validate(raw)


V1 = {"visual_need": "contextual_stock", "search_query": "papel"}  # cena sem planos: a forma v1


def scenes(
    first: str, *rest: str, shots: list[dict[str, Any]] | None = None, language: str = "pt-BR"
) -> ScenesManifest:
    opening = {"shots": shots} if shots else V1
    all_scenes: list[dict[str, Any]] = [{"id": "S01", "narration": first, **opening}]
    all_scenes += [{"id": f"S{i:02d}", "narration": text, **V1} for i, text in enumerate(rest, start=2)]
    return ScenesManifest.model_validate({"episode_id": "ep", "language": language, "scenes": all_scenes})


LONG = "Uma frase comprida de narração que serve para encher o tempo do roteiro de teste. " * 14  # ~80 s a 14


def test_brief_is_read_by_its_contract_and_ignores_new_fields() -> None:
    read = brief(guidance("long_video"), guidance("ask_comment", strength="hint", about="engagement"))
    assert [g.trait for g in read.patterns()] == ["long_video"]
    assert [g.trait for g in read.hints()] == ["ask_comment"]
    assert brief_summary(read) == (
        "radar-brief.json: nicho exemplo, 34 Reels lidos, de 12/10/2026; "
        "1 padrão(ões) e 1 indício(s) de forma"
    )
    with pytest.raises(ValidationError):
        brief(schema="patterns.v1")


def test_opening_is_the_first_spoken_sentence_without_pause_marks() -> None:
    manifest = scenes(f"Você sabe quanto vale? {SP} Perto de trinta milhões.")
    assert opening_sentence(manifest) == "Você sabe quanto vale?"


def test_short_script_goes_against_the_long_video_pattern() -> None:
    read = brief(guidance("long_video"))
    (warning,) = form_warnings(scenes("Uma fala curta."), read, 14.0)
    assert "long_video anda com mais compartilhamento" in warning
    assert "2,3% com × 1,1% sem, n=17/17" in warning and "o corte é 72 s" in warning
    assert form_warnings(scenes(LONG), read, 14.0) == []


def test_avoid_advice_warns_when_the_script_has_the_trait() -> None:
    read = brief(guidance("long_video", advice="avoid"))
    (warning,) = form_warnings(scenes(LONG), read, 14.0)
    assert "anda com menos compartilhamento" in warning and "o roteiro tem" in warning
    assert form_warnings(scenes("Uma fala curta."), read, 14.0) == []


def test_opening_traits_are_measured_on_the_first_sentence() -> None:
    read = brief(guidance("addresses_viewer", about="opening"), guidance("opens_question", about="opening"))
    assert form_warnings(scenes("Você sabe quanto vale? Depois, o resto."), read, 14.0) == []
    warnings = form_warnings(scenes("A empresa assinou um contrato. Você sabia?"), read, 14.0)
    assert [w.split(":")[1].split()[0] for w in warnings] == ["addresses_viewer", "opens_question"]
    english = scenes("Do you know what it costs?", language="en")
    assert form_warnings(english, read, 14.0) == []


def test_alert_title_counts_in_the_first_shots_of_the_first_scene() -> None:
    read = brief(guidance("screen_alert", about="video"))
    photo = {"kind": "photo", "anchor": "Você sabe", "visual_need": "contextual_stock",
             "search_query": "papel", "asset_id": None}
    title = {"kind": "keyword", "anchor": "quanto vale", "text": "quanto vale?"}
    assert form_warnings(scenes("Você sabe quanto vale?", shots=[photo, title]), read, 14.0) == []
    (warning,) = form_warnings(scenes("Você sabe quanto vale?", shots=[photo]), read, 14.0)
    assert "screen_alert" in warning and "primeiros planos: photo" in warning


def test_caption_traits_only_with_a_caption() -> None:
    read = brief(guidance("has_emoji", about="opening"), guidance("ask_comment", about="engagement"))
    manifest = scenes("Você sabe quanto vale?")
    assert form_warnings(manifest, read, 14.0) == []  # sem legenda, nada a medir
    assert unmeasured_patterns(manifest, read, 14.0) == ["has_emoji", "ask_comment"]
    assert form_warnings(manifest, read, 14.0, caption="🚨 Você sabe?\n\nConta nos comentários.") == []
    assert len(form_warnings(manifest, read, 14.0, caption="Você sabe?\n\nÉ isso.")) == 2


def test_hints_themes_and_what_the_code_cannot_see_do_not_warn() -> None:
    read = brief(
        guidance("long_video", strength="hint"),
        guidance("scene_talking_head", about="video"),
        guidance("opens_alert", about="opening"),
    )
    manifest = scenes("Uma fala curta.")
    assert form_warnings(manifest, read, 14.0) == []
    assert unmeasured_patterns(manifest, read, 14.0) == ["scene_talking_head", "opens_alert"]


def test_old_brief_warns() -> None:
    read = brief()
    assert form_warnings(scenes(LONG), read, 14.0, today=date(2026, 10, 20)) == []
    (warning,) = form_warnings(scenes(LONG), read, 14.0, today=date(2026, 12, 1))
    assert "resumo de 12/10/2026 (50 dias)" in warning


def write_episode(root: Path, brief_raw: dict[str, Any] | None) -> JsonFileStore:
    folder = root / "ep"
    folder.mkdir(parents=True)
    manifest = scenes("A empresa assinou um contrato.")
    (folder / "scenes.json").write_text(manifest.model_dump_json())
    if brief_raw is not None:
        (folder / BRIEF_FILE).write_text(json.dumps(brief_raw))
    return JsonFileStore(root)


def test_vp_check_reads_the_episode_brief_and_only_warns(tmp_path: Path) -> None:
    read = brief(guidance("long_video"), guidance("scene_talking_head"))
    raw = json.loads(read.model_dump_json(by_alias=True))
    report = check_episode(write_episode(tmp_path, raw), "ep", today=date(2026, 10, 13))
    assert report.ok  # forma nunca é erro
    assert any(line.startswith("radar-brief.json: nicho exemplo") for line in report.checked)
    assert any("sem conferência no texto: scene_talking_head" in line for line in report.checked)
    assert any("long_video anda com mais" in w for w in report.warnings)


def test_vp_check_without_a_brief_says_nothing_about_the_radar(tmp_path: Path) -> None:
    report = check_episode(write_episode(tmp_path, None), "ep")
    assert not any("radar" in line for line in report.checked + report.warnings)


def test_brief_with_the_wrong_contract_is_an_error(tmp_path: Path) -> None:
    report = check_episode(write_episode(tmp_path, {"schema": "patterns.v1"}), "ep")
    assert any(error.startswith("radar-brief.json:") for error in report.errors)
