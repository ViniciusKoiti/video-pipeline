"""Lacuna dita na fala (decisão do dono, 2026-11-14): o `vp check` avisa quando o narrador diz que não
achou."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.pipeline.check import check_episode
from app.pipeline.narration_gaps import gap_warnings
from app.pipeline.schemas import ScenesManifest
from app.storage.json_files import JsonFileStore


def manifest(*narrations: str, language: str = "pt-BR") -> ScenesManifest:
    scenes = [
        {"id": f"S{i:02d}", "narration": text, "visual_need": "contextual_stock", "search_query": "x"}
        for i, text in enumerate(narrations, start=1)
    ]
    raw: dict[str, Any] = {"episode_id": "ep", "language": language, "scenes": scenes}
    return ScenesManifest.model_validate(raw)


def test_narrator_saying_it_did_not_find_warns_with_the_words_as_said() -> None:
    (warning,) = gap_warnings(manifest("Uma fala.", "Quanto é esse repasse, eu não encontrei."))
    assert warning.startswith("S02: a fala diz que não achou ('não encontrei')")
    assert "eu acho X, porque Y" in warning


def test_other_ways_of_saying_it_and_english() -> None:
    texts = (
        "Medido, eu não achei.", "Isso eu não sei.", "Não consegui descobrir quanto.", "I couldn’t find it.",
    )
    assert len(gap_warnings(manifest(*texts[:3]))) == 3
    assert len(gap_warnings(manifest(texts[3], language="en"))) == 1


def test_pause_mark_in_the_middle_does_not_hide_it() -> None:
    assert gap_warnings(manifest("Quanto é, eu não <short pause> encontrei."))


def test_opinion_with_a_reason_and_found_data_do_not_warn() -> None:
    ok = (
        "Eu acho que a maior parte disso é mensalidade, porque só catorze por cento pagavam a taxa.",
        "Encontrei esse número no balanço.",
        "A empresa não diz qual.",
    )
    assert gap_warnings(manifest(*ok)) == []


def test_vp_check_reports_it_as_a_warning_not_an_error(tmp_path: Path) -> None:
    folder = tmp_path / "ep"
    folder.mkdir()
    (folder / "scenes.json").write_text(manifest("Quanto cada um pesa, eu não encontrei.").model_dump_json())
    report = check_episode(JsonFileStore(tmp_path), "ep")
    assert report.ok
    assert any("a fala diz que não achou" in w for w in report.warnings)
