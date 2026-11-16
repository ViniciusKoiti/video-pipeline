from __future__ import annotations

from app.pipeline.models._schemas_shot import _Shot


class _FactualShot(_Shot):
    """Plano que põe fato na tela (número, data, citação, cargo, gráfico): o `ScenesManifest` exige
    `claims` nele (ADR 008), salvo no roteiro de ficção histórica declarada (`fiction: true`, ADR 055,
    opção C). A regra mora no manifesto porque só ele sabe o formato; o plano solto (e o `episode.json`)
    aceita a lista vazia."""
