from __future__ import annotations

import hashlib
from pathlib import Path

from app.pipeline.models.model import Model
from app.pipeline.models.sfx_sound import SfxSound


class SfxKit(Model):
    root: Path
    license: str
    sounds: dict[str, SfxSound]

    def path(self, sound: SfxSound) -> Path:
        return self.root / sound.file

    def file_problem(self, sound: SfxSound) -> str | None:
        path = self.path(sound)
        if not path.is_file():
            return f"{sound.id}: falta o arquivo {sound.file} no kit"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != sound.sha256:
            return f"{sound.id}: o arquivo não bate com o sha256 do kit"
        return None
