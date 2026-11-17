"""Conferência da fala depois da voz (ADR 062).

A voz clonada não segue a grafia do glossário de forma estável: no `vazio-de-ter-tudo`, com "Tórfin", "ôuf" e
"én émpti mén" no texto enviado, saíram trechos como "em Man" e "Wolf", e palavras comuns trocadas ("curso"
por "custo", "care" por "cárie"). Aqui um reconhecedor local ouve o WAV de cada cena, sem o texto esperado, e
o resultado é comparado com o roteiro:

- **termo** do glossário: o que se ouviu no lugar dele precisa lembrar a grafia ou a `fala` (sem acento, sem
  "h" e sem letra dobrada); senão, é diferença;
- **palavra** comum: trocada ou faltando, quando tem pelo menos quatro letras (as curtas são ruído do
  reconhecedor) e não é só número escrito de outro jeito.

Não aprova nada: o reconhecedor também erra. A diferença aponta o trecho que o dono ouve (folha de escuta).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from difflib import SequenceMatcher
from pathlib import Path

from app.media.narration import strip_pauses
from app.media.pronunciation import Glossary, Term
from app.pipeline.constants.speech_review_constants import SpeechReviewConstants as Constants
from app.pipeline.models.heard_difference import HeardDifference
from app.pipeline.models.scene_hearing import SceneHearing
from app.pipeline.models.speech_review import SpeechReview
from app.pipeline.schemas import Scene, ScenesManifest
from app.providers.alignment.base import TimedWord, WordAligner

Span = tuple[int, int]


def norm(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in decomposed if unicodedata.category(c) != "Mn"))


def sound(text: str) -> str:
    """Uma aproximação do som, para comparar nome escrito de jeitos diferentes: sem acento, espaço, "h" e
    letra dobrada ("Thorfinn" e "Tórfin" viram "torfin")."""
    plain = "".join(norm(word) for word in text.split()).replace("h", "")
    return re.sub(r"(.)\1+", r"\1", plain)


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def _term_spans(ours: Sequence[str], glossary: Glossary) -> list[tuple[Span, Term]]:
    spans = []
    for term in glossary.termos:
        words = [norm(w) for w in term.escrita.split() if norm(w)]
        size = len(words)
        starts = [i for i in range(len(ours) - size + 1) if list(ours[i : i + size]) == words]
        spans += [((i, i + size), term) for i in starts]
    return spans


def _heard_span(opcodes: Sequence[tuple[str, int, int, int, int]], first: int, last: int) -> Span:
    """As palavras ouvidas que correspondem às do roteiro de `first` a `last` (exclusivo)."""
    found: list[int] = []
    start_at = None
    for tag, i1, i2, j1, j2 in opcodes:
        if i2 <= first or i1 >= last:
            if i1 >= last and start_at is None:
                start_at = j1
            continue
        if tag == "equal":
            found += [j1 + (i - i1) for i in range(max(i1, first), min(i2, last))]
        else:
            found += list(range(j1, j2))
            start_at = j1 if start_at is None else start_at
    if found:
        return min(found), max(found) + 1
    at = start_at if start_at is not None else 0
    return at, at


def _times(words: Sequence[TimedWord], span: Span) -> Span:
    j1, j2 = span
    if j1 < j2:
        return words[j1].start_ms, words[j2 - 1].end_ms
    before = words[j1 - 1].end_ms if 0 < j1 <= len(words) else 0
    after = words[j1].start_ms if j1 < len(words) else before + 1000
    return before, max(before, after)


def _is_noise(expected: Sequence[str], heard: Sequence[str]) -> bool:
    if all(len(word) < Constants.MIN_CONTENT_LETTERS for word in expected):
        return True
    if heard and all(word.isdigit() for word in heard):  # o reconhecedor escreve número com algarismo
        return True
    return all(word.isdigit() for word in expected) or sound(" ".join(expected)) == sound(" ".join(heard))


def hear_scene(scene: Scene, wav: str, words: Sequence[TimedWord], glossary: Glossary) -> SceneHearing:
    raw = [token for token in strip_pauses(scene.narration).split() if norm(token)]
    words = [word for word in words if norm(word.text)]
    ours, theirs = [norm(token) for token in raw], [norm(word.text) for word in words]
    opcodes = SequenceMatcher(None, ours, theirs, autojunk=False).get_opcodes()
    differences: list[HeardDifference] = []
    terms = _term_spans(ours, glossary)
    for (first, last), term in terms:
        span = _heard_span(opcodes, first, last)
        heard = " ".join(word.text for word in words[span[0] : span[1]])
        if max(_similar(sound(heard), sound(term.escrita)), _similar(sound(heard), sound(term.fala))) >= (
            Constants.TERM_SIMILARITY
        ):
            continue
        start, end = _times(words, span)
        differences.append(HeardDifference(
            scene_id=scene.id, kind="termo", expected=" ".join(raw[first:last]), heard=heard,
            spoken_as=term.fala, start_ms=start, end_ms=end,
        ))
    errors = 0
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            continue
        errors += max(i2 - i1, j2 - j1)
        inside_term = any(i1 < last and i2 > first for (first, last), _ in terms)
        if i1 == i2 or inside_term or _is_noise(ours[i1:i2], theirs[j1:j2]):
            continue
        start, end = _times(words, (j1, j2))
        differences.append(HeardDifference(
            scene_id=scene.id, kind="palavra", expected=" ".join(raw[i1:i2]),
            heard=" ".join(word.text for word in words[j1:j2]), start_ms=start, end_ms=end,
        ))
    rate = round(errors / len(ours), 3) if ours else 0.0
    heard_text = " ".join(word.text for word in words)
    return SceneHearing(
        scene_id=scene.id, wav=wav, heard=heard_text, word_error_rate=rate, differences=differences
    )


def review_speech(
    recognizer: WordAligner, scenes: ScenesManifest, wavs: Mapping[str, Path], glossary: Glossary,
    episode_dir: Path,
) -> SpeechReview:
    """Ouve a fala de cada cena (sem o texto esperado como `prompt`) e compara com o roteiro."""
    hearings = []
    for scene in scenes.scenes:
        wav = wavs[scene.id]
        words = recognizer.recognize_words(wav, scenes.language)
        hearings.append(hear_scene(scene, str(wav.relative_to(episode_dir)), words, glossary))
    return SpeechReview(episode_id=scenes.episode_id, recognizer=recognizer.info.name, scenes=hearings)
