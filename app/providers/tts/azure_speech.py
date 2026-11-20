"""Adapter Azure Speech (voz neural pronta, ADR 058): REST por SSML, uma fala por chamada, só na camada F0.

- `POST https://<região>.tts.speech.microsoft.com/cognitiveservices/v1`, corpo SSML, resposta WAV PCM
  (`riff-24khz-16bit-mono-pcm`), gravada como veio.
- A chave vai só no cabeçalho `Ocp-Apim-Subscription-Key` e nunca aparece em erro nem em log (§2.7).
- Custo zero (§2.1): o adapter não tem como ver a camada do recurso pela chave; ela é declarada em
  `[azure_speech] tier`. Fora de `F0` o provedor declara custo e o `ensure_free` o recusa.
- A F0 aceita 20 chamadas por 60 s: o adapter espaça as chamadas. Falha passageira (429, 500, 502, 503,
  tempo esgotado ou rede) espera o intervalo e tenta de novo uma vez; o segundo 429 vira `QuotaExhausted`
  (a cena fica pendente e as chamadas param). Nunca troca de voz sozinho.
- O texto é escapado para XML; cada `<short pause>` (ADR 015) vira `<break time="…ms"/>`.
- A entrega por cena (ADR 022) muda só a velocidade (emenda de 2026-11-16 da ADR 058): o fator da entrega
  (`[azure_speech.delivery]`) multiplica `rate`; entrega sem fator fala em `rate`. A velocidade efetiva entra
  na identidade, então a cena neutra com fator 1 guarda o nome de antes.
- Fonemas (emenda de 2026-11-15 da ADR 058): o `lexicon` do pedido (grafia -> IPA da tabela do pt-BR) vira
  `<phoneme alphabet="ipa" ph="…">grafia</phoneme>` em cada ocorrência da palavra inteira; fonema fora da
  tabela volta como HTTP 400 e a cena fica pendente. Só os termos presentes no texto entram na identidade.
  Com `ipa=False` (voz MAI, ADR 063) o adapter não se declara de fonemas e recebe o texto já com a `fala` do
  glossário, porque o `<phoneme>` estica a palavra nessas vozes.
- Marcas de emoção (ADR 063): cada trecho marcado vira `<mstts:express-as style="…">` pela tabela `styles`
  (marca -> estilo); marca sem estilo na tabela fala como o resto. Texto sem marca gera o SSML de antes, e só
  os estilos usados no texto entram na identidade.
"""

from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Callable, Mapping
from xml.sax.saxutils import escape, quoteattr

from app.media.narration import emotion_segments, has_pauses, split_pauses
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.http import BytesPost, TransportError, post_bytes
from app.providers.tts.base import SpeechRequest, SpeechResult
from app.providers.tts.constants.azure_speech_constants import AzureSpeechConstants
from app.providers.tts.files import atomic_wav


