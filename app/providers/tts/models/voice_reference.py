from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VoiceReference:
    """A gravação efetivamente escolhida; o nome remoto é relativo ao volume privado."""

    path: Path
    remote_name: str | None = None

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()
