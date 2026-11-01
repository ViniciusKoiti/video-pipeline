"""Constantes de molde; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class MoldeConstants:
    MOLDE_FILE: Final[str] = "molde.json"
    PARTITURA_FILE: Final[str] = "partitura.md"
    # a abertura que o molde mede em `cortes_60s` e `voce_60s`
    OPENING_S: Final[float] = 60.0
    # a duração estimada pode ficar 20% longe da que a partitura pede
    DURATION_TOLERANCE: Final[float] = 0.2
    # planos por minuto acima do dobro do molde viram alerta
    CUT_RATIO: Final[float] = 2.0
    # o molde "sobe" uma palavra no fecho quando o último décimo tem 30% a mais que o corpo
    CLOSING_RISE: Final[float] = 1.3
    # abaixo disso o molde é descrição, e o alerta diz isso
    MIN_VIDEOS: Final[int] = 8
    # frase curta sem claims (ponte, pergunta retórica) não é afirmação de fato
    STATEMENT_MIN_WORDS: Final[int] = 6
    # palavra de conteúdo do título: 4 letras ou mais, fora de TITLE_STOP
    TITLE_MIN_LETTERS: Final[int] = 4
    TITLE_STOP: Final = frozenset(
        (
            "como",
            "para",
            "pelo",
            "pela",
            "pelos",
            "pelas",
            "você",
            "voce",
            "vocês",
            "voces",
            "isso",
            "isto",
            "esse",
            "essa",
            "este",
            "esta",
            "aquele",
            "aquela",
            "mais",
            "menos",
            "muito",
            "tudo",
            "nada",
            "quando",
            "onde",
            "porque",
            "então",
            "ainda",
            "sobre",
            "entre",
            "até",
            "depois",
            "antes",
            "mesmo",
            "cada",
            "sempre",
            "nunca",
            "quem",
            "qual",
            "quais",
            "coisa",
            "coisas",
            "vídeo",
            "video",
            "parte",
            "episódio",
            "episodio",
            "minutos",
            "pode",
            "podem",
            "deve",
            "devem",
            "está",
            "estão",
            "foram",
            "sendo",
            "tinha",
            "teria",
            "fazer",
            "ouvir",
            "enquanto",
            "outra",
            "outro",
            "outras",
            "outros",
            "também",
            "assim",
            "aqui",
            "agora",
            "hoje",
            "anos",
            "todo",
            "toda",
            "todos",
            "todas",
            "primeiro",
            "primeira",
            "deveria",
            "devia",
            "deviam",
            "estava",
            "estavam",
            "gente",
            "certo",
            "certa",
            "nosso",
            "nossa",
            "ninguém",
            "ninguem",
            "alguém",
            "alguem",
        )
    )
    _VOCE: Final = re.compile("\\bvoc[êe]s?\\b", re.IGNORECASE)
    _EU: Final = re.compile("\\beu\\b", re.IGNORECASE)
    _CONFISSAO: Final = re.compile(
        (
            "\\beu (vou )?(admitir|admito|confesso|confessar)\\b|\\beu "
            "(acreditei|achava|errei|errava)\\b|\\bvergonha\\b|\\beu (ia|tinha) "
            "(come[çc]ar|escrito)\\b|\\bestava escrito aqui\\b"
        ),
        re.IGNORECASE,
    )
    _SENTENCE_END: Final = re.compile("(?<=[.?!…])\\s+")
    _WORD: Final = re.compile("\\w+", re.UNICODE)
    _FIRST_PERSON: Final = re.compile(
        "^(eu\\b|pra mim|para mim|acho|na minha|confesso|admito|a meu ver)", re.IGNORECASE
    )
    _STOP: Final = frozenset(
        (
            "a",
            "o",
            "e",
            "de",
            "do",
            "da",
            "que",
            "em",
            "um",
            "uma",
            "para",
            "com",
            "não",
            "por",
            "se",
            "os",
            "as",
            "no",
            "na",
            "é",
            "mais",
            "você",
            "vocês",
            "ele",
            "ela",
            "isso",
            "esse",
            "essa",
            "aqui",
            "ali",
            "lá",
            "já",
            "tá",
            "pra",
            "pro",
            "dos",
            "das",
            "ao",
            "à",
            "como",
            "mas",
            "ou",
            "também",
            "muito",
            "tudo",
            "nada",
            "ser",
            "foi",
            "era",
            "tem",
            "tinha",
            "vai",
            "vou",
            "eu",
            "nós",
            "gente",
            "quando",
            "onde",
            "porque",
            "então",
            "ainda",
            "sobre",
            "entre",
            "até",
            "depois",
            "antes",
            "mesmo",
            "cada",
            "bem",
            "só",
        )
    )
