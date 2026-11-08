"""Entradas dos efeitos sonoros lidas do disco (RF5, G10): o `sounds.json` do kit e o `sfx.json` do vídeo.

Arquivo ilegível ou fora do contrato vira `SfxInputError` (um `PipelineError`) antes de qualquer síntese,
junção ou escrita, com o som ou o efeito que falhou na mensagem. O JSON do kit é do dono (clone do SFX Kit);
só os campos que o auto-play usa são validados; os demais são ignorados, sem reescrever o arquivo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.errors import PipelineError
from app.pipeline.constants.sfx_constants import SfxConstants
from app.pipeline.models.sfx_kit import SfxKit
from app.pipeline.models.sfx_plan import SfxPlan
from app.pipeline.models.sfx_sound import SfxSound


class SfxInputError(PipelineError, ValueError):
    """`sounds.json` ou `sfx.json` ilegível ou fora do contrato."""


def _details(error: ValidationError) -> str:
    return "; ".join(f"{'.'.join(map(str, e['loc'])) or 'registro'}: {e['msg']}" for e in error.errors())


def parse_kit(root: Path, text: str) -> SfxKit:
    index = SfxConstants.KIT_INDEX
    try:
        data = json.loads(text)
    except ValueError as error:
        raise SfxInputError(f"{index}: JSON inválido ({error})") from error
    records = data.get("sounds") if isinstance(data, dict) else None
    if not isinstance(records, list) or not records:
        raise SfxInputError(f"{index}: 'sounds' deve ser uma lista com ao menos um som")
    sounds: dict[str, SfxSound] = {}
    for n, record in enumerate(records, start=1):
        sound = _sound(record, f"{index}, som {n}")
        if sound.id in sounds:
            raise SfxInputError(f"{index}: o id {sound.id!r} aparece mais de uma vez")
        sounds[sound.id] = sound
    return SfxKit(root=root, license=str(data.get("license", "")), sounds=sounds)


def _sound(record: Any, label: str) -> SfxSound:
    if not isinstance(record, dict):
        raise SfxInputError(f"{label}: o registro deve ser um objeto")
    label = f"{label} ({record.get('id')})"
    try:
        fits = record.get("fits_seconds")
        return SfxSound(
            id=record["id"],
            file=record["file"],
            duration=record["duration"],
            sync_at=record["sync"]["at"],
            meets=record["sync"]["meets"],
            onset=record["timing"]["onset"],
            body_end=record["timing"]["body_end"],
            under_voiceover_db=record["under_voiceover_db"],
            avoid_for=record.get("avoid_for", []),
            fits_seconds=tuple(fits) if fits else None,
            sha256=record["sha256"],
        )
    except KeyError as error:
        raise SfxInputError(f"{label}: falta o campo {error}") from error
    except (TypeError, ValueError) as error:  # ValidationError é ValueError
        detail = _details(error) if isinstance(error, ValidationError) else str(error)
        raise SfxInputError(f"{label}: {detail}") from error


def load_plan(path: Path) -> SfxPlan:
    """O `sfx.json` de um vídeo: ausente, JSON inválido ou efeito fora do contrato é `SfxInputError`."""
    try:
        return SfxPlan.model_validate_json(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise SfxInputError(f"{path.name}: não foi possível ler ({error})") from error
    except ValidationError as error:
        raise SfxInputError(f"{path.name}: {_details(error)}") from error
