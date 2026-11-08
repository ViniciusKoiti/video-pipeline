from __future__ import annotations

from pydantic import AwareDatetime

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.check_verdict import CheckVerdict
from app.pipeline.models.model import Model


class CheckEntry(Model):
    """Parecer do agente verificador sobre fichas e roteiro (skill `checagem`), gravado por `vp checagem`."""

    verdict: CheckVerdict
    problems: list[NonEmpty] = []  # uma linha por problema, no formato do relatório da skill
    reviewer: NonEmpty
    at: AwareDatetime
    input_hash: str  # hash de facts.json + scenes.json + outline.md no momento do parecer
