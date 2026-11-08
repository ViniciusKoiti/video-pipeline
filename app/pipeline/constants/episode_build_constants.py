"""Constantes da montagem do `episode.json`; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class EpisodeBuildConstants:
    # extensões aceitas para a mídia de um plano de foto ou B-roll e para a faixa da trilha, em `assets/`
    MEDIA_SUFFIXES: Final = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")
    MUSIC_SUFFIXES: Final = (".mp3", ".m4a", ".wav", ".ogg")
    # o `episode.json` é um rascunho até o gate 4: o título carrega o aviso
    DRAFT_TITLE: Final[str] = "{episode_id} (rascunho)"
