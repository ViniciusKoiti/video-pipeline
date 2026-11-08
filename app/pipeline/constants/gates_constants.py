"""Constantes de gates; dados fixos sem I/O."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from app.pipeline.schemas import Step


class GatesConstants:
    GATE_FILES: Final[Mapping[Step, tuple[str, ...]]] = MappingProxyType(
        {Step.SOURCES: ("sources.json", "facts.json"), Step.SCRIPT: ("scenes.json", "outline.md")}
    )
    # o gate 4 revê o mais acabado
    RENDERS: Final = ("renders/final.mp4", "renders/preview.mp4")
    # entram no gate 4 quando existem
    PREVIEW_FILES: Final = ("episode.json", "captions.srt", "legenda-post.txt")
    # faixas da trilha, aprovadas no gate 3 (ADR 030)
    AUDIO_SUFFIXES: Final = (".mp3", ".m4a", ".wav", ".ogg")
    CHECK_FILE: Final[str] = "checagem.json"
    # o que o verificador confere contra os trechos
    CHECKED_FILES: Final = ("facts.json", "scenes.json", "outline.md")
    # a imagem escolhida para o plano
    ASSET_ID: Final = re.compile(b'("asset_id"\\s*:\\s*)"(?:[^"\\\\]|\\\\.)*"')
    GATED_STEPS: Final = (*GATE_FILES, Step.ASSETS, Step.TRANSLATION, Step.PREVIEW)
    MEDIA_SUFFIXES: Final = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm", *AUDIO_SUFFIXES)
