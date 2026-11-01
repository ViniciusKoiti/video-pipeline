"""Tempos e efeitos de um Short (RF7; eram `voiced`, `cmd_tempos` e `sfx_placed` de `shorts_tec.py`).

- `voiced`: as falas de cena (WAV e trecho falado) do registro que `vp short voz` escreveu, conferido contra
  o WAV (`app/pipeline/motion_inputs.py`).
- `fit_timing`: o conteúdo com cada cena esticada até a fala caber, sem encurtar nenhuma.
- `resolve_effects`: o plano de efeitos (ADR 035) conferido e colocado sobre as cenas e as falas.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.errors import PipelineError
from app.media.loudness import integrated_lufs
from app.media.probe import duration_ms
from app.pipeline import sfx as sfx_module
from app.pipeline.models.fit_row import FitRow
from app.pipeline.models.motion_content import MotionContent
from app.pipeline.models.placed_sfx import PlacedSfx
from app.pipeline.models.voiced_speech import VoicedSpeech
from app.pipeline.motion_inputs import fit_content, load_narration, load_voiced


class ShortAssemblyError(PipelineError, ValueError):
    """A montagem do Short não fecha: efeito fora do contrato, fala que não cabe, cena que não existe."""


def voiced(folder: Path, narration: Path) -> dict[str, VoicedSpeech]:
    """As falas de cena (WAV e o trecho falado), pelo registro que `voz` escreveu, conferido contra o WAV."""
    record = folder / f"{narration.stem}.voz.json"
    return load_voiced(folder, record, lambda wav: duration_ms(wav) / 1000)


def fitted_path(content_file: Path) -> Path:
    return content_file.with_name(content_file.name.replace(".json", ".voz.json"))


def fit_timing(content: MotionContent, wavs: dict[str, VoicedSpeech]) -> tuple[MotionContent, list[FitRow]]:
    return fit_content(content, {scene_id: speech.seconds for scene_id, speech in wavs.items()})


def resolve_effects(
    data_dir: Path,
    content: MotionContent,
    narration: Path,
    plan_file: Path,
    wavs: dict[str, VoicedSpeech],
    warn: Callable[[str], None],
) -> tuple[list[PlacedSfx], float | None]:
    """O plano de efeitos conferido e resolvido sobre as cenas e as falas (os efeitos colocados e a loudness
    média das falas); os alertas vão para `warn` e o primeiro erro de verdade para a execução."""
    kit = sfx_module.load_kit(data_dir)
    plan = sfx_module.load_plan(plan_file)
    narrations = {line.scene: line.text for line in load_narration(narration).lines if line.scene}
    speeches = {scene_id: sfx_module.Speech(seconds=speech.seconds) for scene_id, speech in wavs.items()}
    starts = content.starts()
    durations = {s["id"]: float(s["durationSec"]) for s in content.raw["scenes"]}
    errors, warnings = sfx_module.plan_problems(plan, kit, starts, durations, narrations, speeches)
    for warning in warnings:
        warn(f"sfx: alerta: {warning}")
    if errors:
        raise ShortAssemblyError("\n".join(f"sfx: {error}" for error in errors))
    assert kit is not None  # sem o kit, `plan_problems` já devolveu o erro
    voice = [integrated_lufs(speech.wav) for speech in wavs.values()]
    voice_lufs = sum(voice) / len(voice) if voice else None
    return sfx_module.resolve_sfx(plan, kit, starts, narrations, speeches, voice_lufs), voice_lufs
