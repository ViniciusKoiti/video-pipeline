"""Constantes de cli; dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from app.commands.arguments import (
    _approve_arguments,
    _bench_arguments,
    _checagem_arguments,
    _new_arguments,
    _numeros_arguments,
    _reject_arguments,
    _render_arguments,
    _reopen_arguments,
)
from app.commands.models.command import Command
from app.pipeline.schemas import CheckVerdict, Decision


class CliConstants:
    # erro esperado tratado na borda (`app.commands.errors.run`); 2 é o uso incorreto do argparse
    EXIT_ERROR: Final[int] = 1
    # distinto de 1 (falha) e 2 (uso incorreto, argparse)
    EXIT_NOT_IMPLEMENTED: Final[int] = 3
    # com `VP_DEBUG` definido, o erro tratado sobe com o traceback inteiro
    DEBUG_ENV: Final[str] = "VP_DEBUG"
    COMMANDS: Final[tuple[Command, ...]] = (
        Command(
            "bench",
            "RAM, CPU, tok/s do modelo local, tempo de TTS",
            5,
            takes_episode=False,
            add_arguments=_bench_arguments,
        ),
        Command("new", "cria data/episodes/<id>/ e o manifesto inicial", 12, add_arguments=_new_arguments),
        Command("sources", "busca, download e extração de texto -> sources.json", 26),
        Command("script", "roteiro com retrieval + validação de schema e de claims", 27),
        Command("scenes", "divisão em cenas + visual_need + search_query", 28),
        Command("assets", "busca visual em cascata, respeitando limites", 22),
        Command("gallery", "galeria HTML estática em 127.0.0.1", 23),
        Command("voice", "Kokoro por bloco + ffprobe -> voice/", 16),
        Command("subs", "legendas alinhadas -> captions.srt", 17),
        Command("render", "motor escolhido -> renders/", 13, add_arguments=_render_arguments),
        Command("export", "final.mp4 + srt + description.txt + credits.txt", 18),
        Command("approve", "registra aprovação humana em review.json", 12, add_arguments=_approve_arguments),
        Command("reject", "registra reprovação ou mudanças pedidas", 12, add_arguments=_reject_arguments),
        Command("status", "estados por etapa e pendências", 12),
        Command(
            "reopen",
            "reabre etapa aprovada para refazer (motivo no review.json)",
            12,
            add_arguments=_reopen_arguments,
        ),
        Command("excerpts", "trechos numerados de cada fonte -> excerpts/<fonte>.md (ADR 009)", 48),
        Command("check", "valida fontes, fichas e cenas, escritas por agente ou à mão (ADR 009)", 48),
        Command(
            "checagem",
            "grava o parecer do verificador sobre fichas e roteiro -> checagem.json (gate 2)",
            48,
            add_arguments=_checagem_arguments,
        ),
        Command("traducao", "confere a tradução contra o original: cenas, pausas e números (ADR 034)", 0),
        Command(
            "medicao", "confere os números do Short contra o arquivo de resultado da medição (ADR 034)", 0
        ),
        Command(
            "numeros",
            "números do roteiro e comparação com o nicho -> bloco do outline.md (#170)",
            170,
            add_arguments=_numeros_arguments,
        ),
    )
    DECISION_LABELS: Final = MappingProxyType(
        {
            Decision.APPROVED: "aprovado",
            Decision.REJECTED: "reprovado",
            Decision.CHANGES_REQUESTED: "mudanças pedidas",
        }
    )
    CHECK_LABELS: Final = MappingProxyType(
        {CheckVerdict.APPROVED: "aprovado", CheckVerdict.REJECTED: "reprovado"}
    )
