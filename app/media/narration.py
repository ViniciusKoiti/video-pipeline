"""Pausas dentro da narração (ADR 015): `<short pause>` no ponto exato, na própria `narration`.

O texto falado leva a marca (o Gemini a lê como pausa; o Kokoro vira silêncio); a tela, a legenda e as âncoras
dos planos usam o texto sem ela. No tempo dos planos cada marca vale `PAUSE_CHARS` caracteres, para os planos
depois de uma pausa não ficarem adiantados.
"""

from __future__ import annotations

from app.media.constants.narration_constants import NarrationConstants


def strip_pauses(text: str) -> str:
    """O texto sem as marcas: cada uma (com os espaços em volta) vira um espaço só."""
    return NarrationConstants._PAUSE.sub(" ", text)


def has_pauses(text: str) -> bool:
    return NarrationConstants.PAUSE_TAG in text


def split_pauses(text: str) -> list[str]:
    """Os trechos entre as marcas, sem vazios: o que o Kokoro sintetiza um a um."""
    return [part.strip() for part in NarrationConstants._PAUSE.split(text) if part.strip()]


def pause_positions(text: str) -> list[int]:
    """Posição de cada marca no texto sem marcas (onde começa a fala depois dela)."""
    positions, removed = [], 0
    for match in NarrationConstants._PAUSE.finditer(text):
        positions.append(match.start() - removed + 1)
        removed += (match.end() - match.start()) - 1
    return positions


def timeline_length(text: str) -> int:
    """Tamanho da fala em caracteres, com cada pausa valendo `PAUSE_CHARS`."""
    return len(strip_pauses(text)) + NarrationConstants.PAUSE_CHARS * len(pause_positions(text))


def timeline_position(text: str, plain_position: int) -> int:
    """Posição, na mesma conta, de um ponto do texto sem marcas: conta as pausas que vêm antes dele."""
    return plain_position + NarrationConstants.PAUSE_CHARS * sum(
        1 for p in pause_positions(text) if p <= plain_position
    )


def narration_problems(text: str) -> list[str]:
    """Erros das marcas: outra tag `<…>`, `<long pause>`, marca mal encaixada, no começo ou no fim."""
    problems = []
    if NarrationConstants.LONG_PAUSE_TAG in text:
        problems.append(
            f"{NarrationConstants.LONG_PAUSE_TAG} é só do lote de cenas; dentro da narração use "
            f"{NarrationConstants.PAUSE_TAG}"
        )
    others = sorted(
        {
            t
            for t in NarrationConstants._ANY_TAG.findall(text)
            if t not in (NarrationConstants.PAUSE_TAG, NarrationConstants.LONG_PAUSE_TAG)
        }
    )
    if others:
        problems.append(
            f"tag desconhecida na narração: {', '.join(others)} (só vale {NarrationConstants.PAUSE_TAG})"
        )
    count = text.count(NarrationConstants.PAUSE_TAG)
    if count and (
        text.startswith(NarrationConstants.PAUSE_TAG)
        or text.endswith(NarrationConstants.PAUSE_TAG)
        or text.strip().endswith(NarrationConstants.PAUSE_TAG)
    ):
        problems.append(f"{NarrationConstants.PAUSE_TAG} no começo ou no fim da narração")
    elif count and len(NarrationConstants._WELL_PLACED.findall(text)) != count:
        problems.append(
            f"{NarrationConstants.PAUSE_TAG} precisa de uma palavra e um espaço de c"
            f"ada lado (sem duas seguidas)"
        )
    return problems
