"""Texto e WAV da fala clonada: o corte da fala longa em grupos de frases, a junção dos trechos e o hash da
referência (que identifica a voz no cache). Funções puras; o adapter está em `chatterbox.py`."""

from __future__ import annotations

import hashlib
import wave
from pathlib import Path

from app.providers.tts.constants.chatterbox_constants import ChatterboxConstants


def _pack(pieces: list[str], limit: int) -> list[str]:
    groups: list[str] = []
    current = ""
    for piece in pieces:
        joined = f"{current} {piece}" if current else piece
        if current and len(joined) > limit:
            groups.append(current)
            current = piece
        else:
            current = joined
    return [*groups, current] if current else groups


def _split_sentence(sentence: str, limit: int) -> list[str]:
    """Frase maior que o limite: parte nas vírgulas, e a oração ainda maior, nas palavras."""
    pieces: list[str] = []
    for clause in ChatterboxConstants._CLAUSE_END.split(sentence):
        pieces.extend(_pack(clause.split(), limit) if len(clause) > limit else [clause])
    return _pack(pieces, limit)


def split_long(text: str, limit: int = ChatterboxConstants.MAX_PART_CHARS) -> list[str]:
    """Os grupos de frases, cada um com até `limit` caracteres, na ordem do texto; o texto curto
    fica inteiro."""
    text = text.strip()
    if len(text) <= limit:
        return [text] if text else []
    pieces: list[str] = []
    for sentence in ChatterboxConstants._SENTENCE_END.split(text):
        sentence = sentence.strip()
        if sentence:
            pieces.extend(_split_sentence(sentence, limit) if len(sentence) > limit else [sentence])
    return _pack(pieces, limit)


def join_wavs(pieces: list[Path], gap_ms: int, out_path: Path) -> None:
    """Junta WAVs PCM do mesmo formato, com `gap_ms` de silêncio entre eles."""
    with wave.open(str(pieces[0]), "rb") as first:
        params = first.getparams()
    gap = b"\x00" * (round(params.framerate * gap_ms / 1000) * params.sampwidth * params.nchannels)
    with wave.open(str(out_path), "wb") as out:
        out.setnchannels(params.nchannels)
        out.setsampwidth(params.sampwidth)
        out.setframerate(params.framerate)
        for i, piece in enumerate(pieces):
            with wave.open(str(piece), "rb") as wav:
                if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != params[:3]:
                    raise ValueError(f"formato diferente em {piece.name}")
                if i:
                    out.writeframes(gap)
                out.writeframes(wav.readframes(wav.getnframes()))


def reference_hash(reference: Path) -> str:
    """Entra na chave de cache da fala: trocar a gravação de referência troca a voz."""
    return hashlib.sha256(reference.read_bytes()).hexdigest()[:12]
