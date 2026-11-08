from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_types import Sha256
from app.pipeline.models.model import Model


class PackageMarker(Model):
    """`renders/pacote.json`: o que o pacote devia ser. `writing` = a gravação não terminou."""

    state: Literal["writing", "complete"]
    video_sha256: Sha256
    text_sha256: Sha256
