"""Estágio do funil (ADR 026 e emenda de 2026-11-16): topo, meio e fundo, com a chamada final, a pergunta dos
comentários no vídeo longo e, no fundo, a oferta."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.schemas import Funnel, ScenesManifest
from app.pipeline.script.checks.funnel import funnel_attention, funnel_errors, funnel_summary, funnel_warnings

LAST = "A conta é preço dividido pelo peso. Salva pra conferir na próxima encomenda."
MIDDLE = {"stage": "meio", "cta": "Salva pra conferir na próxima encomenda."}
OFFER = "planilha de custo por unidade"
BOTTOM = {"stage": "fundo", "cta": "Comenta PLANILHA que eu te mando.", "offer": OFFER}
ASK = "Nos comentários: em que você começaria a ficar bom?"
SUBSCRIBE = "Se inscreve no canal pra ver o próximo."
TOP_LONG = {"stage": "topo", "engagement": ASK, "cta": SUBSCRIBE}
CPS = 15.0
BODY = "Uma frase de corpo com umas palavras a mais para durar. " * 20  # ~1 min de fala a 15 caracteres/s


def manifest(funnel: dict[str, Any] | None, last: str = LAST, body: str = "Uma fala.") -> ScenesManifest:
    scenes = [
        {"id": f"S0{i}", "narration": body, "visual_need": "contextual_stock", "search_query": "x"}
        for i in range(1, 5)
    ]
    scenes.append({"id": "S05", "narration": last, "visual_need": "contextual_stock", "search_query": "x"})
    raw: dict[str, Any] = {"episode_id": "ep", "language": "pt-BR", "scenes": scenes}
    if funnel is not None:
        raw["funnel"] = funnel
    return ScenesManifest.model_validate(raw)


def test_each_stage_and_the_offer_only_at_the_bottom() -> None:
    assert Funnel.model_validate(MIDDLE).stage == "meio"
    assert Funnel.model_validate(BOTTOM).offer == OFFER
    assert Funnel.model_validate(TOP_LONG).engagement == ASK
    with pytest.raises(ValidationError, match="funil fundo precisa de offer"):
        Funnel.model_validate({**BOTTOM, "offer": None})
    with pytest.raises(ValidationError, match="offer só existe no funil fundo"):
        Funnel.model_validate({**MIDDLE, "offer": "planilha"})
    with pytest.raises(ValidationError):
        Funnel.model_validate({**MIDDLE, "stage": "lateral"})
    with pytest.raises(ValidationError):
        Funnel.model_validate({"stage": "topo"})  # sem chamada não entra


def test_script_without_a_stage_warns_and_old_scripts_still_load() -> None:
    assert manifest(None).funnel is None  # roteiros antigos continuam válidos
    (warning,) = funnel_warnings(manifest(None))
    assert "sem estágio do funil" in warning
    assert funnel_errors(manifest(None)) == []
    assert funnel_warnings(manifest(MIDDLE)) == [] and funnel_errors(manifest(MIDDLE)) == []


def test_a_call_that_does_not_ask_what_the_stage_asks_is_an_error() -> None:
    saves = "Salva pra conferir."
    (wrong,) = funnel_errors(manifest({"stage": "topo", "cta": saves}, saves))
    assert "funil topo" in wrong and "se inscrever" in wrong
    bottom = manifest(BOTTOM, "Quer a planilha pronta? Comenta PLANILHA que eu te mando.")
    assert funnel_errors(bottom) == []


def test_the_comment_question_alone_is_not_a_top_call() -> None:
    """O fecho do `vazio-de-ter-tudo`: a pergunta dos comentários no lugar da chamada do topo."""
    (wrong,) = funnel_errors(manifest({"stage": "topo", "cta": ASK}, ASK))
    assert "não pede para seguir, se inscrever" in wrong


@pytest.mark.parametrize("call", [
    "Segue pra ver a próxima.", SUBSCRIBE, "Compartilha com quem precisa.",
    "O próximo vídeo continua essa história.", "No próximo episódio, a segunda parte.",
])
def test_youtube_calls_count_at_the_top(call: str) -> None:
    assert funnel_errors(manifest({"stage": "topo", "cta": call}, call)) == []


def test_next_alone_is_not_a_call() -> None:
    call = "Na próxima encomenda, confere."
    assert funnel_errors(manifest({"stage": "topo", "cta": call}, call))


def test_the_call_is_said_in_the_last_scene() -> None:
    (missing,) = funnel_errors(manifest(MIDDLE, "A conta é preço dividido pelo peso."))
    assert "não está na narração da última cena (S05)" in missing
    # acentos, maiúsculas, pontuação e marcas de pausa não contam como diferença
    assert funnel_errors(manifest(MIDDLE, "Salva <short pause> pra CONFERIR na proxima encomenda!")) == []


def test_the_comment_question_comes_before_the_call_in_the_last_scene() -> None:
    assert funnel_errors(manifest(TOP_LONG, f"{ASK} {SUBSCRIBE}")) == []
    (missing,) = funnel_errors(manifest(TOP_LONG, SUBSCRIBE))
    assert "a pergunta" in missing and "(S05)" in missing
    (late,) = funnel_errors(manifest(TOP_LONG, f"{SUBSCRIBE} {ASK}"))
    assert "vem depois da chamada" in late


def test_long_video_without_the_comment_question_needs_attention() -> None:
    call = "Segue o canal."
    long_video = manifest({"stage": "topo", "cta": call}, call, body=BODY)
    (line,) = funnel_attention(long_video, CPS)
    assert "funnel.engagement" in line
    assert funnel_attention(manifest({"stage": "topo", "cta": call}, call), CPS) == []  # Short: um pedido só
    assert funnel_attention(manifest(TOP_LONG, f"{ASK} {SUBSCRIBE}", body=BODY), CPS) == []
    comment = "Comenta a sua dúvida."
    assert funnel_attention(manifest({"stage": "meio", "cta": comment}, comment, body=BODY), CPS) == []


def test_summary_line_shows_stage_question_call_and_offer() -> None:
    assert funnel_summary(manifest(None)) is None
    assert funnel_summary(manifest(MIDDLE)) == f"funil: meio; chamada: {MIDDLE['cta']}"
    assert funnel_summary(manifest(TOP_LONG)) == f"funil: topo; pergunta: {ASK}; chamada: {SUBSCRIBE}"
    line = funnel_summary(manifest(BOTTOM, "Comenta PLANILHA que eu te mando."))
    assert line is not None and line.endswith(f"; oferta: {OFFER}")
