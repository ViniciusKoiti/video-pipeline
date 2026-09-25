"""HTTP mínimo com a biblioteca padrão, compartilhado pelos adapters (sem dependência nova).

As mensagens de erro nunca incluem URL nem headers: podem carregar tokens (§2.7).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any

JsonPost = Callable[[str, Mapping[str, Any], float], dict[str, Any]]  # url, corpo, timeout → JSON


class TransportError(Exception):
    def __init__(self, status: int | None, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}" if status else message)
        self.status = status


def post_json(url: str, payload: Mapping[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None
