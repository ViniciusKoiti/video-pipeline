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
LANG_CODES = {"en": "a", "pt-BR": "p"}  # códigos do KPipeline: inglês americano, português do Brasil


def apply_lexicon(text: str, lexicon: Mapping[str, str]) -> str:
    """Troca termos do glossário pelos fonemas numa passada só; termos mais longos têm prioridade."""
    if not lexicon:
        return text
    terms = sorted(lexicon, key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, terms)) + r")(?!\w)")
    return pattern.sub(lambda match: f"[{match[1]}](/{lexicon[match[1]]}/)", text)


class KokoroTTS:
    def __init__(self, voices: Mapping[str, str], *, num_threads: int = 8) -> None:
        self.info = ProviderInfo("kokoro", remote=False)
        self._voices = dict(voices)  # idioma -> voz (ex.: {"en": "am_michael", "pt-BR": "pm_alex"})
        self._num_threads = num_threads  # 8 = núcleos físicos (ADR 004)
        self._pipelines: dict[str, Any] = {}

    def voice_for(self, request: SpeechRequest) -> tuple[str, str]:
        """(código do KPipeline, voz) do pedido; idioma sem voz configurada é erro do provedor."""
        lang_code = LANG_CODES.get(request.language)
        voice = request.voice or self._voices.get(request.language)
        if lang_code is None or voice is None:
            raise ModelUnavailable(self.info.name, f"sem voz configurada para o idioma {request.language!r}")
        return lang_code, voice

    def _load(self, lang_code: str) -> Any:
        if lang_code not in self._pipelines:
            try:
                import torch
                from kokoro import KPipeline
            except ImportError as error:
                raise ModelUnavailable(self.info.name, "extra 'tts' ausente (uv sync --extra tts)") from error
            torch.set_num_threads(self._num_threads)
            self._pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id=REPO_ID)
        return self._pipelines[lang_code]

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        import numpy as np
        import soundfile as sf

        lang_code, voice = self.voice_for(request)
        pipeline = self._load(lang_code)
        text = apply_lexicon(request.text, request.lexicon)
        chunks = [audio for _, _, audio in pipeline(text, voice=voice)]
        if not chunks:
            raise ProviderError(self.info.name, "nenhum áudio gerado para o texto")
        request.out_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(request.out_path, np.concatenate(chunks), SAMPLE_RATE)
        return SpeechResult(path=request.out_path, model=REPO_ID, voice=voice)
