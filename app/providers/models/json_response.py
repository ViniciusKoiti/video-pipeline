from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.providers.models._http_types import JsonPayload


@dataclass(frozen=True)
class JsonResponse:
    data: JsonPayload
    headers: Mapping[str, str]  # nomes em minúsculas (ex.: "x-ratelimit-remaining")
