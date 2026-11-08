from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrackDraft:
    """O que o dono informa da faixa que baixou da Audio Library: a escuta (clima, voz cantada) é dele."""

    title: str
    moods: tuple[str, ...]
    vocals: bool
    license_id: str
    artist: str | None = None
    attribution: str = ""  # o texto do botão Copy, para faixa CC
    bpm: int | None = None
    loops: bool = False
