"""Adapter Kokoro-82M local (Apache-2.0, §7). Importa kokoro/torch só no primeiro uso (extra `tts`).

Glossário de pronúncia (§9) usa a sintaxe de fonemas do Kokoro: `[Greely](/ɡɹˈili/)`. Leitura do
`voice/glossary.json` por episódio fica para a etapa 15.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING

from app.providers.tts.constants.kokoro_constants import KokoroConstants

if TYPE_CHECKING:
    from kokoro import KPipeline
    from torch import Tensor

from app.media.narration import has_pauses, split_pauses
from app.providers.base import ProviderInfo
from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest, SpeechResult
from app.providers.tts.files import atomic_wav


def apply_lexicon(text: str, lexicon: Mapping[str, str]) -> str:
    """Troca termos do glossário pelos fonemas numa passada só; termos mais longos têm prioridade."""
    if not lexicon:
        return text
    terms = sorted(lexicon, key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, terms)) + r")(?!\w)")
    return pattern.sub(lambda match: f"[{match[1]}](/{lexicon[match[1]]}/)", text)


class KokoroTTS:
    identity = KokoroConstants.IDENTITY  # `info.name` é só o nome de exibição

    def __init__(self, voices: Mapping[str, str], *, num_threads: int = 8, pause_ms: int = 300) -> None:
        self.info = ProviderInfo("kokoro", remote=False)
        self._voices = dict(voices)  # idioma -> voz (ex.: {"en": "am_michael", "pt-BR": "pm_alex"})
        self._num_threads = num_threads  # 8 = núcleos físicos (ADR 004)
        self._pause_ms = pause_ms  # silêncio no lugar de cada `<short pause>` da narração (ADR 015)
        self._pipelines: dict[str, KPipeline] = {}

    def voice_for(self, request: SpeechRequest) -> tuple[str, str]:
        """(código do KPipeline, voz) do pedido; idioma sem voz configurada é erro do provedor."""
        lang_code = KokoroConstants.LANG_CODES.get(request.language)
        voice = request.voice or self._voices.get(request.language)
        if lang_code is None or voice is None:
            raise ModelUnavailable(self.info.name, f"sem voz configurada para o idioma {request.language!r}")
        return lang_code, voice

    def fingerprint(self, request: SpeechRequest) -> str:
        """`kokoro|<voz>`, mais `|pausa<ms>` quando o texto tem pausa e `|lexico<hash>` quando o pedido traz
        glossário de fonemas (o único jeito de o Kokoro ler o termo de outra forma)."""
        _, voice = self.voice_for(request)
        pause = f"|pausa{self._pause_ms}" if has_pauses(request.text) else ""
        terms = sorted(request.lexicon.items())
        lexicon = f"|lexico{hashlib.sha256(repr(terms).encode()).hexdigest()[:8]}" if terms else ""
        return f"{self.identity}|{voice}{pause}{lexicon}"

    def _load(self, lang_code: str) -> KPipeline:
        if lang_code not in self._pipelines:
            try:
                import torch
                from kokoro import KPipeline
            except ImportError as error:
                raise ModelUnavailable(self.info.name, "extra 'tts' ausente (uv sync --extra tts)") from error
            torch.set_num_threads(self._num_threads)
            self._pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id=KokoroConstants.REPO_ID)
        return self._pipelines[lang_code]

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        import numpy as np
        import soundfile as sf

        lang_code, voice = self.voice_for(request)
        pipeline = self._load(lang_code)
        # O Kokoro não tem tags: divide em cada `<short pause>` e separa os pedaços por silêncio.
        silence = np.zeros(round(KokoroConstants.SAMPLE_RATE * self._pause_ms / 1000), dtype=np.float32)
        chunks: list[np.ndarray | Tensor] = []
        for i, part in enumerate(split_pauses(request.text) or [request.text]):
            if i:
                chunks.append(silence)
            text = apply_lexicon(part, request.lexicon)
            chunks += [audio for result in pipeline(text, voice=voice) if (audio := result[2]) is not None]
        if not chunks:
            raise ProviderError(self.info.name, "nenhum áudio gerado para o texto")
        with atomic_wav(request.out_path, self.info.name) as partial:
            sf.write(partial, np.concatenate(chunks), KokoroConstants.SAMPLE_RATE, format="WAV")
        return SpeechResult(path=request.out_path, model=KokoroConstants.REPO_ID, voice=voice)
