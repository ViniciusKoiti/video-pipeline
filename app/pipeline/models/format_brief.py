from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field

from app.pipeline.models._numbers_brief import _Brief
from app.pipeline.models.format_measure import FormatMeasure


class FormatBrief(_Brief):
    schema_name: Literal["formato_brief.v1"] = Field(alias="schema")
    nicho: str
    grupo: str
    data: date
    n: int
    medidas: dict[str, FormatMeasure]
