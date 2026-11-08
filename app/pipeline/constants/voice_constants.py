"""Constantes da biblioteca de falas e do narrador; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class VoiceConstants:
    # vozes clonadas: no Short, a entrega entra na chave pelo nome, no formato de hoje (ADR 049)
    CLONED: Final = ("chatterbox", "chatterbox_modal")
    NEUTRAL: Final[str] = "neutral"
    LEGACY_DELIVERY: Final[str] = "|entrega:{name}"
    # no longo, a entrega clonada de hoje é `|entrega:<nome>=<exaggeration>,<cfg_weight>` (ADR 041); o nome de
    # WAV de antes não tinha os valores, então eles saem da chave
    DELIVERY_VALUES: Final = re.compile(r"(\|entrega:[^=|]+)=[^|]*")
    # tamanho do hash no nome do WAV
    DIGEST_CHARS: Final[int] = 10
