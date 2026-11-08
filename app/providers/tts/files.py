"""Publicação de um WAV: nunca um arquivo pela metade nem inválido no caminho final (RF3, §9)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.media.wav import wav_is_valid
from app.providers.errors import InvalidOutput


@contextmanager
def atomic_wav(final: Path, provider: str) -> Iterator[Path]:
    """Um caminho temporário ao lado de `final`: o adapter escreve nele, e só um WAV válido o substitui.

    Erro no bloco, ou arquivo inválido, apaga o temporário e deixa `final` como estava (a fala anterior,
    se havia, continua utilizável). O nome começa com ponto: os `glob` de limpeza do cache não o pegam."""
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_name(f".{final.stem}.partial{final.suffix}")
    partial.unlink(missing_ok=True)
    try:
        yield partial
        if not wav_is_valid(partial):
            raise InvalidOutput(provider, f"{final.name}: o áudio gerado não é um WAV válido")
        partial.replace(final)
    finally:
        partial.unlink(missing_ok=True)
