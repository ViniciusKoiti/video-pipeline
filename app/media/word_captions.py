"""Legenda palavra a palavra: o texto do roteiro com o tempo de cada palavra tirado do áudio (ADR 023).

O reconhecedor (`WordAligner`) devolve as palavras que ouviu, com tempo. A tela mostra as palavras do
**roteiro**, não as do reconhecedor: as duas listas são casadas sem acento, caixa nem pontuação; palavra do
roteiro que não casou (número por extenso que o reconhecedor escreveu em algarismos, nome que ele grafou de
outro jeito) recebe o trecho de tempo entre as vizinhas que casaram, dividido pelo tamanho, e fica marcada.

`captions.words.json` guarda, por cena, o nome do WAV, as palavras reconhecidas (o resultado caro, remoto)
e as palavras do roteiro com tempo, em ms da cena. A cena só é reconhecida de novo quando o WAV muda (o nome
dele já leva o hash do texto e da voz).
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from app.media.narration import strip_pauses
from app.providers.alignment.base import TimedWord

WORDS = "captions.words.json"
VERSION = 1


@dataclass(frozen=True)
class CaptionWord:
    text: str
    start_ms: int
    end_ms: int
    matched: bool  # False = tempo dividido entre as vizinhas que casaram


@dataclass(frozen=True)
class SceneSpeech:
    id: str
    audio: str  # caminho do WAV no episode.json; muda quando o texto ou a voz mudam
    narration: str
    duration_ms: int


def script_words(narration: str) -> list[str]:
    """As palavras que vão para a tela: a fala sem as marcas de pausa, separada por espaço."""
    return strip_pauses(narration).split()


def _norm(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in decomposed if unicodedata.category(c) != "Mn"))


def match_words(script: Sequence[str], heard: Sequence[TimedWord], duration_ms: int) -> list[CaptionWord]:
    """Cada palavra do roteiro com tempo, em ordem e dentro de `duration_ms`."""
    if not script:
        return []
    times: list[tuple[int, int] | None] = [None] * len(script)
    ours, theirs = [_norm(w) for w in script], [_norm(w.text) for w in heard]
    matcher = SequenceMatcher(None, ours, theirs, autojunk=False)
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            word = heard[block.b + k]
            times[block.a + k] = (word.start_ms, word.end_ms)
    matched = [t is not None for t in times]
    i = 0
    while i < len(script):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(script) and times[j] is None:
            j += 1
        before = times[i - 1] if i > 0 else None
        after = times[j] if j < len(script) else None
        left = before[1] if before else 0
        right = max(after[0] if after else duration_ms, left)
        weights = [len(script[k]) + 1 for k in range(i, j)]
        total, done, start = sum(weights), 0, left
        for k in range(i, j):
            done += weights[k - i]
            end = left + (right - left) * done // total
            times[k] = (start, end)
            start = end
        i = j
    words, previous = [], 0
    for text, span, ok in zip(script, times, matched, strict=True):
        assert span is not None
        start = min(max(span[0], previous), duration_ms)
        end = min(max(span[1], start), duration_ms)
        words.append(CaptionWord(text, start, end, ok))
        previous = start
    return words


# --- arquivo -------------------------------------------------------------------------------------------


def load(path: Path) -> dict[str, dict[str, Any]]:
    """Cenas já reconhecidas, pelo caminho do WAV. Arquivo ausente ou de outra versão: nada."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text())
    if data.get("version") != VERSION:
        return {}
    return {scene["audio"]: scene for scene in data.get("scenes", [])}


def save(path: Path, aligner: str, scenes: Iterable[dict[str, Any]]) -> None:
    payload = {"version": VERSION, "aligner": aligner, "scenes": list(scenes)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


@dataclass(frozen=True)
class Report:
    with_words: list[str]  # cenas com palavra a palavra
    without: list[str]  # cenas sem reconhecimento (ficam na legenda por frase)
    unmatched: int  # palavras do roteiro com tempo dividido


def sync_words(
    path: Path,
    scenes: Sequence[SceneSpeech],
    recognize: Callable[[SceneSpeech], list[TimedWord]] | None,
    aligner: str,
) -> Report:
    """Recalcula as palavras de cada cena; com `recognize`, reconhece as cenas cujo WAV ainda não foi visto.
    Grava depois de cada cena reconhecida: uma cota esgotada no meio não perde o que já veio."""
    known = load(path)
    entries: dict[str, dict[str, Any]] = {}
    with_words, without, unmatched = [], [], 0
    for scene in scenes:
        entry = known.get(scene.audio)
        if entry is None and recognize is not None:
            heard = recognize(scene)
            entry = {"id": scene.id, "audio": scene.audio, "recognized": [asdict(w) for w in heard]}
            entries[scene.audio] = entry
            save(path, aligner, [*entries.values(), *(e for a, e in known.items() if a not in entries)])
        if entry is None:
            without.append(scene.id)
            continue
        heard = [TimedWord(**w) for w in entry["recognized"]]
        words = match_words(script_words(scene.narration), heard, scene.duration_ms)
        entry = {**entry, "id": scene.id, "words": [asdict(w) for w in words]}
        entries[scene.audio] = entry
        with_words.append(scene.id)
        unmatched += sum(not w.matched for w in words)
    if entries:
        save(path, aligner, [entries[s.audio] for s in scenes if s.audio in entries])
    return Report(with_words, without, unmatched)


def scene_word_frames(path: Path, audio: str, fps: int) -> list[dict[str, Any]]:
    """Palavras de uma cena em quadros relativos ao início dela, para o template; vazio se a cena não tem."""
    entry = load(path).get(audio)
    if entry is None or "words" not in entry:
        return []
    return [
        {"text": w["text"], "from": round(w["start_ms"] * fps / 1000), "to": round(w["end_ms"] * fps / 1000)}
        for w in entry["words"]
    ]
