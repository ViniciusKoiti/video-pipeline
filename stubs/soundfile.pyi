from pathlib import Path

from numpy import _ArrayLike

def write(file: str | Path, data: _ArrayLike, samplerate: int, *, format: str | None = None) -> None: ...
