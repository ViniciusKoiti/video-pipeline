"""Rótulos do rodapé por idioma (ADR 011, emenda "número por idioma"): "A e B" e "A and B", "A et al."."""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from app.pipeline.attribution import INTERESTED_FLAG, shot_attribution, source_label
from app.pipeline.schemas import Claim, Language, Source
from app.pipeline.shots import episode_shots
from app.render.remotion import PROJECT
from tests.test_editorial_shots import NET, make_scene, network, sources_of
from tests.test_research import source
from tests.test_shots import photo


def label(language: Language, **extra: object) -> str:
    return source_label(Source.model_validate(source(1, **extra)), language)


def test_source_label_follows_the_language() -> None:
    two, three = ["Silva, Gustavo", "Dalla Costa, Armando"], ["A, x", "B, y", "C, z"]
    assert label("pt-BR", authors=two) == "Silva e Dalla Costa"
    assert label("en", authors=two) == "Silva and Dalla Costa"
    assert label("pt-BR", authors=three) == "A e outros"
    assert label("en", authors=three) == "A et al."
    # sem autores, o título
    assert label("en", title="Annual Report 2025 — Company A") == "Annual Report 2025"


def test_shot_attribution_follows_the_language() -> None:
    manifest = sources_of(
        source(1, authors=["Silva, G"]), source(3, title="Annual Report — Company A", interested=True),
        source(4, title="Newspaper B"),
    )

    def claims(*ids: int) -> list[Claim]:
        return [Claim(text="x", source_ids=[f"source-0{i}" for i in ids])]

    assert shot_attribution(claims(1, 3, 4), manifest, "pt-BR") == ("Silva; Annual Report e outras", None)
    assert shot_attribution(claims(1, 3, 4), manifest, "en") == ("Silva; Annual Report and others", None)
    assert shot_attribution(claims(3), manifest) == ("Annual Report", INTERESTED_FLAG)  # padrão: pt-BR
    assert shot_attribution(claims(3), manifest, "en") == ("Annual Report", "interested source")


def test_episode_shots_label_the_source_in_the_language_of_the_episode() -> None:
    manifest = sources_of(source(1, authors=["Silva, G"], interested=True))
    scene = make_scene([photo("O grupo", asset_id="f"), network("crédito no banco")], NET)
    _, portuguese = episode_shots(scene, 9000, lambda _: "assets/f.jpg", manifest)
    _, english = episode_shots(scene, 9000, lambda _: "assets/f.jpg", manifest, "en")
    assert (portuguese.source, portuguese.source_flag) == ("Silva", "fonte interessada")
    assert (english.source, english.source_flag) == ("Silva", "interested source")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node ausente")
def test_template_labels_cover_both_languages() -> None:
    """`video/src/labels.ts`: as mesmas palavras nos dois idiomas, nenhuma vazia, e o rodapé muda."""
    version = subprocess.run(["node", "--version"], capture_output=True, text=True, check=False).stdout
    match = re.match(r"v(\d+)\.(\d+)", version)
    if match is None or (int(match[1]), int(match[2])) < (22, 18):
        pytest.skip("Node 22.18+ ausente (TypeScript sem build)")
    result = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test", "tests/labels.test.ts"],
        cwd=PROJECT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
