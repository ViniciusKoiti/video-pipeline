"""A busca de candidatos visuais de um pedido (RF7; era o corpo de `buscar_candidatos.py`).

Um **pedido** é `{"id", "plano", "consultas": [...], "midias": ["video", "photo"], "min_duration_s",
"orientacao"}`. Cada consulta vai a cada banco em cada mídia pedida; a falha de um banco (cota, serviço)
fica registrada no resultado, com o motivo, e não interrompe os outros (§2.1). Provedor pago bloqueado
interrompe a busca (`PaidApiBlocked`, custo zero, ADR 044). Tudo é ilustração: `visual_need` sempre
`contextual_stock`. Nada é baixado aqui; o resultado é o conteúdo de `candidatos/<pedido>.json`.

Orientação do arquivo: `orientacao` do pedido (`landscape` ou `portrait`); sem ela, a do `scenes.json` do
episódio (ADR 014), e sem o arquivo, `landscape`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from app.pipeline.assets import AssetError, search_archives
from app.pipeline.constants.candidates_constants import CandidatesConstants as Constants
from app.pipeline.models.skipped_archive import SkippedArchive
from app.pipeline.schemas import Orientation, VisualNeed
from app.providers.archives.base import ArchiveProvider, AssetCandidate, AssetQuery


def episode_orientation(episode_dir: Path) -> Orientation:
    """`orientation` do scenes.json do episódio (ADR 014); sem o arquivo, 16:9."""
    scenes = episode_dir / "scenes.json"
    if scenes.is_file() and json.loads(scenes.read_text()).get("orientation") == "portrait":
        return "portrait"
    return "landscape"


def _relative(path: Path, root: Path) -> str:
    """Caminho a partir da raiz do repositório; com `DATA_DIR` fora dela (worktree), o caminho inteiro."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _record(candidate: AssetCandidate, bank: str, text: str, media: str, root: Path) -> dict[str, Any]:
    thumb = candidate.thumbnail_path
    return {
        "banco": bank,
        "consulta": text,
        "midia": media,
        "largura": candidate.width,
        "altura": candidate.height,
        "duracao_s": candidate.duration_s,
        "miniatura": _relative(thumb, root) if thumb else None,
        "ativo": candidate.asset.model_dump(mode="json"),
    }


def search_request(
    archives: Sequence[ArchiveProvider],
    skipped: Sequence[SkippedArchive],
    request: Mapping[str, Any],
    default_orientation: Orientation,
    limit: int,
    root: Path,
) -> tuple[dict[str, Any], Orientation]:
    """O resultado de um pedido e a orientação usada. Orientação inválida é erro, antes de qualquer busca."""
    orientation = request.get("orientacao", default_orientation)
    if orientation not in Constants.ORIENTATIONS:
        raise AssetError(f"{request['id']}: orientacao é landscape ou portrait, não {orientation!r}")
    found: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    for text in request["consultas"]:
        for media in request.get("midias", Constants.DEFAULT_MEDIA):
            query = AssetQuery(
                text=text,
                visual_need=VisualNeed.CONTEXTUAL_STOCK,
                limit=limit,
                media=media,
                min_duration_s=request.get("min_duration_s") if media == "video" else None,
                orientation=orientation,
            )
            searched = search_archives(archives, query)  # PaidApiBlocked interrompe a busca
            failures += [
                {"banco": f.bank, "consulta": f.query, "razao": f.reason, "motivo": f.detail}
                for f in searched.failures
            ]
            for bank, candidate in searched.hits:
                found.setdefault(candidate.asset.id, _record(candidate, bank, text, media, root))
    result = {
        "pedido": request,
        "candidatos": list(found.values()),
        "falhas": failures,
        "bancos_pulados": [{"banco": s.name, "motivo": s.reason} for s in skipped],
    }
    return result, orientation


def count_by_bank(result: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for candidate in result["candidatos"]:
        counts[candidate["banco"]] = counts.get(candidate["banco"], 0) + 1
    return counts
