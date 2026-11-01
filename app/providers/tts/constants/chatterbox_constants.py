"""Constantes de chatterbox; dados fixos sem I/O."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping


class ChatterboxConstants:
    WORKER: Final = Path(__file__).parent.parent / "chatterbox_worker.py"
    MODAL_CLIENT: Final = Path(__file__).parent.parent / "chatterbox_modal_client.py"
    MODEL_PREFIX: Final[str] = "chatterbox-multilingual-"
    MAX_PART_CHARS: Final[int] = 300
    SENTENCE_GAP_MS: Final[int] = 150
    # Versão do corte e da junção da fala longa. Entra na identidade do cache só acima de 1 (as falas de hoje
    # seguem com o mesmo nome); subir o número ao mudar o algoritmo regenera as falas afetadas (ADR 041).
    SPEECH_VERSION: Final[int] = 1
    # exaggeration e cfg_weight que o modelo usa quando a entrega não os define
    NEUTRAL_DEFAULT: Final = (0.5, 0.5)
    _SENTENCE_END: Final = re.compile('(?<=[.!?…])\\s+|(?<=[.!?…][”\\"’)])\\s+')
    _CLAUSE_END: Final = re.compile("(?<=[,;:])\\s+")
    DEFAULT_DELIVERY: Final[Mapping[str, Mapping[str, float]]] = MappingProxyType(
        {
            "hook": MappingProxyType({"exaggeration": 0.8, "cfg_weight": 0.3}),
            "turn": MappingProxyType({"exaggeration": 0.7, "cfg_weight": 0.4}),
            "invite": MappingProxyType({"exaggeration": 0.6, "cfg_weight": 0.4}),
            "neutral": MappingProxyType({"exaggeration": 0.5, "cfg_weight": 0.5}),
            "calm": MappingProxyType({"exaggeration": 0.4, "cfg_weight": 0.6}),
        }
    )
