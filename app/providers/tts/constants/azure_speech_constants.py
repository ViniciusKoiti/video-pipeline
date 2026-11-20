"""Constantes de azure_speech; dados fixos sem I/O."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final


class AzureSpeechConstants:
    IDENTITY: Final[str] = "azure_speech"  # chave do cache de voz, no nome do WAV (ADR 041)
    MODEL: Final[str] = "azure-speech-neural"  # vozes neurais padrão ("Standard" na tabela de vozes)
    # endpoint regional da síntese por SSML (rest-text-to-speech, consulta de 2026-11-11)
    API: Final[str] = "https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    REGION: Final = re.compile(r"[a-z0-9]+")  # `brazilsouth`, `eastus2`: vai no nome do host
    KEY_HEADER: Final[str] = "Ocp-Apim-Subscription-Key"
    FORMAT_HEADER: Final[str] = "X-Microsoft-OutputFormat"
    CONTENT_TYPE: Final[str] = "application/ssml+xml"
    SSML_NAMESPACE: Final[str] = "http://www.w3.org/2001/10/synthesis"
    # `mstts:express-as`: o estilo por trecho das marcas de emoção (ADR 063)
    MSTTS_NAMESPACE: Final[str] = "https://www.w3.org/2001/mstts"
    FREE_TIER: Final[str] = "F0"
    # fora da F0 a síntese é cobrada por caractere: US$ 15 por milhão no exemplo da página de cotas, ~1.000
    # caracteres por cena. Só serve para o `ensure_free` recusar a camada paga (§2.1).
    PAID_USD_PER_CALL: Final[float] = 0.015
    TIMEOUT_S: Final[float] = 60.0
    # e status None: tempo esgotado ou rede (a página de cotas pede nova tentativa no 429)
    TRANSIENT: Final = frozenset((429, 500, 502, 503))
    REFUSED: Final = frozenset((401, 403))  # chave ou região erradas
    MARGIN_S: Final[float] = 0.5  # folga sobre 60 / chamadas por minuto
    # o serviço corta o áudio em 10 minutos sem avisar; uma fala deste tamanho fica bem abaixo disso
    MAX_TEXT_CHARS: Final[int] = 5000
    # aspas escapadas além de &, < e > (o texto e o atributo `ph` vão no SSML)
    XML_ENTITIES: Final = MappingProxyType({'"': "&quot;", "'": "&apos;"})
    # alfabeto do `<phoneme>` (speech-synthesis-markup-pronunciation; tabela do pt-BR em
    # speech-ssml-phonetic-sets, consulta de 2026-11-15)
    PHONEME_ALPHABET: Final[str] = "ipa"
    # velocidade efetiva aceita (rate × fator da entrega; emenda de 2026-11-16 da ADR 058): a do `prosody`
    RATE_RANGE: Final[tuple[float, float]] = (0.5, 2.0)
