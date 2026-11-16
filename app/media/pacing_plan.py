"""O plano da cadência (`voice/cadencia.json`): quanto silêncio cada fim de frase recebe, pelo texto.

Uma voz sintética põe o mesmo silêncio depois de toda frase (o Azure dá ~0,9 s no ponto e ~0,8 s de cauda em
todo WAV), seja a próxima frase a continuação da anterior, seja uma pergunta. Aqui o silêncio sai do papel da
frase: continuação curta, ponto comum médio, conclusão, pergunta e virada longas, mais um respiro depois de
frase longa.
Puro: só texto entra, só números saem. Quem aplica no áudio é `app/media/voice_pacing.py`.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from app.media.constants.voice_pacing_constants import VoicePacingConstants as C
from app.media.models.scene_pacing import ScenePacing
from app.media.models.voice_pacing import VoicePacing
from app.media.narration import strip_pauses


def load_pacing(episode_dir: Path) -> VoicePacing | None:
    """A cadência do episódio; sem `voice/cadencia.json`, nenhuma (a fala fica como a voz deu)."""
    path = episode_dir / C.FILE
    if not path.is_file():
        return None
    return VoicePacing.model_validate_json(path.read_text(encoding="utf-8"))


def sentences(text: str) -> list[str]:
    """As frases da narração, sem as marcas de pausa; um ponto seguido de minúscula não fecha frase."""
    pieces = [piece for piece in C.SENTENCE_SPLIT.split(" ".join(strip_pauses(text).split())) if piece]
    merged: list[str] = []
    for piece in pieces:
        first = next((char for char in piece if char.isalpha()), "")
        if merged and first.islower():
            merged[-1] = f"{merged[-1]} {piece}"
        else:
            merged.append(piece)
    return merged


def _starts_with(sentence: str, prefixes: tuple[tuple[str, ...], ...]) -> bool:
    words = tuple(word.lower() for word in C.WORD.findall(sentence)[:3])
    return any(words[: len(prefix)] == prefix for prefix in prefixes)


def gap(before: str, after: str | None, pacing: VoicePacing, *, after_delivery: str = "neutral") -> float:
    """O silêncio entre a frase `before` e a `after` (None: era a última fala do vídeo)."""
    if after is None:
        return pacing.final_s
    if after_delivery in C.TURN_DELIVERIES:
        value = pacing.virada_s
    elif C.QUESTION_END.search(before):
        value = pacing.pergunta_s
    elif _starts_with(after, C.CONCLUSIONS):
        value = pacing.conclusao_s
    elif _starts_with(after, C.CONTINUATIONS):
        value = pacing.continuacao_s
    else:
        value = pacing.ponto_s
    if len(C.WORD.findall(before)) >= pacing.frase_longa_palavras:
        value += pacing.frase_longa_extra_s
    return round(value, 3)


def pacing_plan(lines: Sequence[tuple[str, str]], pacing: VoicePacing) -> list[ScenePacing]:
    """O plano de cada cena, na ordem: `lines` traz `(narração, entrega)` de todas as cenas do vídeo."""
    split = [sentences(text) for text, _ in lines]
    plans = []
    for index, parts in enumerate(split):
        internal = tuple(gap(parts[k], parts[k + 1], pacing) for k in range(len(parts) - 1))
        following = next((s for s in split[index + 1:] if s), None)
        delivery = lines[index + 1][1] if index + 1 < len(lines) else "neutral"
        last = parts[-1] if parts else ""
        tail = gap(last, following[0] if following else None, pacing, after_delivery=delivery)
        plans.append(ScenePacing(internal, tail))
    return plans
