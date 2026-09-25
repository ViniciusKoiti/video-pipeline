"""Adapter Kokoro-82M local (Apache-2.0, §7). Importa kokoro/torch só no primeiro uso (extra `tts`).

Glossário de pronúncia (§9) usa a sintaxe de fonemas do Kokoro: `[Greely](/ɡɹˈili/)`. Leitura do
`voice/glossary.json` por episódio fica para a etapa 15.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from app.providers.base import ProviderInfo
from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest, SpeechResult

REPO_ID = "hexgrad/Kokoro-82M"
SAMPLE_RATE = 24_000


def apply_lexicon(text: str, lexicon: Mapping[str, str]) -> str:
    """Troca termos do glossário pelos fonemas numa passada só; termos mais longos têm prioridade."""
    if not lexicon:
        return text
    terms = sorted(lexicon, key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, terms)) + r")(?!\w)")
    return pattern.sub(lambda match: f"[{match[1]}](/{lexicon[match[1]]}/)", text)


class KokoroTTS:
    def __init__(self, voice: str, *, num_threads: int = 8, lang_code: str = "a") -> None:
        self.info = ProviderInfo("kokoro", remote=False)
        self._voice = voice
        self._num_threads = num_threads  # 8 = núcleos físicos (ADR 004)
        self._lang_code = lang_code  # "a" = inglês americano
        self._pipeline: Any = None

    def _load(self) -> Any:
        if self._pipeline is None:
            try:
                import torch
                from kokoro import KPipeline
            except ImportError as error:
                raise ModelUnavailable(self.info.name, "extra 'tts' ausente (uv sync --extra tts)") from error
            torch.set_num_threads(self._num_threads)
            self._pipeline = KPipeline(lang_code=self._lang_code, repo_id=REPO_ID)
        return self._pipeline

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        import numpy as np
        import soundfile as sf

        voice = request.voice or self._voice
        pipeline = self._load()
        text = apply_lexicon(request.text, request.lexicon)
        chunks = [audio for _, _, audio in pipeline(text, voice=voice)]
        if not chunks:
            raise ProviderError(self.info.name, "nenhum áudio gerado para o texto")
        request.out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(request.out_path, np.concatenate(chunks), SAMPLE_RATE)
        return SpeechResult(path=request.out_path, model=REPO_ID, voice=voice)
