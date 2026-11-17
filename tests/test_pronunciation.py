"""Glossário de pronúncia: a grafia que a voz lê, sem mudar o texto do roteiro."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.media.constants.pronunciation_constants import PronunciationConstants
from app.media.pronunciation import Glossary, Term, ipa_lexicon, load_glossary, respell

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


def test_replacement_keeps_backslashes_literal() -> None:
    glossary = Glossary(termos=[Term(escrita="termo", fala=r"fala\1\nome")])
    assert respell("termo", glossary) == r"fala\1\nome"


def test_missing_file_is_an_empty_glossary(tmp_path: Path) -> None:
    assert load_glossary(tmp_path) == Glossary()
    (tmp_path / PronunciationConstants.GLOSSARY_FILE).parent.mkdir()
    (tmp_path / PronunciationConstants.GLOSSARY_FILE).write_text(GLOSSARY.model_dump_json(), encoding="utf-8")
    assert load_glossary(tmp_path) == GLOSSARY


def test_tags_are_refused() -> None:
    with pytest.raises(ValidationError, match="marcas"):
        Term(escrita="FBI", fala="efe <short pause> bê i")


def test_a_term_with_ipa_keeps_the_script_spelling_for_a_phoneme_voice() -> None:
    glossary = Glossary(termos=[
        Term(escrita="TotalPass", fala="Tótal Pás", ipa="ˌtɔ.taw.ˈpas"), Term(escrita="FBI", fala="efe bê i"),
    ])
    text = "O TotalPass e o FBI."
    assert respell(text, glossary) == "O Tótal Pás e o efe bê i."  # voz sem fonemas lê a `fala`
    assert respell(text, glossary, keep_ipa=True) == "O TotalPass e o efe bê i."
    assert ipa_lexicon(glossary) == {"TotalPass": "ˌtɔ.taw.ˈpas"}


def test_ipa_cannot_carry_markup() -> None:
    with pytest.raises(ValidationError):
        Term(escrita="TotalPass", fala="Tótal Pás", ipa='"/><break time="20s')
