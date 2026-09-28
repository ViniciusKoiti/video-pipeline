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
from typing import Any, ClassVar
from urllib.parse import urlparse

from app.pipeline.schemas import Asset, Provider, Status
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.base import ProviderInfo
from app.providers.errors import ProviderError, QuotaExhausted
from app.providers.http import FileGet, JsonGet, JsonResponse, TransportError, download, get_json

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


class StockArchive:
    """O que os bancos de imagem fazem igual (ArchiveProvider): busca com cache, filtro 16:9 de pelo menos
    1920×1080, miniatura, ativo em revisão com licença e crédito, download do arquivo escolhido sem a chave.

    Cada banco diz de onde vêm os resultados (`_results`) e como um resultado vira candidato (`_parse`).
    """

    provider: ClassVar[Provider]
    license_id: ClassVar[str]
    license_url: ClassVar[str]

    def __init__(
        self,
        *,
        cache_dir: Path | None = None,
        min_width: int = 1920,
        min_height: int = 1080,
        timeout_s: float = 30,
        download_timeout_s: float = 300,
        get: JsonGet = get_json,
        get_file: FileGet = download,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self.info = ProviderInfo(self.provider.value, remote=True)
        self._cache = ArchiveCache(cache_dir, self.info.name, now=now) if cache_dir else None
        self._min_width, self._min_height = min_width, min_height
        self._timeout_s, self._download_timeout_s = timeout_s, download_timeout_s
        self._get, self._get_file, self._now = get, get_file, now

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]:
        candidates: list[AssetCandidate] = []
        for item in self._results(query):
            candidate = self._parse(item, query)
            if candidate is not None and all(c.asset.id != candidate.asset.id for c in candidates):
                candidates.append(candidate)
            if len(candidates) == query.limit:
                break
        return candidates

    def download_asset(self, asset: Asset, dest: Path) -> Path:
        if asset.original_url is None:
            raise ProviderError(self.info.name, f"{asset.id} sem original_url")
        try:
            return self._get_file(asset.original_url, dest, {}, self._download_timeout_s)
        except TransportError as error:
            raise provider_error(self.info.name, error) from None

    def _results(self, query: AssetQuery) -> list[Mapping[str, Any]]:
        raise NotImplementedError

    def _parse(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        raise NotImplementedError

    def _fetch(self, url: str, headers: Mapping[str, str], cache_key: Mapping[str, Any]) -> dict[str, Any]:
        """`cache_key` identifica a busca no cache e nunca leva a chave de API."""

        def fetch() -> JsonResponse:
            return self._get(url, headers, self._timeout_s)

        try:
            return fetch().data if self._cache is None else self._cache.search(cache_key, fetch)
        except TransportError as error:
            raise provider_error(self.info.name, error) from None

    def _fits(self, width: int | None, height: int | None) -> bool:
        """Horizontal e pelo menos 1920×1080: o vídeo é 16:9."""
        width, height = width or 0, height or 0
        return width > height and width >= self._min_width and height >= self._min_height

    @staticmethod
    def _long_enough(duration: float, query: AssetQuery) -> bool:
        return query.min_duration_s is None or duration >= query.min_duration_s

    def _candidate(
        self,
        item_id: object,
        *,
        media: str,
        file_url: str,
        page_url: str,
        author: str,
        thumb_url: str | None,
        width: int,
        height: int,
        duration: float | None = None,
        credit: str | None = None,
    ) -> AssetCandidate:
        asset = Asset(
            id=f"{self.info.name}-{media}-{item_id}".lower(),
            provider=self.provider,
            provider_id=str(item_id),
            original_url=file_url,
            page_url=page_url,
            author=author,
            license_id=self.license_id,
            license_url=self.license_url,
            attribution_text=credit or f"{author} via {self.license_id}",
            retrieved_at=self._now(),
            review_status=Status.NEEDS_REVIEW,  # conferência de pessoas, marcas e texto é humana (ADR 007)
        )
        thumb_path = None
        if self._cache is not None and thumb_url:
            try:
                thumb_path = self._cache.thumbnail(
                    asset.id, thumb_url, lambda url, dest: self._get_file(url, dest, {}, self._timeout_s)
                )
            except TransportError as error:
                raise provider_error(self.info.name, error) from None
        return AssetCandidate(asset, thumb_url, thumb_path, width, height, duration)
