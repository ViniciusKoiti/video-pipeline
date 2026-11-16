"""Grade de cor do B-roll (ADR 057): `tratamento.json` do episódio lista os ativos em preto e branco."""

from __future__ import annotations

import json
from pathlib import Path

from app.errors import PipelineError
from app.render.constants.remotion_constants import RemotionConstants as Constants


class GradeInvalid(PipelineError, ValueError):
    """O `tratamento.json` não segue o formato `{"mono": ["id-do-ativo", ...]}`."""


def mono_assets(episode_dir: Path) -> frozenset[str]:
    """Ids dos ativos de B-roll que saem em preto e branco; sem o arquivo, nenhum."""
    path = episode_dir / Constants.GRADE_FILE
    if not path.is_file():
        return frozenset()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise GradeInvalid(f"{path.name}: JSON inválido ({exc})") from exc
    ids = data.get("mono") if isinstance(data, dict) else None
    if not isinstance(ids, list) or not all(isinstance(i, str) and i for i in ids) or set(data) - {"mono"}:
        raise GradeInvalid(f'{path.name}: esperado {{"mono": ["id-do-ativo", ...]}}')
    return frozenset(ids)
