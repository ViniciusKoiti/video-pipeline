from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models.host_identity import HostIdentity
from app.pipeline.models.model import Model


class HostSpec(Model):
    """O apresentador do episódio: um personagem numa janela que muda de canto a cada cena (ADR 013).
    A boca segue o áudio de cada cena; o canto sai de uma regra sobre os planos (`app/media/host.py`).

    Pele `notionists`: personagem montado de peças (`identity`). Pele `dono` (ADR 017, parte A): o desenho
    do dono, em imagens na pasta do episódio (`app/media/host.py`), sem peças."""

    skin: Literal["notionists", "dono"] = "notionists"
    identity: HostIdentity | None = None

    @model_validator(mode="after")
    def _identity_matches_skin(self) -> Self:
        if self.skin == "notionists" and self.identity is None:
            raise ValueError("a pele notionists precisa de identity (as peças do personagem)")
        if self.skin != "notionists" and self.identity is not None:
            raise ValueError(f"a pele {self.skin} é um desenho pronto: não leva identity")
        return self
    width: float | None = Field(default=None, ge=0.1, le=0.5)  # fração do quadro; padrão por perfil

    def width_for(self, *, portrait: bool) -> float:
        """Largura da janela: a dada, ou o padrão do perfil (o quadro em pé é mais estreito)."""
        return self.width if self.width is not None else (0.28 if portrait else 0.16)
