"""Legenda por frase a partir do áudio real de cada cena (#17, ADR 021).

Sem alinhamento fino: a fala da cena é dividida em frases (nas marcas `<short pause>`, no fim das orações e,
quando a frase não cabe em duas linhas, nas vírgulas ou perto do meio). O tempo de cada fronteira vem do WAV:
ela cai no fim de um silêncio detectado perto da posição proporcional ao texto (a próxima frase aparece quando
a fala recomeça). Sem silêncio por perto, fica na posição proporcional e conta como aproximada.

`captions.srt` é editável: quem revisa acerta número, nome e pausa. Ele só é refeito quando a fala muda (o
nome dos WAVs já leva o hash do texto e da voz); a versão anterior fica em `captions.old.srt`.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.media.narration import PAUSE_CHARS, split_pauses

CAPTIONS = "captions.srt"
OLD_CAPTIONS = "captions.old.srt"
KEY = "captions.key"
VERSION = 1  # muda quando a divisão ou o tempo mudam: a legenda gerada antes é refeita

MAX_CHARS = 60  # duas linhas da legenda em retrato (54 px em 86% de 1080 cabem ~31 caracteres por linha)
MIN_CUE_MS = 600  # bloco mais curto que isto não dá tempo de ler
SNAP_MS = 600  # distância máxima entre a posição proporcional e o silêncio onde a fronteira cai
PAUSE_SNAP_MS = 1500  # numa marca `<short pause>` o silêncio existe com certeza: procura mais longe
END_SLACK_MS = 40  # arredondamento tolerado no fim do áudio

_SENTENCE = re.compile(r"(?<=[.!?;:])\s+")
_COMMA = re.compile(r"(?<=,)\s+")
_SRT_TIME = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")
_WORD = re.compile(r"[\wÀ-ÿ]+(?:-[\wÀ-ÿ]+)*")
_NUMBER_WORDS = frozenset(
    {
        "dois", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
        "treze", "catorze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove", "vinte",
        "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa", "cem", "cento",
        "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos",
        "novecentos", "mil", "milhão", "milhões", "bilhão", "bilhões", "real", "reais", "centavo", "centavos",
        "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty",
        "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
        "billion",
    }
)


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True)
class Phrase:
    text: str
    pause_after: bool = False  # termina numa marca `<short pause>`


@dataclass(frozen=True)
class SceneAudio:
    """O que a legenda precisa de uma cena: onde ela começa no episódio, a fala e o áudio medido."""

    start_ms: int
    duration_ms: int
    narration: str
    silences_ms: Sequence[tuple[int, int]]  # silêncios internos do WAV (início, fim), em ms da cena


# --- divisão em frases -----------------------------------------------------------------------------


def phrases(narration: str, max_chars: int = MAX_CHARS) -> list[Phrase]:
    """Frases da fala, na ordem, sem as marcas de pausa; nenhuma passa de `max_chars` se der para quebrar."""
    parts = split_pauses(narration) or [narration.strip()]
    result: list[Phrase] = []
    for i, part in enumerate(parts):
        chunks = [chunk for sentence in _SENTENCE.split(part) for chunk in _fit(sentence.strip(), max_chars)]
        chunks = [c for c in chunks if c]
        for j, chunk in enumerate(chunks):
            result.append(Phrase(chunk, pause_after=j == len(chunks) - 1 and i < len(parts) - 1))
    return result


def _fit(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    for piece in _COMMA.split(text):
        if chunks and len(chunks[-1]) + 1 + len(piece) <= max_chars:
            chunks[-1] = f"{chunks[-1]} {piece}"
        else:
            chunks.append(piece)
    return [half for chunk in chunks for half in _halve(chunk, max_chars)]


def _halve(text: str, max_chars: int) -> list[str]:
    """Quebra no espaço mais perto do meio, até caber; palavra sozinha maior que o limite fica inteira."""
    if len(text) <= max_chars or " " not in text:
        return [text]
    middle = len(text) // 2
    spaces = [i for i, ch in enumerate(text) if ch == " "]
    cut = min(spaces, key=lambda i: abs(i - middle))
    return _halve(text[:cut], max_chars) + _halve(text[cut + 1 :], max_chars)


# --- tempo -------------------------------------------------------------------------------------------


def scene_cues(scene: SceneAudio, max_chars: int = MAX_CHARS) -> tuple[list[Cue], int]:
    """Blocos da cena em ms do episódio, cobrindo a cena inteira, e quantas fronteiras ficaram aproximadas."""
    found = phrases(scene.narration, max_chars)
    if not found:
        return [], 0
    weights = [len(p.text) + 1 + (PAUSE_CHARS if p.pause_after else 0) for p in found]
    total = sum(weights)
    edges, used, approximate, cumulative = [0], set(), 0, 0
    for k, phrase in enumerate(found[:-1]):
        cumulative += weights[k]
        estimate = round(scene.duration_ms * cumulative / total)
        window = PAUSE_SNAP_MS if phrase.pause_after else SNAP_MS
        edge = _snap(estimate, window, scene.silences_ms, used, edges[-1], scene.duration_ms)
        if edge is None:
            edge = estimate
            approximate += 1
        remaining = len(found) - 1 - k  # blocos que ainda precisam caber depois desta fronteira
        edge = max(edge, edges[-1] + 1)
        edge = min(edge, scene.duration_ms - remaining)
        edges.append(edge)
    edges.append(scene.duration_ms)
    cues = [
        Cue(scene.start_ms + edges[i], scene.start_ms + edges[i + 1], phrase.text)
        for i, phrase in enumerate(found)
    ]
    return cues, approximate


def _snap(
    estimate: int, window: int, silences: Sequence[tuple[int, int]], used: set[int], after: int, end: int
) -> int | None:
    """Fim do silêncio livre mais perto da estimativa, sem deixar bloco curto demais antes nem depois."""
    candidates = [
        (abs((start + stop) // 2 - estimate), i, stop)
        for i, (start, stop) in enumerate(silences)
        if i not in used
        and abs((start + stop) // 2 - estimate) <= window
        and stop - after >= MIN_CUE_MS
        and end - stop >= MIN_CUE_MS
    ]
    if not candidates:
        return None
    _, index, stop = min(candidates)
    used.add(index)
    return stop


def episode_cues(scenes: Sequence[SceneAudio], max_chars: int = MAX_CHARS) -> tuple[list[Cue], int]:
    cues: list[Cue] = []
    approximate = 0
    for scene in scenes:
        found, rough = scene_cues(scene, max_chars)
        cues += found
        approximate += rough
    return cues, approximate


# --- SRT ---------------------------------------------------------------------------------------------


def _srt_time(ms: int) -> str:
    return f"{ms // 3_600_000:02}:{ms // 60_000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def to_srt(cues: Sequence[Cue]) -> str:
    return "".join(
        f"{n}\n{_srt_time(c.start_ms)} --> {_srt_time(c.end_ms)}\n{c.text}\n\n" for n, c in enumerate(cues, 1)
    )


def parse_srt(text: str) -> tuple[list[Cue], list[str]]:
    """Blocos do SRT e os problemas de formato (bloco sem tempo, texto vazio)."""
    cues: list[Cue] = []
    problems: list[str] = []
    for n, block in enumerate(re.split(r"\n\s*\n", text.strip()), 1):
        lines = block.strip().splitlines()
        if not lines:
            continue
        times = _SRT_TIME.findall(lines[1]) if len(lines) >= 2 else []
        if len(times) != 2:
            problems.append(f"bloco {n}: sem a linha de tempo 'hh:mm:ss,mmm --> hh:mm:ss,mmm'")
            continue
        start, end = (int(h) * 3_600_000 + int(m) * 60_000 + int(s) * 1000 + int(ms) for h, m, s, ms in times)
        body = " ".join(line.strip() for line in lines[2:]).strip()
        if not body:
            problems.append(f"bloco {n}: sem texto")
            continue
        cues.append(Cue(start, end, body))
    return cues, problems


def timing_problems(cues: Sequence[Cue], total_ms: int) -> list[str]:
    """Intervalo vazio ou invertido, bloco que começa antes do anterior acabar, bloco além do áudio."""
    problems: list[str] = []
    if not cues:
        problems.append("nenhum bloco de legenda")
    previous_end = 0
    for n, cue in enumerate(cues, 1):
        if cue.end_ms <= cue.start_ms:
            problems.append(f"bloco {n}: fim {_srt_time(cue.end_ms)} não vem depois do início")
        if cue.start_ms < previous_end:
            problems.append(f"bloco {n}: começa antes de o bloco {n - 1} acabar")
        if cue.end_ms > total_ms + END_SLACK_MS:
            problems.append(
                f"bloco {n}: termina em {_srt_time(cue.end_ms)}, depois do áudio ({_srt_time(total_ms)})"
            )
        previous_end = max(previous_end, cue.end_ms)
    return problems


# --- revisão -----------------------------------------------------------------------------------------


def review_hints(cues: Sequence[Cue]) -> list[tuple[int, str]]:
    """Blocos a conferir à mão: número (algarismo ou por extenso) e nome próprio fora do início da frase."""
    hints: list[tuple[int, str]] = []
    for n, cue in enumerate(cues, 1):
        reasons = []
        if any(ch.isdigit() for ch in cue.text) or any(
            w.lower() in _NUMBER_WORDS for w in _WORD.findall(cue.text)
        ):
            reasons.append("número")
        if _proper_names(cue.text):
            reasons.append("nome: " + ", ".join(_proper_names(cue.text)))
        if reasons:
            hints.append((n, f"{'; '.join(reasons)} — {cue.text}"))
    return hints


def _proper_names(text: str) -> list[str]:
    names, sentence_start = [], True
    for match in re.finditer(r"[^\s]+", text):
        token = match.group()
        word = _WORD.search(token)
        if word and word.group()[0].isupper() and not sentence_start:
            names.append(word.group())
        sentence_start = token[-1] in ".!?:"
    return names


# --- arquivo editável ---------------------------------------------------------------------------------


def captions_key(audio_names: Sequence[str], max_chars: int = MAX_CHARS) -> str:
    """O que, mudando, refaz a legenda: os WAVs (o nome já leva texto e voz), o limite e a versão."""
    raw = f"v{VERSION}|{max_chars}|" + "|".join(audio_names)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def sync_captions(episode_dir: Path, cues: Sequence[Cue], key: str) -> str:
    """Grava `captions.srt` se ele não existe ou se a fala mudou; senão mantém o arquivo (talvez revisado)."""
    srt, key_file = episode_dir / CAPTIONS, episode_dir / KEY
    if srt.is_file() and key_file.is_file() and key_file.read_text().strip() == key:
        return "mantida (pode ter revisão à mão)"
    if srt.is_file():
        srt.replace(episode_dir / OLD_CAPTIONS)
        note = f"refeita porque a fala mudou; a anterior ficou em {OLD_CAPTIONS}: revise de novo"
    else:
        note = "gerada; revise números, nomes e pausas"
    srt.write_text(to_srt(cues))
    key_file.write_text(key + "\n")
    return note
