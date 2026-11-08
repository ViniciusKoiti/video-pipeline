from __future__ import annotations

from app.pipeline.models._schemas_types import HostVariant
from app.pipeline.models.model import Model


class HostIdentity(Model):
    """Peças do personagem (estilo Notionists, DiceBear); sem peça, vale a do estilo (ou nenhuma)."""

    hair: HostVariant
    outfit: HostVariant
    eyes: HostVariant = "variant05"
    brows: HostVariant | None = None
    nose: HostVariant | None = None
    facial_hair: HostVariant | None = None
    glasses: HostVariant | None = None
