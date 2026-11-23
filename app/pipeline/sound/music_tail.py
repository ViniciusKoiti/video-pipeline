"""A cauda da tela final (emenda de 2026-11-23 da ADR 030): segundos só de trilha depois da última fala.

O fundo que chega ao fim da última cena continua por `end_tail_ms` do `music.json`, com o fade no fim novo
e `loop` recalculado. Sem fundo que chegue ao fim, é erro: a tela final ficaria em silêncio.
"""

from __future__ import annotations

from app.pipeline.schemas import EpisodeManifest, EpisodeMusic, MusicCatalog


def with_end_tail(
    music: list[EpisodeMusic], tail_ms: int, episode: EpisodeManifest, catalog: MusicCatalog
) -> list[EpisodeMusic]:
    """O fundo que chega ao fim da última fala continua por `tail_ms`: a tela final fica só com a trilha."""
    if not tail_ms:
        return music
    end = max(s.start_ms + s.duration_ms for s in episode.scenes)
    last = [i for i, m in enumerate(music) if m.role == "bed" and m.end_ms == end]
    if not last:
        raise ValueError(f"trilha: cauda de {tail_ms} ms sem fundo que chegue ao fim da última fala")
    entry = music[last[-1]]
    length = end + tail_ms - entry.start_ms
    music[last[-1]] = entry.model_copy(
        update={
            "end_ms": end + tail_ms,
            "loop": entry.track_offset_ms + length > catalog.by_id()[entry.asset_id].duration_ms,
        }
    )
    return music
