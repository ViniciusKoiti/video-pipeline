from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer, model_validator

from app.pipeline.models.host_identity import HostIdentity
from app.pipeline.models.model import Model


class HostSpec(Model):
    """O apresentador do episódio: um personagem numa janela que muda de canto a cada cena (ADR 013).
    A boca segue o áudio de cada cena; o canto sai de uma regra sobre os planos (`app/media/host.py`).

    Pele `notionists`: personagem montado de peças (`identity`). Pele `dono` (ADR 017, parte A): o desenho
    do dono, em imagens na pasta do episódio (`app/media/host.py`), sem peças.

    `show` (ADR 056): `all` (padrão) põe o apresentador em toda cena, menos nas marcadas `host: false`;
    `marked` só o põe nas cenas marcadas `host: true`, para ele entrar "às vezes"."""

    skin: Literal["notionists", "dono"] = "notionists"
    identity: HostIdentity | None = None
    show: Literal["all", "marked"] = "all"

    def shows(self, scene_host: bool | None) -> bool:
        """O apresentador aparece na cena? A marca da cena vale; sem ela, vale o `show` do episódio."""
        return scene_host if scene_host is not None else self.show == "all"

    @model_serializer(mode="wrap")
    def _omit_default_show(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if data.get("show") == "all":  # o `episode.json` de antes (e seu carimbo no gate 4) não muda
            del data["show"]
        return data

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
