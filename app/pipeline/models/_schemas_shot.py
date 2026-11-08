from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.claim import Claim
from app.pipeline.models.model import Model


class _Shot(Model):
    anchor: NonEmpty  # trecho da narração coberto pelo plano; precisa aparecer na narração, em ordem
    claims: list[Claim] = []  # o que o plano afirma na tela também precisa de fonte (§2.2)
