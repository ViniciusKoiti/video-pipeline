"""Constantes da cadência das pausas (`voice/cadencia.json`); dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class VoicePacingConstants:
    # com o arquivo, a cadência entra; sem ele, a fala fica como a voz deu
    FILE: Final = "voice/cadencia.json"
    DIRECTORY: Final = "paced"  # cópias em voice/paced/, o WAV bruto (e o nivelado) ficam como estão
    VERSION: Final = 1
    REASON: Final = "pacing_failed"
    DIGEST_CHARS: Final = 10
    # silêncio é o que fica abaixo de -40 dB por pelo menos 0,12 s (as vírgulas do Azure dão ~0,2 s)
    NOISE_DB: Final = -40
    MIN_SILENCE_S: Final = 0.12
    # um silêncio que começa (ou termina) a menos de 20 ms da ponta do arquivo é o da ponta
    EDGE_S: Final = 0.02
    # dentro da cena, só um silêncio desta duração para cima é fim de frase (o Azure dá ~0,9 s no ponto,
    # 0,5 s na `<short pause>` e até 0,4 s na vírgula); se a contagem não bater com o texto, ficam como estão
    SENTENCE_SILENCE_S: Final = 0.65
    # o que se mantém da fala em volta de cada silêncio cortado (o fim da última sílaba e o ataque da próxima)
    MARGIN_S: Final = 0.06
    # todo WAV começa com exatamente este silêncio antes da fala: o intervalo entre cenas fica previsível
    HEAD_S: Final = 0.05
    # fim de frase: ponto, interrogação, exclamação ou reticências, seguido de espaço e de nova frase
    SENTENCE_SPLIT: Final = re.compile(r"(?<=[.?!…])[\"”»)]?\s+(?=\S)")
    QUESTION_END: Final = re.compile(r"\?[\"”»)]?\s*$")
    # a frase seguinte continua a anterior quando começa por um destes conectivos (pt-BR e inglês)
    CONTINUATIONS: Final = (
        ("e",), ("mas",), ("só", "que"), ("porque",), ("pois",), ("aí",), ("ou",), ("nem",),
        ("and",), ("but",), ("or",), ("because",),
    )
    # a frase seguinte fecha um raciocínio quando começa por um destes (respiro maior antes dela)
    CONCLUSIONS: Final = (("então",), ("no", "fim"), ("resumindo",), ("so",), ("in", "the", "end"))
    # a entrega da cena seguinte que pede respiro maior antes dela (ADR 022)
    TURN_DELIVERIES: Final = frozenset(("turn", "invite"))
    WORD: Final = re.compile(r"[\wÀ-ÿ]+")
