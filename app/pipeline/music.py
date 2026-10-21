"""Trilha sonora (ADR 030): do `music.json` do diretor musical ao campo `music` do `episode.json`.

Cada entrada (cue) se ancora num trecho da narração, como os planos (ADR 008): o tempo sai da posição do
trecho sobre a duração real do WAV da cena. O `vp check` confere o plano antes da voz (âncoras, faixas do
catálogo, voz cantada, fundos sobrepostos, trocas por minuto); a resolução em milissegundos vem depois da voz.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from app.media.narration import strip_pauses, timeline_length, timeline_position
from app.pipeline.schemas import (
    MUSIC_CATALOG_FILE,
    MUSIC_DIR,
    MUSIC_GAIN_DB,
    EpisodeManifest,
    EpisodeMusic,
    EpisodeScene,
    MusicAnchor,
    MusicCatalog,
    MusicPlan,
    RelPath,
    Scene,
)

MAX_BED_CHANGES_PER_MINUTE = 1.0  # fundos novos por minuto de vídeo, em média: troca só nas viradas
MIN_CUE_MS = 1000


def load_music_catalog(data_dir: Path) -> MusicCatalog | None:
    """O catálogo de `data/music/`; sem o arquivo, None."""
    path = data_dir / MUSIC_DIR / MUSIC_CATALOG_FILE
    if not path.is_file():
        return None
    return MusicCatalog.model_validate_json(path.read_text(encoding="utf-8"))


def _position(narration: str, anchor: MusicAnchor, *, edge: str) -> int | None:
    """Posição da âncora no texto falado (sem as marcas de pausa); sem `text`, o começo ou o fim da cena."""
    spoken = strip_pauses(narration)
    if anchor.text is None:
        return 0 if edge == "start" else len(spoken)
    found = spoken.find(anchor.text)
    return None if found < 0 else found


def anchor_problems(plan: MusicPlan, scenes: Sequence[Scene]) -> list[str]:
    """Âncoras que não existem no roteiro ou que terminam antes de começar."""
    narrations = {s.id: s.narration for s in scenes}
    order = {s.id: i for i, s in enumerate(scenes)}
    problems = []
    for n, cue in enumerate(plan.cues, start=1):
        points = []
        for edge, anchor in (("start", cue.start), ("end", cue.end)):
            if anchor.scene not in narrations:
                problems.append(f"music.json, entrada {n}: cena {anchor.scene} não existe")
                continue
            position = _position(narrations[anchor.scene], anchor, edge=edge)
            if position is None:
                problems.append(
                    f"music.json, entrada {n}: {anchor.text!r} não aparece na narração de {anchor.scene}"
                )
                continue
            points.append((order[anchor.scene], position))
        if len(points) == 2 and points[1] <= points[0]:
            problems.append(f"music.json, entrada {n}: a saída vem antes da entrada")
    return problems


def _span(plan_index: int, plan: MusicPlan, order: dict[str, int], narrations: dict[str, str]) -> tuple:
    cue = plan.cues[plan_index]
    start = (order[cue.start.scene], _position(narrations[cue.start.scene], cue.start, edge="start"))
    end = (order[cue.end.scene], _position(narrations[cue.end.scene], cue.end, edge="end"))
    return start, end


def plan_problems(
    plan: MusicPlan, scenes: Sequence[Scene], catalog: MusicCatalog | None, estimated_minutes: float
) -> tuple[list[str], list[str]]:
    """(erros, alertas) do plano da trilha, antes da voz. `estimated_minutes`: duração estimada do vídeo."""
    errors = anchor_problems(plan, scenes)
    warnings: list[str] = []
    tracks = catalog.by_id() if catalog else {}
    for n, cue in enumerate(plan.cues, start=1):
        if cue.track is None:
            continue
        track = tracks.get(cue.track)
        if track is None:
            errors.append(f"music.json, entrada {n}: faixa {cue.track} fora do catálogo")
        elif track.vocals:
            errors.append(f"music.json, entrada {n}: {cue.track} tem voz cantada; nunca sob a narração")
    if errors:
        return errors, warnings
    order = {s.id: i for i, s in enumerate(scenes)}
    narrations = {s.id: s.narration for s in scenes}
    spans = [(_span(i, plan, order, narrations), cue) for i, cue in enumerate(plan.cues)]
    beds = sorted(((span, cue) for span, cue in spans if cue.role == "bed"), key=lambda item: item[0][0])
    for (previous, a), (current, b) in zip(beds, beds[1:], strict=False):
        if current[0] < previous[1]:
            errors.append(
                f"music.json: fundos sobrepostos ({a.track} até {a.end.scene}; {b.track} em {b.start.scene})"
            )
    silences = [span for span, cue in spans if cue.role == "silence"]
    for span, cue in spans:
        if cue.role != "bed":
            continue
        for quiet in silences:
            if span[0] < quiet[1] and quiet[0] < span[1]:
                errors.append(f"music.json: fundo {cue.track} toca dentro de um silêncio proposital")
    if estimated_minutes > 0 and len(beds) > 1 + MAX_BED_CHANGES_PER_MINUTE * estimated_minutes:
        errors.append(
            f"music.json: {len(beds)} fundos em ~{estimated_minutes:.0f} min; troca de faixa só nas viradas "
            f"(no máximo {MAX_BED_CHANGES_PER_MINUTE:g} por minuto)"
        )
    used = {cue.track for cue in plan.cues if cue.track}
    if len(used) > 4:
        warnings.append(f"music.json: {len(used)} faixas diferentes; poucas faixas por vídeo (ADR 030)")
    return errors, warnings


def _at(scene: EpisodeScene, anchor: MusicAnchor, *, edge: str) -> int:
    position = _position(scene.narration, anchor, edge=edge)
    if position is None:
        raise ValueError(f"trilha: {anchor.text!r} não aparece na narração de {scene.id}")
    total = timeline_length(scene.narration)
    offset = round(timeline_position(scene.narration, position) / total * scene.duration_ms) if total else 0
    return scene.start_ms + min(offset, scene.duration_ms)


def resolve_music(
    plan: MusicPlan, episode: EpisodeManifest, catalog: MusicCatalog, media_for: Callable[[str], RelPath]
) -> list[EpisodeMusic]:
    """Entradas do `episode.json` com o tempo dos WAVs; o silêncio não vira entrada, é a falta de trilha.
    `media_for`: o arquivo da faixa na pasta do episódio."""
    scenes = {s.id: s for s in episode.scenes}
    tracks = catalog.by_id()
    result = []
    for cue in plan.cues:
        if cue.track is None:
            continue
        start = _at(scenes[cue.start.scene], cue.start, edge="start")
        end = _at(scenes[cue.end.scene], cue.end, edge="end")
        length = end - start
        if length < MIN_CUE_MS:
            raise ValueError(f"trilha {cue.track}: trecho de {length} ms, curto demais")
        fade_in, fade_out = cue.fade_in_ms, cue.fade_out_ms
        if fade_in + fade_out > length:  # trecho curto: os fades dividem o trecho na mesma proporção
            scale = length / (fade_in + fade_out)
            fade_in, fade_out = int(fade_in * scale), int(fade_out * scale)
        track = tracks[cue.track]
        result.append(
            EpisodeMusic(
                asset_id=cue.track,
                media=media_for(cue.track),
                role="sting" if cue.role == "sting" else "bed",
                start_ms=start,
                end_ms=end,
                track_offset_ms=cue.track_offset_ms,
                gain_db=MUSIC_GAIN_DB[cue.level],
                fade_in_ms=fade_in,
                fade_out_ms=fade_out,
                loop=cue.track_offset_ms + length > track.duration_ms,
            )
        )
    return result
