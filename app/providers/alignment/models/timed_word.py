from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimedWord:
    """Uma palavra reconhecida no áudio, com o tempo em ms do arquivo. O texto é o do reconhecedor, não o do
    roteiro: quem usa casa os dois (`app.media.word_captions`)."""

    text: str
    start_ms: int
    end_ms: int
