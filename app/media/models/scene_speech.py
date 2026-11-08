from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SceneSpeech:
    id: str
    audio: str  # caminho do WAV no episode.json; muda quando o texto ou a voz mudam
    narration: str
    duration_ms: int
