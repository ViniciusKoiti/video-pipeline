"""Número na tela por idioma (ADR 011, emenda "número por idioma"): leitura, convenção e props do template."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter

from app.pipeline.check import CheckReport, check_episode
from app.pipeline.schemas import EpisodeManifest, Language, Shot, number_format_problem, screen_number
from app.render.remotion import PROJECT, RemotionEngine
from tests.test_remotion_props import FIXTURE
from tests.test_research import EP, episode, facts_file, scenes
from tests.test_shots import CLAIM, v2_episode

SHOT = TypeAdapter(Shot)
CASES = json.loads((Path(__file__).parent / "fixtures" / "screen-numbers.json").read_text())


# --- Leitura -------------------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c['language']}:{c['text']}")
def test_screen_number_reads_the_convention_of_each_language(case: dict[str, Any]) -> None:
    expected = case["number"]
    result = screen_number(case["text"], case["language"])
    if expected is None:
        assert result is None
    else:
        assert result == (expected["prefix"], expected["value"], expected["suffix"])


def test_screen_number_defaults_to_pt_br() -> None:
    assert screen_number("1.500") == ("", 1500.0, "")
    # o mesmo texto, lido em outro idioma, muda de valor
    assert screen_number("US$ 1,500") == ("US$", 1.5, "")


@pytest.mark.parametrize(
    ("value", "language"),
    [
        ("R$ 47,6 bi", "pt-BR"), ("1.500", "pt-BR"), ("R$ 1.234.567,89", "pt-BR"), ("78%", "pt-BR"),
        ("6ª", "pt-BR"), ("muito", "pt-BR"), ("1,5", "pt-BR"), ("0,125", "pt-BR"),
        ("US$ 1,500", "en"), ("$4.2 bn", "en"), ("1,234,567", "en"), ("$1,500.50", "en"), ("15.3%", "en"),
        ("1.500", "en"), ("6th", "en"), ("many", "en"),
    ],
)
def test_number_format_accepts_the_convention_of_the_language(value: str, language: Language) -> None:
    assert number_format_problem(value, language) is None


@pytest.mark.parametrize(
    ("value", "language"),
    [
        ("R$ 47,6 bi", "en"),  # vírgula decimal
        ("4,25%", "en"),
        ("1.234.567", "en"),  # ponto de milhar
        ("US$ 4.2 bn", "pt-BR"),  # ponto decimal
        ("15.3%", "pt-BR"),
        ("1,234,567", "pt-BR"),  # vírgula de milhar
        ("$1,500.50", "pt-BR"),
        ("12.34.56", "pt-BR"),
        ("1.5000", "pt-BR"),  # grupo de milhar com quatro dígitos
    ],
)
def test_number_format_refuses_the_other_convention(value: str, language: Language) -> None:
    problem = number_format_problem(value, language)
    assert problem is not None and repr(value) in problem and language in problem


def test_compare_in_scale_does_not_read_the_number_in_a_language() -> None:
    """A unidade (prefixo e sufixo) não depende do idioma: "US$ 1,234,567" é número em inglês."""
    raw = {"kind": "compare", "anchor": "x", "mode": "scale", "claims": [CLAIM],
           "left": {"value": "US$ 1,234,567", "label": "a"}, "right": {"value": "US$ 20,000", "label": "b"}}
    assert SHOT.validate_python(raw).kind == "compare"


# --- vp check ------------------------------------------------------------------------------------


def checked(tmp_path: Path, language: Language, shot: dict[str, Any]) -> CheckReport:
    raw = scenes()
    raw["language"] = language
    claims = raw["scenes"][0]["shots"][0]["claims"]
    raw["scenes"][0]["shots"][0] = {"anchor": "Em 1918", "claims": claims, **shot}
    facts = facts_file()
    facts["language"] = language
    return check_episode(episode(tmp_path, facts=facts, scenes_json=raw), EP)


def number(value: str) -> dict[str, Any]:
    return {"kind": "number", "value": value, "label": "x"}


def compare(left: str, right: str) -> dict[str, Any]:
    return {"kind": "compare", "left": {"value": left, "label": "a"}, "right": {"value": right, "label": "b"}}


def bars(values: list[float], kind: str = "bar") -> dict[str, Any]:
    labels = ["1927", "1928", "1929"] if kind == "line" else ["a", "b", "c"]
    return {"kind": "chart", "title": "t", "type": kind,
            "points": [{"label": label, "value": v} for label, v in zip(labels, values, strict=True)]}


@pytest.mark.parametrize(
    ("language", "shot"),
    [
        ("en", number("US$ 1,500")), ("en", number("$4.2 bn")), ("pt-BR", number("R$ 1.500")),
        ("pt-BR", number("R$ 4,2 bi")), ("en", number("many")), ("en", compare("US$ 1,500", "US$ 20,000")),
    ],
)
def test_screen_number_in_the_convention_of_the_episode_passes(
    tmp_path: Path, language: Language, shot: dict[str, Any]
) -> None:
    assert checked(tmp_path, language, shot).errors == []


@pytest.mark.parametrize(
    ("language", "shot", "wrong"),
    [
        ("en", number("R$ 47,6 bi"), "R$ 47,6 bi"),
        ("pt-BR", number("US$ 4.2 bn"), "US$ 4.2 bn"),
        ("en", compare("US$ 1,500", "4,25%"), "4,25%"),
        ("pt-BR", compare("12.34.56", "R$ 1.500"), "12.34.56"),
    ],
)
def test_screen_number_in_the_other_convention_is_an_error(
    tmp_path: Path, language: Language, shot: dict[str, Any], wrong: str
) -> None:
    (error,) = checked(tmp_path, language, shot).errors
    assert error.startswith("S01: ") and repr(wrong) in error and language in error


def test_english_bar_chart_is_limited_to_where_the_kit_formatting_agrees(tmp_path: Path) -> None:
    """O BarChart do kit fixado formata em pt-BR: "1.500" e "4,2" onde o inglês pede "1,500" e "4.2"."""
    for values in ([10, 20, 30], [999, 5, 0]):
        assert checked(tmp_path / str(values[0]), "en", bars(values)).errors == []
    for values in ([1500, 20, 30], [4.2, 5, 6]):
        (error,) = checked(tmp_path / str(values[0]), "en", bars(values)).errors
        assert re.search(r"S01: gráfico de barras .* pt-BR", error)
    assert checked(tmp_path / "pt", "pt-BR", bars([1500, 4.2, 30])).errors == []
    # o LineChart e o ShareChart do kit têm `locale`: só o BarChart limita
    assert checked(tmp_path / "line", "en", bars([1500, 2000, 3000], "line")).errors == []


# --- Props do template ---------------------------------------------------------------------------


def test_scene_props_carry_the_language_only_outside_pt_br(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "f.jpg").write_bytes(
        (FIXTURE / "assets" / "commons-lc-usz62-136192.jpg").read_bytes()
    )
    engine = RemotionEngine()
    (portuguese,) = engine.scene_props(EpisodeManifest.model_validate(v2_episode()), tmp_path, preview=True)
    (english,) = engine.scene_props(
        EpisodeManifest.model_validate({**v2_episode(), "language": "en"}), tmp_path, preview=True
    )
    assert "language" not in portuguese  # as props (e o cache) dos vídeos em português ficam como estavam
    assert english.pop("language") == "en"
    assert english == portuguese


# --- Espelho no template (Node) ------------------------------------------------------------------


def node_supports_type_stripping() -> bool:
    node = shutil.which("node")
    if node is None:
        return False
    version = subprocess.run([node, "--version"], capture_output=True, text=True, check=False).stdout
    match = re.match(r"v(\d+)\.(\d+)", version)
    return match is not None and (int(match[1]), int(match[2])) >= (22, 18)


@pytest.mark.skipif(not node_supports_type_stripping(), reason="Node 22.18+ ausente (TypeScript sem build)")
def test_template_reads_numbers_like_the_python_side() -> None:
    """`video/src/numbers.ts` e `screen_number` leem os mesmos casos de `fixtures/screen-numbers.json`."""
    result = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test", "tests/numbers.test.ts"],
        cwd=PROJECT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
