from __future__ import annotations

from app.pipeline.models.model import Model
from app.pipeline.models.numero import Numero


class Medicao(Model):
    arquivo: str  # relativo à pasta do vídeo ou à raiz do repositório
    ambiente: str | None = None
    numeros: list[Numero]
