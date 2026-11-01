"""`vp medicao` e `vp traducao`: conferências que só leem e dizem os problemas (ADR 034)."""

from __future__ import annotations

import argparse

from app.pipeline.medicao import medicao_problems
from app.pipeline.ports import Context
from app.pipeline.translation import translation_problems


def _report(problems: list[str], warnings: list[str] | None = None) -> int:
    for problem in problems:
        print(f"- {problem}")
    for warning in warnings or []:
        print(f"- aviso: {warning}")
    print("resultado: " + (f"{len(problems)} problema(s)" if problems else "sem problemas"))
    return 1 if problems else 0


def medicao(args: argparse.Namespace, context: Context) -> int:
    """Os números de um Short contra o arquivo de resultado da medição do dono (`medicao.json`)."""
    return _report(*medicao_problems(context.store, args.episode_id))


def traducao(args: argparse.Namespace, context: Context) -> int:
    """Uma pasta de tradução contra o original: cenas, entregas, pausas e números."""
    return _report(translation_problems(context.store, args.episode_id))
