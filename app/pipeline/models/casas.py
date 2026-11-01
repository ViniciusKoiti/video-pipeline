from __future__ import annotations

from app.pipeline.models._molde_molde import _Molde


class Casas(_Molde):
    """O que a `partitura.py` pediu para este episódio, gravado na cópia do molde."""

    duracao_min: float
    assunto: str | None = None
    blocos: int | None = None
    abertura_s: float | None = None
    fecho_inicio_s: float | None = None
    confissao_s: float | None = None
