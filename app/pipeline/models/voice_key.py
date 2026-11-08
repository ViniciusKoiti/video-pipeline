from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.pipeline.constants.voice_constants import VoiceConstants
from app.pipeline.models.naming import Naming


@dataclass(frozen=True)
class VoiceKey:
    """O que decide o nome do WAV: tudo o que, se mudar, pede fala nova."""

    line_id: str
    provider: str  # a identidade do cache do TTS (`TTSProvider.identity`), não o nome de exibição
    language: str
    fingerprint: str  # o que muda a fala além do texto, já no formato do `Naming` da biblioteca
    spoken: str  # o texto que a voz lê (glossário aplicado)

    @property
    def digest(self) -> str:
        raw = f"{self.fingerprint}|{self.spoken}".encode()
        return hashlib.sha256(raw).hexdigest()[: VoiceConstants.DIGEST_CHARS]

    def stem(self, naming: Naming) -> str:
        """A parte do nome antes do hash: o que identifica as versões da mesma fala."""
        if naming is Naming.SHORT:
            return f"{self.line_id}-{self.provider}-{self.language.lower().replace('-', '')}"
        return f"{self.line_id}-{self.provider}"

    def file_name(self, naming: Naming) -> str:
        return f"{self.stem(naming)}-{self.digest}.wav"
