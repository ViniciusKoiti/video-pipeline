from __future__ import annotations

from typing import Any

from pydantic import SerializerFunctionWrapHandler, model_serializer

from app.pipeline.models._schemas_shot import _Shot


class _FactualShot(_Shot):
    """Plano que põe fato na tela (número, data, citação, cargo, gráfico): o `ScenesManifest` exige
    `claims` nele (ADR 008), salvo no roteiro de ficção histórica declarada (`fiction: true`, ADR 055,
    opção C). A regra mora no manifesto porque só ele sabe o formato; o plano solto (e o `episode.json`)
    aceita a lista vazia.

    `estimate` (ADR 065): numa cena `especulacao`, o dado na tela é estimativa da linha alternativa, não fato;
    é a única forma de um plano destes ficar sem `claims` nessa cena, e a tela o mostra com o selo."""

    estimate: bool = False

    @model_serializer(mode="wrap")
    def _omit_default_estimate(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if data.get("estimate") is False:  # o `episode.json` de antes (e seu carimbo no gate 4) não muda
            del data["estimate"]
        return data
