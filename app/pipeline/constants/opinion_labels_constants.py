"""Constantes de opinion_labels; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class OpinionLabelsConstants:
    # Rótulo que anuncia a opinião em vez de dizê-la, no texto sem acento e em minúsculas (pt-BR e inglês).
    # "Na minha opinião" e "na minha leitura" são fala natural e passam.
    PHRASES: Final = (
        r"\bcomo (?:uma |minha )?opiniao\b(?! public)",
        r"\bisso (?:e|eh) (?:so |apenas )?(?:uma |a |minha )?opiniao\b",
        r"\b(?:e|eh) (?:so |apenas )?(?:uma )?opiniao (?:minha|pessoal|do canal)\b",
        r"\ba titulo de opiniao\b",
        r"\bem carater de opiniao\b",
        r"\bopiniao do canal\b",
        r"\bas (?:an |my )?opinion\b",
        r"\bthis is (?:just |only )?(?:an |my )?opinion\b",
    )
    # o que a mensagem de erro sugere no lugar
    INSTEAD: Final[str] = '"na minha leitura", "pelo menos é assim que eu enxergo", "eu acho"'
