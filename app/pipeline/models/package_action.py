from __future__ import annotations

from enum import StrEnum


class PackageAction(StrEnum):
    PUBLISHED = "published"  # o pacote novo ficou completo
    UNCHANGED = "unchanged"  # o vídeo e o texto já eram estes: nada foi escrito
