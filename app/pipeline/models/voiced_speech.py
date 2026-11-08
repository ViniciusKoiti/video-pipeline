from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VoicedSpeech:
    """A fala de uma cena: o WAV e o trecho falado dentro dele, em segundos desde o começo do arquivo."""

    wav: Path
    begin: float
    end: float

    @property
    def seconds(self) -> float:
        return self.end - self.begin
