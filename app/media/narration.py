"""Marcas dentro da narração: `<short pause>` no ponto exato (ADR 015) e marcas de emoção por trecho
(ADR 063).

O texto falado leva as marcas (o Gemini lê a pausa; o Kokoro vira silêncio; o Azure traduz a emoção em
estilo); a tela, a legenda e as âncoras dos planos usam o texto sem elas. A marca de emoção não ocupa
espaço; no tempo dos planos cada pausa vale `PAUSE_CHARS` caracteres, para os planos depois de uma pausa não
ficarem adiantados.
"""

from __future__ import annotations

from app.media.constants.narration_constants import NarrationConstants


def strip_emotions(text: str) -> str:
    """O texto sem as marcas de emoção (`<raiva>`, `</raiva>`…), que não ocupam espaço."""
    return NarrationConstants._EMOTION.sub("", text)


def strip_pauses(text: str) -> str:
    """O texto sem marcas: a de emoção some, e cada pausa (com os espaços em volta) vira um espaço só."""
    return NarrationConstants._PAUSE.sub(" ", strip_emotions(text))


def has_pauses(text: str) -> bool:
    return NarrationConstants.PAUSE_TAG in text


def split_pauses(text: str) -> list[str]:
    """Os trechos entre as pausas, sem vazios e sem marcas de emoção: o que o Kokoro sintetiza um a um."""
    return [part.strip() for part in NarrationConstants._PAUSE.split(strip_emotions(text)) if part.strip()]


def emotion_segments(text: str) -> list[tuple[str | None, str]]:
    """Os trechos seguidos da fala com a emoção de cada um (`None` fora de marca), pausas mantidas."""
    segments: list[tuple[str | None, str]] = []
    current: str | None = None
    last = 0
    for match in NarrationConstants._EMOTION_PARTS.finditer(text):
        piece = text[last:match.start()]
        if piece.strip():
            segments.append((current, piece.strip()))
        current = None if match[1] else match[2]
        last = match.end()
    if text[last:].strip():
        segments.append((current, text[last:].strip()))
    return segments


def pause_positions(text: str) -> list[int]:
    """Posição de cada pausa no texto sem marcas (onde começa a fala depois dela)."""
    positions, removed = [], 0
    for match in NarrationConstants._PAUSE.finditer(strip_emotions(text)):
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


def _emotion_problems(text: str) -> list[str]:
    """Erros das marcas de emoção: fechar sem abrir, abrir dentro de outra, não fechar, marca vazia."""
    problems: list[str] = []
    current: str | None = None
    start = 0
    for match in NarrationConstants._EMOTION_PARTS.finditer(text):
        closing, name = bool(match[1]), match[2]
        if closing and current != name:
            problems.append(f"</{name}> sem <{name}> aberta antes")
        elif closing:
            if not strip_pauses(text[start:match.start()]).strip():
                problems.append(f"<{name}> vazia")
            current = None
        elif current is not None:
            problems.append(f"<{name}> dentro de <{current}> (uma marca de emoção de cada vez)")
        else:
            current, start = name, match.end()
    if current is not None:
        problems.append(f"<{current}> sem </{current}>")
    return problems


def narration_problems(text: str) -> list[str]:
    """Erros das marcas: outra tag `<…>`, `<long pause>`, pausa mal encaixada, no começo ou no fim, e marca de
    emoção mal formada (ADR 063)."""
    problems = []
    if NarrationConstants.LONG_PAUSE_TAG in text:
        problems.append(
            f"{NarrationConstants.LONG_PAUSE_TAG} é só do lote de cenas; dentro da narração use "
            f"{NarrationConstants.PAUSE_TAG}"
        )
    known = (NarrationConstants.PAUSE_TAG, NarrationConstants.LONG_PAUSE_TAG)
    others = sorted(
        {
            t
            for t in NarrationConstants._ANY_TAG.findall(text)
            if t not in known and not NarrationConstants._EMOTION.fullmatch(t)
        }
    )
    if others:
        allowed = ", ".join(f"<{name}>" for name in NarrationConstants.EMOTION_TAGS)
        problems.append(
            f"tag desconhecida na narração: {', '.join(others)} "
            f"(vale {NarrationConstants.PAUSE_TAG} e as marcas de emoção: {allowed})"
        )
    problems += _emotion_problems(text)
    text = strip_emotions(text)
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
