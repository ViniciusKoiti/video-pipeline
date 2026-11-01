from __future__ import annotations

from enum import StrEnum


class TrackInstallAction(StrEnum):
    INSTALLED = "installed"  # faixa e ativo copiados para o episódio
    UNCHANGED = "unchanged"  # o episódio já tinha exatamente esta faixa
    REPAIRED = "repaired"  # o ativo estava lá, a mídia não: refeita, sem trocar nada que existia
