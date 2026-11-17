from __future__ import annotations

from typing import Self

from pydantic import model_validator

from app.pipeline.models._schemas_types import FunnelStage, NonEmpty
from app.pipeline.models.model import Model


class Funnel(Model):
    """Em que estágio do funil o vídeo trabalha e o que ele pede a quem assiste (ADR 026).

    - `topo`: alcance. Tema amplo, gancho forte, pouco método; a chamada pede para seguir ou compartilhar.
    - `meio`: confiança. Ensina a conta ou o método, com fonte; a chamada pede para salvar ou comentar a
      dúvida.
    - `fundo`: ação. Oferece a planilha ou o modelo (`offer`); a chamada diz como pedir.

    No vídeo longo, `engagement` é a pergunta para os comentários, dita na última cena antes da chamada
    (emenda de 2026-11-16). O estágio vem do dono, pela pauta, como o objetivo."""

    stage: FunnelStage
    cta: NonEmpty  # a chamada final, como a narração a diz
    engagement: NonEmpty | None = None  # a pergunta para os comentários, antes da chamada, na última cena
    offer: NonEmpty | None = None  # o que o vídeo oferece: obrigatório no fundo, e só existe nele

    @model_validator(mode="after")
    def _offer_only_at_the_bottom(self) -> Self:
        if self.stage == "fundo" and self.offer is None:
            raise ValueError("funil fundo precisa de offer: o que o vídeo oferece")
        if self.stage != "fundo" and self.offer is not None:
            raise ValueError("offer só existe no funil fundo")
        return self