def _used(text: str, lexicon: Mapping[str, str]) -> list[tuple[str, str]]:
    """Os termos do glossário de fonemas que aparecem no texto como palavra inteira, em ordem estável."""
    return sorted((t, ipa) for t, ipa in lexicon.items() if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", text))


def _phonemes(part: str, lexicon: Mapping[str, str]) -> str:
    """O trecho já escapado, com cada termo do glossário (palavra inteira) dentro de `<phoneme>`."""
    if not lexicon:
        return part
    escaped = {escape(term, AzureSpeechConstants.XML_ENTITIES): ipa for term, ipa in lexicon.items()}
    alphabet = AzureSpeechConstants.PHONEME_ALPHABET
    pattern = "|".join(re.escape(term) for term in sorted(escaped, key=len, reverse=True))
    return re.sub(
        rf"(?<!\w)({pattern})(?!\w)",
        lambda m: f'<phoneme alphabet="{alphabet}" ph={quoteattr(escaped[m[1]])}>{m[1]}</phoneme>',
        part,
    )


def _used_styles(text: str, styles: Mapping[str, str]) -> list[tuple[str, str]]:
    """As marcas de emoção do texto que têm estilo na tabela, em ordem estável."""
    return sorted({(name, styles[name]) for name, _ in emotion_segments(text) if name and name in styles})


def ssml(
    text: str, *, language: str, voice: str, rate: float, pause_ms: int,
    lexicon: Mapping[str, str] | None = None, styles: Mapping[str, str] | None = None,
) -> str:
    """O documento SSML de uma fala: texto escapado, termos do glossário de fonemas em `<phoneme>`, pausas
    como `<break>`, velocidade só se não for 1 e, por trecho marcado, o estilo da emoção (ADR 063)."""
    entities = AzureSpeechConstants.XML_ENTITIES
    pieces = []
    for emotion, segment in emotion_segments(text):
        parts = [_phonemes(escape(part, entities), lexicon or {}) for part in split_pauses(segment)]
        body = f'<break time="{pause_ms}ms"/>'.join(parts)
        if not body:
            continue
        if rate != 1.0:
            body = f'<prosody rate="{rate:g}">{body}</prosody>'
        style = (styles or {}).get(emotion) if emotion else None
        styled = f"<mstts:express-as style={quoteattr(style)}>{body}</mstts:express-as>" if style else body
        pieces.append(styled)
    body = " ".join(pieces)
    mstts = f' xmlns:mstts="{AzureSpeechConstants.MSTTS_NAMESPACE}"' if "<mstts:" in body else ""
    return (
        f'<speak version="1.0" xmlns="{AzureSpeechConstants.SSML_NAMESPACE}"{mstts} '
        f"xml:lang={quoteattr(language)}>"
        f"<voice name={quoteattr(voice)}>{body}</voice></speak>"
    )


class AzureSpeechTTS:
    identity = AzureSpeechConstants.IDENTITY
    phoneme_alphabet = AzureSpeechConstants.PHONEME_ALPHABET  # aceita o glossário de fonemas (`PhonemeTTS`)

    def __init__(
        self,
        api_key: str,
        region: str,
        *,
        voices: Mapping[str, str],
        output_format: str,
        rate: float = 1.0,
        delivery_rates: Mapping[str, float] | None = None,
        pause_ms: int = 500,
        requests_per_minute: int = 20,
        tier: str = AzureSpeechConstants.FREE_TIER,
        styles: Mapping[str, str] | None = None,
        ipa: bool = True,
        post: BytesPost = post_bytes,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        paid = tier != AzureSpeechConstants.FREE_TIER
        cost = AzureSpeechConstants.PAID_USD_PER_CALL if paid else 0.0
        self.info = ProviderInfo("azure_speech", remote=True, usd_per_call=cost)
        self._key = api_key
        self._url = AzureSpeechConstants.API.format(region=region)
        self._voices = dict(voices)  # idioma -> voz (ex.: {"pt-BR": "pt-BR-AntonioNeural"})
        self._format = output_format
        self._rate = rate
        self._delivery_rates = dict(delivery_rates or {})  # entrega -> fator sobre `rate` (ADR 022)
        self._pause_ms = pause_ms
        self._styles = dict(styles or {})  # marca de emoção -> estilo do express-as (ADR 063)
        if not ipa:  # voz MAI: o glossário chega como `fala` no texto, sem `<phoneme>` (ADR 063)
            self.phoneme_alphabet = ""
        self._interval = 60 / requests_per_minute + AzureSpeechConstants.MARGIN_S
        self._post = post
        self._clock = clock
        self._sleep = sleep
        self._last_call: float | None = None

    def voice_for(self, request: SpeechRequest) -> str:
        voice = request.voice or self._voices.get(request.language)
        if voice is None:
            raise ModelUnavailable(self.info.name, f"sem voz configurada para o idioma {request.language!r}")
        return voice

    def rate_for(self, request: SpeechRequest) -> float:
        """A velocidade da fala: `rate` vezes o fator da entrega da cena (1 sem fator), com 3 casas."""
        effective = round(self._rate * self._delivery_rates.get(request.delivery, 1.0), 3)
        low, high = AzureSpeechConstants.RATE_RANGE
        if not low <= effective <= high:
            message = f"velocidade {effective:g} fora de {low:g} a {high:g} ({request.delivery})"
            raise ProviderError(self.info.name, message)
        return effective

    def fingerprint(self, request: SpeechRequest) -> str:
        """`azure_speech|<voz>|<formato>`, mais `|rate<v>` quando a velocidade não é 1, `|pausa<ms>` quando
        o texto tem pausa, `|ipa<hash>` quando um termo do glossário de fonemas aparece no texto e
        `|estilos<hash>` quando uma marca de emoção do texto tem estilo na tabela."""
        voice = self._check(request)
        effective = self.rate_for(request)
        rate = f"|rate{effective:g}" if effective != 1.0 else ""
        pause = f"|pausa{self._pause_ms}" if has_pauses(request.text) else ""
        used = _used(request.text, request.lexicon)
        ipa = f"|ipa{hashlib.sha256(repr(used).encode()).hexdigest()[:8]}" if used else ""
        styled = _used_styles(request.text, self._styles)
        styles = f"|estilos{hashlib.sha256(repr(styled).encode()).hexdigest()[:8]}" if styled else ""
        return f"{self.identity}|{voice}|{self._format}{rate}{pause}{ipa}{styles}"

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        voice = self._check(request)
        if not split_pauses(request.text):
            raise ProviderError(self.info.name, "nenhum texto para falar")
        if len(request.text) > AzureSpeechConstants.MAX_TEXT_CHARS:
            limit = AzureSpeechConstants.MAX_TEXT_CHARS
            raise ProviderError(self.info.name, f"fala com mais de {limit} caracteres; divida a cena")
        document = ssml(
            request.text, language=request.language, voice=voice, rate=self.rate_for(request),
            pause_ms=self._pause_ms,
            lexicon=dict(_used(request.text, request.lexicon)), styles=self._styles,
        )
        audio = self._call(document.encode("utf-8"))
        if audio[:4] != b"RIFF":
            raise InvalidOutput(self.info.name, "áudio sem cabeçalho WAV")
        with atomic_wav(request.out_path, self.info.name) as partial:
            partial.write_bytes(audio)
        return SpeechResult(path=request.out_path, model=AzureSpeechConstants.MODEL, voice=voice)

    def _check(self, request: SpeechRequest) -> str:
        return self.voice_for(request)

    def _call(self, body: bytes) -> bytes:
        headers = {
            AzureSpeechConstants.KEY_HEADER: self._key,
            "Content-Type": AzureSpeechConstants.CONTENT_TYPE,
            AzureSpeechConstants.FORMAT_HEADER: self._format,
        }
        for attempt in (1, 2):
            self._wait()
            try:
                return self._post(self._url, body, headers, AzureSpeechConstants.TIMEOUT_S)
            except TransportError as error:
                passing = error.status is None or error.status in AzureSpeechConstants.TRANSIENT
                if attempt == 1 and passing:
                    continue  # limite por minuto, serviço ocupado ou rede: espera e tenta uma vez mais
                detail = str(error).replace(self._key, "***")  # a chave nunca sai num erro (§2.7)
                if error.status == 429:
                    message = f"limite ou cota da camada gratuita (F0) esgotados: {detail}"
                    raise QuotaExhausted(self.info.name, message) from None
                if error.status in AzureSpeechConstants.REFUSED:
                    message = (
                        f"chave ou região recusada (HTTP {error.status}); "
                        "confira AZURE_SPEECH_KEY e AZURE_SPEECH_REGION no .env"
                    )
                    raise ProviderError(self.info.name, message) from None
                raise ProviderError(self.info.name, detail) from None
        raise AssertionError("inalcançável")

    def _wait(self) -> None:
        now = self._clock()
        if self._last_call is not None:
            remaining = self._interval - (now - self._last_call)
            if remaining > 0:
                self._sleep(remaining)
                now += remaining
        self._last_call = now
