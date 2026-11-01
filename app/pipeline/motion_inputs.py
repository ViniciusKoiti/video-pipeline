"""Entradas do Short lidas do disco (RF5, G10, ADR 048): conteúdo do `motion-video`, fala gerada e narração.

Arquivo ilegível ou fora do contrato vira `MotionInputError` (um `PipelineError`) antes de qualquer síntese,
junção ou escrita, com o arquivo, a cena e o campo na mensagem. Só o que o auto-play usa é validado; o resto
do JSON do kit passa intacto (`MotionContent.raw`).
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import ValidationError

from app.errors import PipelineError
from app.pipeline.constants.motion_constants import MotionConstants
from app.pipeline.models.fit_row import FitRow
from app.pipeline.models.motion_content import MotionContent
from app.pipeline.models.narration import Narration
from app.pipeline.models.voiced_speech import VoicedSpeech


class MotionInputError(PipelineError, ValueError):
    """Conteúdo do `motion-video`, registro de fala ou narração fora do contrato."""


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _contained(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise MotionInputError(f"{path.name}: não foi possível ler ({error})") from error
    except ValueError as error:
        raise MotionInputError(f"{path.name}: JSON inválido ({error})") from error


def parse_content(raw: Any, name: str = "conteúdo") -> MotionContent:
    if not isinstance(raw, dict) or not isinstance(raw.get("scenes"), list) or not raw["scenes"]:
        raise MotionInputError(f"{name}: 'scenes' deve ser uma lista com ao menos uma cena")
    fps: Any = raw.get("fps", MotionConstants.DEFAULT_FPS)
    if not _number(fps) or fps < 1 or fps != int(fps):
        raise MotionInputError(f"{name}: fps deve ser um inteiro a partir de 1 (recebi {fps!r})")
    seen: set[str] = set()
    for n, scene in enumerate(raw["scenes"], start=1):
        label = f"{name}, cena {n}"
        if not isinstance(scene, dict):
            raise MotionInputError(f"{label}: a cena deve ser um objeto")
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id:
            raise MotionInputError(f"{label}: id deve ser um texto não vazio (recebi {scene_id!r})")
        label = f"{label} ({scene_id})"
        if scene_id in seen:
            raise MotionInputError(f"{label}: o id aparece em mais de uma cena")
        seen.add(scene_id)
        duration: Any = scene.get("durationSec")
        if not _number(duration) or duration <= 0:
            raise MotionInputError(f"{label}: durationSec deve ser finito e maior que zero ({duration!r})")
        if not isinstance(scene.get("type"), str) or not scene["type"]:
            raise MotionInputError(f"{label}: type deve ser um texto não vazio")
    return MotionContent(raw)


def load_content(path: Path) -> MotionContent:
    return parse_content(_read_json(path), path.name)


def fit_content(
    content: MotionContent, seconds: Mapping[str, float], pad: float = MotionConstants.PAD_SEC
) -> tuple[MotionContent, list[FitRow]]:
    """`MotionContent.fitted` depois de conferir as falas: de cenas que existem, com tempo finito e >= 0."""
    unknown = sorted(set(seconds) - set(content.scene_ids))
    if unknown:
        raise MotionInputError(f"falas de cenas que não existem no JSON: {', '.join(unknown)}")
    bad = sorted(scene for scene, value in seconds.items() if not _number(value) or value < 0)
    if bad:
        raise MotionInputError(f"duração de fala inválida (negativa ou não finita) em: {', '.join(bad)}")
    return content.fitted(seconds, pad)


def load_narration(path: Path) -> Narration:
    """`{"language": "pt-BR", "lines": [{"scene": ..., "text": ..., "delivery": ...}]}`."""
    try:
        return Narration.model_validate_json(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise MotionInputError(f"{path.name}: não foi possível ler ({error})") from error
    except ValidationError as error:
        first = error.errors()[0]
        where = ".".join(map(str, first["loc"])) or "registro"
        raise MotionInputError(f"{path.name}: {where}: {first['msg']}") from error


def load_voiced(
    folder: Path, record: Path, wav_seconds: Callable[[Path], float]
) -> dict[str, VoicedSpeech]:
    """As falas de cena (WAV e trecho falado) do registro que `voz` escreveu: o WAV fica dentro da pasta e
    existe, o trecho cabe nele (`0 <= começo < fim <= duração do WAV`) e cada cena aparece uma vez."""
    if not record.is_file():
        raise MotionInputError(f"falta {record.name}: rode `voz` antes")
    data = _read_json(record)
    lines = data.get("lines") if isinstance(data, dict) else None
    if not isinstance(lines, list) or not lines:
        raise MotionInputError(f"{record.name}: 'lines' deve ser uma lista com ao menos uma fala")
    speeches: dict[str, VoicedSpeech] = {}
    for n, item in enumerate(lines, start=1):
        label = f"{record.name}, fala {n}"
        if not isinstance(item, dict):
            raise MotionInputError(f"{label}: a fala deve ser um objeto")
        speech = _voiced_line(folder, item, label, wav_seconds)
        scene = item.get("scene")
        if not scene:
            continue
        if scene in speeches:
            raise MotionInputError(f"{label}: a cena {scene!r} tem mais de uma fala")
        speeches[scene] = speech
    return speeches


def _voiced_line(
    folder: Path, item: dict[str, Any], label: str, wav_seconds: Callable[[Path], float]
) -> VoicedSpeech:
    name = item.get("wav")
    if not isinstance(name, str) or not _contained(name):
        raise MotionInputError(f"{label}: wav deve ser um caminho relativo à pasta, sem '..' ({name!r})")
    wav = folder / name
    if not wav.is_file():
        raise MotionInputError(f"{label}: falta o WAV {name} (rode `voz` de novo)")
    span = item.get("speech")
    if not (isinstance(span, list) and len(span) == 2 and all(_number(x) for x in span)):
        raise MotionInputError(f"{label}: speech deve ser [começo, fim] em segundos ({span!r})")
    begin, end = float(span[0]), float(span[1])
    total = wav_seconds(wav)
    if not 0 <= begin < end <= total + MotionConstants.SPEECH_SLACK_S:
        raise MotionInputError(
            f"{label}: o trecho falado [{begin}, {end}] não cabe no WAV ({total:.2f} s): "
            "precisa de 0 <= começo < fim <= duração"
        )
    return VoicedSpeech(wav, begin, end)
