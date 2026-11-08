"""O parecer do verificador, escrito à mão ou por agente em JSON: lido uma vez, na entrada (ADR 009)."""

from __future__ import annotations

import json
from pathlib import Path

from app.pipeline.gates import GateError
from app.pipeline.schemas import CheckVerdict


def load_check_report(path: Path) -> tuple[CheckVerdict, list[str]]:
    """`{"verdict": "approved" | "rejected", "problems": [...]}`. Arquivo ausente ou fora desse formato é
    `GateError`: a tradução do erro de leitura em erro do domínio acontece aqui, e não em cada comando."""
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        return CheckVerdict(report["verdict"]), [str(problem) for problem in report.get("problems", [])]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise GateError(f"{path.name}: parecer inválido ({error})") from error
