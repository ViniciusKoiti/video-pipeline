"""Duração real da fala de cada cena, lida dos WAVs que o `vp voice` registrou no `manifest.json` (ADR 052).

O relógio de retenção (ADR 061) usa estes tempos quando a voz de todas as cenas existe; antes disso, estima
pela quantidade de texto. Medir é do chamador (`measure`, o `ffprobe` na linha de comando): o núcleo não roda
processo. Fala gravada antes de uma mudança no roteiro dá tempo velho: rode o `vp voice` antes de conferir.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from app.pipeline.models.status import Status
from app.pipeline.models.step import Step
from app.pipeline.ports import ManifestStore
from app.pipeline.state import load_state


def voiced_paths(store: ManifestStore, episode_id: str, scene_ids: Sequence[str]) -> dict[str, Path] | None:
    """O WAV que vai ao vídeo (a cópia nivelada, quando existe) de cada cena, por id; `None` se alguma cena
    ainda não tem voz pronta ou o arquivo sumiu."""
    records = load_state(store, episode_id).get(Step.VOICE).scenes
    paths: dict[str, Path] = {}
    for scene_id in scene_ids:
        record = records.get(scene_id)
        if record is None or record.status is not Status.COMPLETED or not record.outputs:
            return None
        path = store.path(episode_id, record.outputs[0])
        if not path.is_file():
            return None
        paths[scene_id] = path
    return paths


def measured_seconds(
    store: ManifestStore, episode_id: str, scene_ids: Sequence[str], measure: Callable[[Path], float]
) -> dict[str, float] | None:
    """Segundos da fala de cada cena, por id; `None` se alguma cena ainda não tem voz pronta."""
    paths = voiced_paths(store, episode_id, scene_ids)
    return None if paths is None else {scene_id: measure(path) for scene_id, path in paths.items()}
