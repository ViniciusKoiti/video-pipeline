from __future__ import annotations

from dataclasses import dataclass, field

from app.pipeline.models.search_failure import SearchFailure
from app.providers.archives.base import AssetCandidate


@dataclass(frozen=True)
class SearchResult:
    """O que uma consulta achou, por banco, e o que falhou. Lista vazia e sem falha é "sem resultado"."""

    hits: list[tuple[str, AssetCandidate]] = field(default_factory=list)
    failures: list[SearchFailure] = field(default_factory=list)
