from __future__ import annotations

from typing import Any

from app.pipeline.models._molde_molde import _Molde
from app.pipeline.models.casas import Casas
from app.pipeline.models.medida import Medida
from app.pipeline.models.molde_videos import MoldeVideos
from app.pipeline.models.traco import Traco


class Molde(_Molde):
    gerado_em: str
    grupos: list[str] = []
    assunto: str | None = None
    videos: MoldeVideos
    medidas: dict[str, Medida] = {}
    prevalencia: dict[str, Traco] = {}
    curvas: dict[str, Any] = {}  # `decimos`, `n_videos` e uma lista por décimo para cada medida
    episodio: Casas | None = None
    copiado_em: str | None = None

    def curva(self, chave: str) -> list[float | None]:
        valores = self.curvas.get(chave)
        return list(valores) if isinstance(valores, list) else []

    def padrao(self, traco: str) -> Traco | None:
        """O traço, só quando a prevalência o sustenta como padrão."""
        item = self.prevalencia.get(traco)
        return item if item is not None and item.forca == "padrao" else None
