"""Linha do tempo e ritmo dos planos (ADR 008).

O tempo de cada plano sai da posição do seu trecho âncora na narração, proporcional à duração real do
WAV da cena. Quando houver tempos por palavra (alinhamento, etapa 17), eles substituem a proporção.
Ritmo é alerta, não bloqueio: a revisão humana decide.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from app.pipeline.schemas import (
    MEDIA_SHOT_KINDS,
    EpisodeFormat,
    EpisodeManifest,
    EpisodeShot,
    RelPath,
    Scene,
    Shot,
    effective_shots,
)

MIN_SHOT_MS = 1500
TARGET_AVERAGE_MS: dict[EpisodeFormat, tuple[int, int]] = {
    EpisodeFormat.EXPLAINER: (2000, 4000),
    EpisodeFormat.ARCHIVAL_DOCUMENTARY: (4000, 6000),
}


def shot_bounds(narration: str, shots: Sequence[Shot], duration_ms: int) -> list[tuple[int, int]]:
    """(início, duração) de cada plano, relativos à cena. O primeiro começa em 0 e o último termina no fim."""
    starts, cursor = [], 0
    for i, shot in enumerate(shots):
        position = 0 if i == 0 else narration.find(shot.anchor, cursor)
        if position < 0:
            raise ValueError(f"âncora {shot.anchor!r} não aparece na narração em ordem")
        starts.append(round(position / len(narration) * duration_ms))
        cursor = position + 1
    ends = [*starts[1:], duration_ms]
    bounds = [(start, end - start) for start, end in zip(starts, ends, strict=True)]
    if any(duration <= 0 for _, duration in bounds):
        raise ValueError("âncoras próximas demais: algum plano ficaria sem duração")
    return bounds


def episode_shots(
    scene: Scene, duration_ms: int, media_for: Callable[[Shot], RelPath | None]
) -> list[EpisodeShot]:
    """Planos de uma cena com tempo resolvido; `media_for` devolve o arquivo do ativo de foto/B-roll."""
    shots = effective_shots(scene)
    return [
        EpisodeShot(
            start_ms=start,
            duration_ms=duration,
            spec=shot,
            media=media_for(shot) if shot.kind in MEDIA_SHOT_KINDS else None,
        )
        for shot, (start, duration) in zip(
            shots, shot_bounds(scene.narration, shots, duration_ms), strict=True
        )
    ]


def pacing_warnings(episode: EpisodeManifest) -> list[str]:
    """Planos curtos demais e média fora da faixa do formato (explicativo 2–4 s, documentário 4–6 s)."""
    warnings, durations = [], []
    for scene in episode.scenes:
        scene_durations = [shot.duration_ms for shot in scene.shots] or [scene.duration_ms]
        durations += scene_durations
        short = [d for d in scene_durations if d < MIN_SHOT_MS]
        if short:
            warnings.append(f"{scene.id}: {len(short)} plano(s) com menos de {MIN_SHOT_MS / 1000:.1f} s")
    low, high = TARGET_AVERAGE_MS[episode.format]
    average = sum(durations) / len(durations)
    if not low <= average <= high:
        warnings.append(
            f"média de {average / 1000:.1f} s por plano fora da faixa {low / 1000:.0f}–{high / 1000:.0f} s "
            f"do formato {episode.format}"
        )
    return warnings
