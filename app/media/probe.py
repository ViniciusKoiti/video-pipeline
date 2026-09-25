"""ffprobe: duração real de mídia. O timing das cenas vem daqui, nunca de estimativa (§9)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class ProbeError(RuntimeError):
    pass


def duration_ms(path: Path) -> int:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProbeError(f"ffprobe falhou em {path.name}: {result.stderr.strip()[:200]}")
    try:
        return round(float(json.loads(result.stdout)["format"]["duration"]) * 1000)
    except (KeyError, ValueError) as error:
        raise ProbeError(f"ffprobe sem duração para {path.name}") from error


def dimensions(path: Path) -> tuple[int, int]:
    """Largura e altura da primeira trilha de vídeo (ou imagem)."""
    streams = probe_streams(path)
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        raise ProbeError(f"sem trilha de vídeo em {path.name}")
    return int(video["width"]), int(video["height"])


def probe_streams(path: Path) -> list[dict[str, object]]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProbeError(f"ffprobe falhou em {path.name}: {result.stderr.strip()[:200]}")
    return list(json.loads(result.stdout).get("streams", []))
