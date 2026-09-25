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
