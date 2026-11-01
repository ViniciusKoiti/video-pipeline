from __future__ import annotations

from enum import StrEnum


class Step(StrEnum):
    FORMAT = "format"  # modalidade do vídeo, recomendada por app.pipeline.format_decision (ADR 001)
    SOURCES = "sources"
    SCRIPT = "script"
    SCENES = "scenes"
    ASSETS = "assets"
    VOICE = "voice"
    SUBS = "subs"
    TRANSLATION = "translation"  # tradução em pasta própria, derivada de outro episódio (ADR 034)
    PREVIEW = "preview"
    EXPORT = "export"
