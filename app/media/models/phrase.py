from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Phrase:
    text: str
    pause_after: bool = False  # termina numa marca `<short pause>`
