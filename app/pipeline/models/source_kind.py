from __future__ import annotations

from enum import StrEnum


class SourceKind(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    NEWSPAPER = "newspaper"
    ARCHIVE = "archive"
    DECLARED = "declared"  # material do próprio dono (receita, nota de compra), sem URL; ele responde por ele
