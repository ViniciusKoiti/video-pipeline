"""Checagem local (#27): prompt, gabarito por mutação e pontuação. Sem rede nem modelo (FakeText)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.pipeline.checagem_local import (
    EXPECTED,
    Case,
    Result,
    build_cases,
    clean_claim,
    load_prompt,
    render,
    run,
    score,
)
from tests.fakes import FakeText

ROOT = Path(__file__).resolve().parents[1]
ALIEN = "Quadro de mercado de tecidos com muitos compradores atacadistas regionais e exportadores. " * 3
SOURCE_1 = "A fábrica de Cidade B foi adquirida pela Empresa A em 1950, depois de dois anos parada."
CLAIM = "Em 1950, a Empresa A comprou a fábrica de Cidade B (F01)"


@pytest.fixture
def episode(tmp_path: Path) -> Path:
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "source-01.txt").write_text(SOURCE_1, encoding="utf-8")
    (tmp_path / "sources" / "source-02.txt").write_text(ALIEN, encoding="utf-8")
    source = {"kind": "secondary", "retrieved_at": "2026-09-26T15:05:48-03:00"}
    (tmp_path / "sources.json").write_text(
        json.dumps(
            {
                "episode_id": "t",
                "sources": [
                    {"id": "source-01", "title": "A", "url": "https://example.org/a",
                     "local_path": "sources/source-01.txt", **source},
                    {"id": "source-02", "title": "B", "url": "https://example.org/b",
                     "local_path": "sources/source-02.txt", **source},
                ],
            }
        ),
        encoding="utf-8",
    )
    claim = {"text": CLAIM, "source_ids": ["source-01"], "excerpt_ids": ["source-01#E1"]}
    scene = {"id": "S01", "narration": "Em 1950, a Empresa A comprou a fábrica.", "claims": [claim],
             "visual_need": "historical_exact", "search_query": "fábrica"}
    (tmp_path / "scenes.json").write_text(
        json.dumps({"episode_id": "t", "language": "pt-BR", "scenes": [scene]}), encoding="utf-8"
    )
    return tmp_path


def test_prompt_file_has_both_sections_and_placeholders() -> None:
    system, template = load_prompt(ROOT)
    for verdict in ("SUSTENTA", "DIVERGE", "SEM_SUPORTE", "EXAGERO"):
        assert verdict in system
    assert all(slot in template for slot in ("{{afirmacao}}", "{{ids}}", "{{trecho}}"))


def test_render_fills_the_slots() -> None:
    _, template = load_prompt(ROOT)
    case = Case("c", "real", "afirmação X", ("source-01#E1", "source-01#E2"), "texto do trecho")
    prompt = render(template, case)
    assert "afirmação X" in prompt and "source-01#E1, source-01#E2" in prompt and "texto do trecho" in prompt
    assert "{{" not in prompt


def test_clean_claim_drops_the_fact_id() -> None:
    assert clean_claim("Em 1950, A comprou B (F01)") == "Em 1950, A comprou B"
    assert clean_claim("Texto (F54, F55)") == "Texto"


def test_build_cases_makes_one_case_of_each_kind(episode: Path) -> None:
    cases = {c.kind: c for c in build_cases(episode)}
    assert set(cases) == set(EXPECTED)
    assert cases["real"].claim == "Em 1950, a Empresa A comprou a fábrica de Cidade B"
    assert "1950" not in cases["numero"].claim and "(F01)" not in cases["numero"].claim
    assert cases["superlativo"].claim.endswith("o maior de todo o país.")
    assert cases["trecho_alheio"].excerpt_ids == ("source-02#E1",)
    assert cases["trecho_alheio"].excerpt == ALIEN.strip()


def test_build_cases_is_deterministic(episode: Path) -> None:
    assert build_cases(episode, seed=3) == build_cases(episode, seed=3)


def test_run_scores_verdicts_against_the_expected_label(episode: Path) -> None:
    cases = build_cases(episode)
    by_kind = {c.kind: c for c in cases}
    answers = {"real": "SUSTENTA", "numero": "DIVERGE", "trecho_alheio": "SUSTENTA", "superlativo": "EXAGERO"}
    fake = FakeText([json.dumps({"confronto": "c", "veredito": answers[c.kind]}) for c in cases])
    system, template = load_prompt(ROOT)
    results = run(fake, cases, system, template, model="m", tick=iter(range(100)).__next__)
    assert [r.case.kind for r in results] == [c.kind for c in cases]
    assert fake.requests[0].model == "m" and fake.requests[0].system == system
    summary = score(results)
    assert summary["alarme_falso"] == 0
    assert summary["erro_deixado_passar"] == pytest.approx(1 / 3)  # só o trecho alheio passou
    assert summary["por_tipo"]["numero"]["rotulo_certo"] == 1
    assert summary["por_tipo"]["trecho_alheio"]["rotulo_certo"] == 0
    assert by_kind["real"].expected == "SUSTENTA"


def test_invalid_model_output_is_recorded_and_the_run_continues(episode: Path) -> None:
    cases = build_cases(episode)
    valid = json.dumps({"confronto": "c", "veredito": "SUSTENTA"})
    fake = FakeText(["não é json"] + [valid] * (len(cases) - 1))
    system, template = load_prompt(ROOT)
    results = run(fake, cases, system, template)
    assert results[0].verdict is None and results[0].error
    assert all(r.verdict == "SUSTENTA" for r in results[1:])
    assert score(results)["por_tipo"][results[0].case.kind]["sem_json_valido"] == 1


def test_score_handles_an_empty_run() -> None:
    assert score([])["casos"] == 0
    only_real = [Result(Case("c", "real", "x", ("s#E1",), "t"), "EXAGERO", "c", "", 1.0)]
    assert score(only_real)["alarme_falso"] == 1 and score(only_real)["erros_pegos"] is None
