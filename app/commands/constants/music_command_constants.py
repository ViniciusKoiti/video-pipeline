"""Constantes do comando `vp music`; dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from app.pipeline.models.track_install_action import TrackInstallAction


class MusicCommandConstants:
    # o que o `usar` diz de cada resultado da instalação da faixa
    ACTIONS: Final = MappingProxyType(
        {
            TrackInstallAction.INSTALLED: "faixa e ativo copiados para assets/ do episódio",
            TrackInstallAction.UNCHANGED: "já está no episódio",
            TrackInstallAction.REPAIRED: "o ativo já estava no episódio; a mídia foi refeita",
        }
    )
