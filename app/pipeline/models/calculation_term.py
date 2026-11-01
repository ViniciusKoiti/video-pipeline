from __future__ import annotations

from app.pipeline.models._schemas_step import _Step
from app.pipeline.models._schemas_types import NonEmpty, Operator


class CalculationTerm(_Step):
    text: NonEmpty  # pronto, como a ficha traz: "R$ 18,44", "395 g"
    label: str = ""  # o que o termo é: "a embalagem"
    op: Operator | None = None  # antes do termo: obrigatório a partir do segundo, e só neles
