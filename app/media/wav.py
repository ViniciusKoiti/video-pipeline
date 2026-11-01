"""Conferência barata de um WAV gerado (RF3): vale para qualquer voz, antes do ffprobe medir a duração."""

from __future__ import annotations

from pathlib import Path

from app.media.constants.wav_constants import WavConstants


def wav_is_valid(path: Path) -> bool:
    """Cabeçalho RIFF/WAVE e algum dado depois dele. Não mede a duração (isso é do ffprobe)."""
    try:
        with path.open("rb") as stream:
            head = stream.read(12)
        has_data = path.stat().st_size > WavConstants.HEADER_BYTES
        return head[:4] == b"RIFF" and head[8:12] == b"WAVE" and has_data
    except OSError:
        return False
