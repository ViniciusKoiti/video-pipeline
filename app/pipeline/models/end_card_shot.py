from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import NonEmpty


class EndCardShot(_Shot):
    """Cartão final (`EndCta` do kit, com o selo da série): só no último plano do vídeo. A `variant` segue o
    estágio do funil (ADR 026): `follow` no topo, `save` no meio, `next` quando a série continua (ADR 028)."""

    kind: Literal["end_card"] = "end_card"
    variant: Literal["save", "follow", "next"]
    text: NonEmpty  # a chamada na tela, curta: "Salve para fazer a sua conta"
    sub: str = ""  # linha menor embaixo: "Parte 2: o docinho"
