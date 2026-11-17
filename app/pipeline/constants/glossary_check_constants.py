"""Constantes de glossary_check; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class GlossaryCheckConstants:
    # Sigla: duas letras maiúsculas ou mais (com algarismo no meio, como "MP3").
    ACRONYM: Final[str] = r"^[A-Z][A-Z0-9]*[A-Z][A-Z0-9]*$"
    # Traços que quase não existem em palavra do português: letras, encontros e letra dobrada (fora rr e ss).
    FOREIGN_PATTERNS: Final = (r"[wyk]", r"th|sh|ph|ck|tz|gh|sch", r"([b-df-hj-np-qtv-z])\1")
    # Letras com que uma palavra do português termina; outra no fim é traço de palavra de fora.
    NATIVE_FINALS: Final = frozenset("aeiouáéíóúâêôãõàlmnrsxz")
    # Palavra da narração: começa por letra (não por "º"/"ª") e termina em letra ou algarismo, sem a aspa
    # simples colada ("'bom'" vira "bom").
    WORD: Final[str] = r"[^\W\d_ºª](?:[\w']*\w)?"
    # Palavras do português com um traço de palavra de fora (fim em "b", "zz"); achadas na varredura dos 48
    # roteiros de data/episodes em 2026-11-17.
    NATIVE_WORDS: Final = frozenset(("sob", "pizza", "pizzas", "pizzaria", "pizzarias"))
    VOICES_WITH_IPA: Final = frozenset(("azure_speech",))
    LANGUAGE: Final[str] = "pt-BR"  # só a narração em português; a inglesa tem outra noção de "de fora"
    # Dois-pontos que abrem uma pergunta ou fala interna, sem `<short pause>` logo depois (a voz cola as
    # palavras).
    COLON_QUESTION: Final[str] = r":(?!\s*<short pause>)[^.:!]*\?"
