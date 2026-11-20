"""Trava fonética no `vp check`: termo de fora sem glossário, `ipa` na voz do Azure e dois-pontos sem pausa
antes de pergunta (CLAUDE.md §6; emenda de 2026-11-16 da ADR 062)."""

from __future__ import annotations

from typing import Any

from app.media.pronunciation import Glossary
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.checks.glossary import colon_pause_warnings, glossary_attention, missing_terms

VINLAND = (
    "Vazio é a palavra de um episódio de Vinland Saga, um anime. O oitavo episódio se chama An Empty Man.",
    "Thorfinn trabalha ao lado de Einar. No episódio seguinte, chamado Oath, ele jura.",
    "Se o peso for grande, o CVV atende a qualquer hora, pelo <short pause> 188.",
)


def manifest(*narrations: str, language: str = "pt-BR") -> ScenesManifest:
    scenes: list[dict[str, Any]] = [
        {"id": f"S0{i}", "narration": text, "visual_need": "contextual_stock", "search_query": "x"}
        for i, text in enumerate(narrations, start=1)
    ]
    return ScenesManifest.model_validate({"episode_id": "ep", "language": language, "scenes": scenes})


def glossary(*pairs: tuple[str, str] | tuple[str, str, str]) -> Glossary:
    terms = [{"escrita": p[0], "fala": p[1], **({"ipa": p[2]} if len(p) > 2 else {})} for p in pairs]
    return Glossary.model_validate({"termos": terms})


def test_foreign_terms_without_an_entry_are_found_in_order() -> None:
    assert missing_terms(manifest(*VINLAND), Glossary()) == ["Vinland", "Empty", "Thorfinn", "Oath", "CVV"]


def test_a_multiword_entry_covers_each_of_its_words() -> None:
    covered = glossary(("Vinland Saga", "Vin Land Saga"), ("An Empty Man", "én émpti mén"),
                       ("Thorfinn", "Tórfin"), ("Oath", "ôuf"), ("CVV", "cê vê vê"))
    assert missing_terms(manifest(*VINLAND), covered) == []


def test_portuguese_words_and_names_pass() -> None:
    text = "O aluguel está pago, a luz acende e o jantar foi bom em São Paulo, com Maria e o Brasil inteiro."
    assert missing_terms(manifest(text), Glossary()) == []


def test_quotes_ordinals_single_letters_emphasis_and_native_exceptions_pass() -> None:
    """Falsos positivos da varredura de 2026-11-17 nos roteiros antigos ("incerteza'", "º", "C", "SIM",
    "sob")."""
    text = ("Ele disse 'incerteza' e 'bom' sob a chuva, no 1º dia; a opção C. "
            "A resposta é SIM, e o sim dele vale. A Pizzaria fechou.")
    assert missing_terms(manifest(text), Glossary()) == []


def test_an_uppercase_word_never_written_in_lowercase_is_still_an_acronym() -> None:
    assert missing_terms(manifest("O IBGE mede. A resposta é SIM."), Glossary()) == ["IBGE", "SIM"]


def test_the_english_narration_is_left_alone() -> None:
    assert missing_terms(manifest("The worker was thinking about the WiFi.", language="en"), Glossary()) == []


def test_attention_names_the_missing_terms_and_the_ipa_the_azure_voice_needs() -> None:
    (line,) = glossary_attention(manifest(*VINLAND), Glossary(), "chatterbox_modal")
    assert line.startswith("glossário: 5 termo(s) de fora sem entrada") and "Thorfinn" in line
    full = glossary(("Vinland", "Vin Land", "vinlɐ̃d"), ("Empty", "émpti"), ("Thorfinn", "Tórfin"),
                    ("Oath", "ôuf"), ("CVV", "cê vê vê"), ("188", "cento e oitenta e oito"))
    assert glossary_attention(manifest(*VINLAND), full, "chatterbox_modal") == []
    (azure,) = glossary_attention(manifest(*VINLAND), full, "azure_speech")
    assert azure.endswith("falta `ipa` em: Empty, Thorfinn, Oath, CVV")  # número não precisa de fonema


def test_a_colon_that_opens_a_question_wants_a_pause_after_it() -> None:
    texts = (
        "Pode ser que ela pense: sem vontade nenhuma, como é que eu começo?",
        "Pode ser que ela pense: <short pause> sem vontade nenhuma, como é que eu começo?",
        "Abre uma conversa antiga e escreve: oi, sumido.",
    )
    (warning,) = colon_pause_warnings(manifest(*texts))
    assert warning.startswith("S01: dois-pontos antes de pergunta")
