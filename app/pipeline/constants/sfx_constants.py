"""Constantes de sfx; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class SfxConstants:
    MAX_GAIN_DB: Final[float] = 6.0
    # prefixo do `avoid_for` dos sons que cobrem a voz
    COVERS_SPEECH: Final[str] = "On top of speech"
    # em data/: o kit clonado em kit/
    SFX_DIR: Final[str] = "sfx"
    KIT_DIR: Final[str] = "kit"
    KIT_INDEX: Final[str] = "sounds.json"
    # na pasta do vídeo
    SFX_PLAN_FILE: Final[str] = "sfx.json"
    # o kit foi nivelado para uma voz a −16 LUFS (GUIDE.md, §3)
    KIT_VOICE_REFERENCE_LUFS: Final = -16.0
    # acima disso é ruído, não acabamento
    MAX_CUES_PER_10S: Final[int] = 8
    # arredondamento do kit: o fim do corpo e o ponto de sincronia podem passar da duração por esse tanto
    TIME_SLACK_S: Final[float] = 1e-6
