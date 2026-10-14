"""Trechos numerados, fichas de fatos e `vp check` (ADR 009)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.cli import main
from app.pipeline.check import check_episode
from app.pipeline.excerpts import excerpts_of, numbered_view, quote_in_excerpt, split_excerpts
from app.pipeline.schemas import FactsManifest, Source
from app.storage.json_files import JsonFileStore
from tests.fakes import make_root

EP = "fatia"
TEXT_A = (
    "Verbete sobre a família.\n\n"
    "Em 1918, Antônio Pereira Inácio adquiriu a fábrica   de tecidos\nVotorantim, em leilão.\n\n"
    "Casou-se com Helena, filha do industrial."
)
TEXT_B = "Outra fonte.\n\nA fábrica foi comprada em 1918 da massa falida do Banco União."


def source(n: int, **extra: Any) -> dict[str, Any]:
    return {
        "id": f"source-0{n}",
        "title": f"Fonte {n}",
        "url": f"https://example.org/{n}",
        "kind": "secondary",
        "retrieved_at": "2026-09-26T10:00:00-03:00",
        "local_path": f"sources/source-0{n}.txt",
        **extra,
    }


def fact(fid: str = "F01", **extra: Any) -> dict[str, Any]:
    return {
        "id": fid,
        "text": "A fábrica foi comprada em 1918.",
        "kind": "turning_point",
        "when": "1918",
        "why_it_matters": "É o começo do grupo.",
        "evidence": [
            {"excerpt_id": "source-01#E2", "quote": "Em 1918, Antônio Pereira Inácio adquiriu a fábrica"},
            {"excerpt_id": "source-02#E2", "quote": "comprada em 1918 da massa falida"},
        ],
        **extra,
    }


# um roteiro limpo declara o que se propõe a fazer (ADR 019)
OBJECTIVE = {
    "kinds": ["explicar"],
    "promise": "A pessoa entende como a fábrica mudou de dono.",
    "question": "Como uma fábrica falida mudou de dono?",
}


def scenes(**claim: Any) -> dict[str, Any]:
    narration = "Em 1918, uma fábrica de tecidos falida mudou de dono, comprada num leilão perto de Sorocaba."
    return {
        "episode_id": EP,
        "language": "pt-BR",
        "objective": OBJECTIVE,
        "scenes": [
            {
                "id": "S01",
                "narration": narration,
                "shots": [
                    {
                        "kind": "stamp",
                        "anchor": "Em 1918",
                        "date": "1918",
                        "claims": [
                            {"text": "compra em 1918", "source_ids": ["source-01"],
                             "excerpt_ids": ["source-01#E2"], **claim}
                        ],
                    },
                    {"kind": "photo", "anchor": "comprada num leilão", "visual_need": "map_or_graphic",
                     "search_query": "mapa"},
                ],
            }
        ],
    }


def episode(tmp_path: Path, *, facts: dict[str, Any] | None = None, scenes_json: dict[str, Any] | None = None,
            sources: list[dict[str, Any]] | None = None) -> JsonFileStore:
    root = tmp_path / "episodes" / EP
    (root / "sources").mkdir(parents=True)
    (root / "sources" / "source-01.txt").write_text(TEXT_A)
    (root / "sources" / "source-02.txt").write_text(TEXT_B)
    files = {
        "sources.json": {"episode_id": EP, "sources": sources or [source(1), source(2)]},
        "facts.json": facts,
        "scenes.json": scenes_json,
    }
    for name, content in files.items():
        if content is not None:
            (root / name).write_text(json.dumps(content, ensure_ascii=False))
    return JsonFileStore(tmp_path / "episodes")


def facts_file(*items: dict[str, Any]) -> dict[str, Any]:
    return {"episode_id": EP, "language": "pt-BR", "facts": list(items) or [fact()]}


# --- Trechos -------------------------------------------------------------------------------------


def test_excerpts_are_numbered_paragraphs() -> None:
    parts = split_excerpts(TEXT_A)
    assert len(parts) == 3
    assert parts[1] == "Em 1918, Antônio Pereira Inácio adquiriu a fábrica de tecidos Votorantim, em leilão."
    src = Source.model_validate(source(1))
    assert list(excerpts_of(src, TEXT_A)) == ["source-01#E1", "source-01#E2", "source-01#E3"]


@pytest.mark.parametrize(
    ("quote", "found"),
    [
        ("adquiriu a fábrica de tecidos", True),
        ("Em 1918 [...] em leilão", True),  # corte marcado
        ("Em 1918… Votorantim", True),
        ("adquiriu a fábrica  de\ntecidos", True),  # espaços não contam
        ("comprou a fábrica", False),  # paráfrase não é citação
        ("em leilão ... Em 1918", False),  # partes fora de ordem
        ("...", False),
    ],
)
def test_quote_must_be_literal(quote: str, found: bool) -> None:
    assert quote_in_excerpt(quote, split_excerpts(TEXT_A)[1]) is found


def test_facts_contract() -> None:
    manifest = FactsManifest.model_validate(facts_file())
    assert manifest.facts[0].source_ids == ["source-01", "source-02"]
    with pytest.raises(ValidationError, match="ids de fato duplicados"):
        FactsManifest.model_validate(facts_file(fact(), fact()))
    with pytest.raises(ValidationError, match="evidence"):
        FactsManifest.model_validate(facts_file(fact(evidence=[])))


# --- vp check ------------------------------------------------------------------------------------


def test_clean_episode_passes(tmp_path: Path) -> None:
    report = check_episode(episode(tmp_path, facts=facts_file(), scenes_json=scenes()), EP)
    assert report.ok, report.errors
    assert report.warnings == []
    assert any("1 fato(s) (turning_point 1)" in line for line in report.checked)


def test_invented_quote_and_missing_excerpt_are_errors(tmp_path: Path) -> None:
    bad = fact(evidence=[
        {"excerpt_id": "source-01#E2", "quote": "comprou por mil contos de réis"},
        {"excerpt_id": "source-02#E9", "quote": "x"},
    ])
    report = check_episode(episode(tmp_path, facts=facts_file(bad)), EP)
    assert report.errors == [
        "F01: citação não está em source-01#E2: 'comprou por mil contos de réis'",
        "F01: trecho source-02#E9 não existe",
    ]


def test_single_and_interested_sources_are_warnings(tmp_path: Path) -> None:
    single = fact("F01", evidence=[fact()["evidence"][0]])
    only_company = fact("F02", evidence=[fact()["evidence"][1]])
    store = episode(tmp_path, facts=facts_file(single, only_company),
                    sources=[source(1), source(2, interested=True)])
    report = check_episode(store, EP)
    assert report.ok
    assert report.warnings == ["F01: uma fonte só (source-01)", "F02: só fontes interessadas (source-02)"]


def test_declared_source_may_omit_url_but_others_may_not() -> None:
    declared = Source.model_validate(source(3, kind="declared", url=None))
    assert declared.url is None
    with pytest.raises(ValidationError, match="sem url"):
        Source.model_validate(source(3, url=None))


def test_declared_source_is_a_warning_and_says_so_in_the_excerpts(tmp_path: Path) -> None:
    declared = source(2, kind="declared", url=None)
    report = check_episode(episode(tmp_path, facts=facts_file(), sources=[source(1), declared]), EP)
    assert report.ok
    assert report.warnings == [
        "source-02: fonte declarada pelo dono, sem URL; ele responde por ela no gate 1"
    ]
    view = numbered_view(Source.model_validate(declared), "Um trecho.")
    assert "Fonte declarada pelo dono" in view and "[source-02#E1] Um trecho." in view


def test_script_may_only_cite_fact_cards(tmp_path: Path) -> None:
    without_excerpt = check_episode(
        episode(tmp_path / "a", facts=facts_file(), scenes_json=scenes(excerpt_ids=[])), EP
    )
    assert without_excerpt.errors == ["S01: afirmação sem trecho: 'compra em 1918'"]
    off_cards = check_episode(
        episode(tmp_path / "b", facts=facts_file(), scenes_json=scenes(excerpt_ids=["source-01#E3"])), EP
    )
    assert off_cards.errors == ["S01: trecho source-01#E3 não está em nenhuma ficha"]


def test_estimated_pacing_flags_short_shots(tmp_path: Path) -> None:
    raw = scenes()
    raw["scenes"][0]["shots"][1]["anchor"] = "uma fábrica"  # 9 caracteres depois de "Em 1918"
    report = check_episode(episode(tmp_path, facts=facts_file(), scenes_json=raw), EP)
    assert report.ok
    assert report.warnings == ["S01: plano stamp ('Em 1918') com ~0.6 s"]


def test_facts_need_downloaded_sources(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path)
    (tmp_path / EP).mkdir()
    (tmp_path / EP / "facts.json").write_text(json.dumps(facts_file()))
    assert check_episode(store, EP).errors == [
        "facts.json sem sources.json: fato só a partir de fonte baixada (§2.2)"
    ]
    assert check_episode(store, "vazio").errors == [
        "nada para validar em vazio (sources.json, facts.json, scenes.json)"
    ]


def test_cli_check_and_excerpts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                capsys: pytest.CaptureFixture[str]) -> None:
    root = make_root(tmp_path)
    episode(root / "data", facts=facts_file(), scenes_json=scenes())
    monkeypatch.chdir(root)
    assert main(["check", EP]) == 0
    assert "resultado: sem erros" in capsys.readouterr().out
    assert main(["excerpts", EP]) == 0
    view = (root / "data" / "episodes" / EP / "excerpts" / "source-01.md").read_text()
    assert "[source-01#E2] Em 1918, Antônio Pereira Inácio" in view
    (root / "data" / "episodes" / EP / "facts.json").write_text(json.dumps(facts_file(fact(kind="rumor"))))
    assert main(["check", EP]) == 1
    assert "erro    facts.json: facts.0.kind" in capsys.readouterr().out


def test_sources_sharing_an_author_are_not_independent(tmp_path: Path) -> None:
    sources = [
        source(1, authors=["Dalla Costa, A. J.", "Silva, G. P."]),
        source(2, authors=["silva,  g. p."]),  # caixa e espaços não contam
    ]
    report = check_episode(episode(tmp_path, facts=facts_file(), sources=sources), EP)
    assert report.ok
    assert report.warnings == ["F01: fontes com os mesmos autores (source-01, source-02)"]
    independent = [source(1, authors=["Dalla Costa, A. J."]), source(2, authors=["Pantoja, S."])]
    assert check_episode(episode(tmp_path / "b", facts=facts_file(), sources=independent), EP).warnings == []


def test_profile_kinds_count_in_the_summary(tmp_path: Path) -> None:
    impact = fact("F01", kind="impact_today")
    rule = fact("F02", kind="rule")
    report = check_episode(episode(tmp_path, facts=facts_file(impact, rule)), EP)
    assert report.ok
    assert any("2 fato(s) (impact_today 1, rule 1)" in line for line in report.checked)
