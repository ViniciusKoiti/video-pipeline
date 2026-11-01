from __future__ import annotations

from enum import StrEnum


class BriefAction(StrEnum):
    INSTALLED = "installed"  # o episódio não tinha: cópia nova
    UNCHANGED = "unchanged"  # já era este conteúdo: nada foi escrito
    REPLACED = "replaced"  # trocado com `--atualizar`; o anterior ficou guardado com a data dele
