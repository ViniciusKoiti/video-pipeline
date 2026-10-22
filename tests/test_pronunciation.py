"""Glossário de pronúncia: a grafia que a voz lê, sem mudar o texto do roteiro."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.media.pronunciation import GLOSSARY_FILE, Glossary, Term, load_glossary, respell

GLOSSARY = Glossary(termos=[Term(escrita="FBI", fala="efe bê i"), Term(escrita="SPK", fala="esse pê cá")])


def test_whole_words_only_and_case_kept() -> None:
    text = "Doze agentes do FBI. <short pause> O prédio da SPK, não FBIs nem fbi."
    assert respell(text, GLOSSARY) == (
        "Doze agentes do efe bê i. <short pause> O prédio da esse pê cá, não FBIs nem fbi."
    )


def test_text_without_terms_is_unchanged() -> None:
    text = "Light faz um deles escrever o nome de todos."
    assert respell(text, GLOSSARY) == text
    assert respell(text, Glossary()) == text


def test_missing_file_is_an_empty_glossary(tmp_path: Path) -> None:
    assert load_glossary(tmp_path) == Glossary()
    (tmp_path / GLOSSARY_FILE).parent.mkdir()
    (tmp_path / GLOSSARY_FILE).write_text(GLOSSARY.model_dump_json(), encoding="utf-8")
    assert load_glossary(tmp_path) == GLOSSARY


def test_tags_are_refused() -> None:
    with pytest.raises(ValidationError, match="marcas"):
        Term(escrita="FBI", fala="efe <short pause> bê i")
