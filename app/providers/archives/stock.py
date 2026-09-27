"""Peças comuns aos adapters de banco de imagem (§8, ADR 007 com a emenda de bancos de imagem).

Cache em `data/cache/archives/<provedor>/`:
- `search/<chave>.json`: parâmetros da busca (nunca a chave de API) e a resposta; consulta repetida não
  chama a API de novo (o Pixabay exige cache de 24 h; aqui ele não expira);
- `thumbs/<asset_id>.<ext>`: miniaturas para a folha de contato;
- `quota.json`: os últimos headers de cota recebidos, sem nenhum outro header.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.providers.errors import ProviderError, QuotaExhausted
from app.providers.http import JsonResponse, TransportError

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")


def normalize_query(text: str) -> str:
    """Mesma busca, mesma chave de cache: minúsculas e espaços simples."""
    return " ".join(text.casefold().split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def provider_error(provider: str, error: TransportError) -> ProviderError:
    """Erro de transporte → falha do provedor, que para só a cena (§2.1). Nunca com URL nem headers."""
    if error.status == 429:
        return QuotaExhausted(provider, "limite de requisições atingido")
    if error.status in (401, 403):
        return ProviderError(provider, f"chave recusada (HTTP {error.status}); confira o .env")
    return ProviderError(provider, str(error))


class ArchiveCache:
    def __init__(self, root: Path, provider: str, *, now: Callable[[], datetime] = utc_now) -> None:
        self._dir = root / provider
        self._now = now

    def search(self, params: Mapping[str, Any], fetch: Callable[[], JsonResponse]) -> dict[str, Any]:
        encoded = json.dumps(params, sort_keys=True, ensure_ascii=False)
        path = self._dir / "search" / f"{hashlib.sha256(encoded.encode()).hexdigest()[:16]}.json"
        if path.is_file():
            return json.loads(path.read_text())["response"]
        response = fetch()
        self._write(
            path, {"params": dict(params), "fetched_at": self._now().isoformat(), "response": response.data}
        )
        self.record_quota(response.headers)
        return response.data

    def record_quota(self, headers: Mapping[str, str]) -> None:
        quota = {name: value for name, value in headers.items() if name.lower().startswith("x-ratelimit")}
        if quota:
            self._write(self._dir / "quota.json", {"at": self._now().isoformat(), "headers": quota})

    def thumbnail(self, asset_id: str, url: str, fetch: Callable[[str, Path], Path]) -> Path:
        suffix = Path(urlparse(url).path).suffix.lower()
        path = self._dir / "thumbs" / f"{asset_id}{suffix if suffix in IMAGE_SUFFIXES else '.jpg'}"
        return path if path.is_file() else fetch(url, path)

    @staticmethod
    def _write(path: Path, data: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
