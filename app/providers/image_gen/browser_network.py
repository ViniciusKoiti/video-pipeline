"""Escuta de rede da aba (CDP): os bytes originais da imagem, sem nova requisição ao site.

O endereço do <img> pode diferir do da resposta (redirecionamento, parâmetros de tamanho): aceita o mesmo
endereço ou o mesmo começo, só entre as respostas chegadas depois do envio, e recusa bytes iguais a uma
referência anexada. Endereços de imagem do site podem ser assinados: nunca vão para log nem erro (§2.7).
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable, Iterable
from typing import Any

from app.providers.image_gen.constants.browser_constants import BrowserConstants


class NetworkCapture:
    """Guarda (requestId, url) de cada resposta de imagem; `mark()` antes do envio separa as novas."""

    def __init__(self, page: Any) -> None:
        self.responses: list[tuple[str, str]] = []
        self.since = 0
        self._cdp = page.context.new_cdp_session(page)
        self._cdp.send("Network.enable", dict(BrowserConstants.NETWORK_BUFFERS))
        self._cdp.on("Network.responseReceived", self._keep)

    def _keep(self, event: dict[str, Any]) -> None:
        response = event["response"]
        if response.get("mimeType", "").startswith("image/"):
            self.responses.append((event["requestId"], response["url"]))

    def mark(self) -> None:
        self.since = len(self.responses)

    def fresh(self) -> list[tuple[str, str]]:
        return self.responses[self.since :]

    def body(self, request_id: str) -> bytes | None:
        try:
            answer = self._cdp.send("Network.getResponseBody", {"requestId": request_id})
        except Exception:  # noqa: BLE001 - corpo fora do buffer: o chamador tenta a próxima
            return None
        if answer.get("base64Encoded"):
            return base64.b64decode(answer["body"])
        return str(answer["body"]).encode("latin-1")


def matching(src: str, responses: list[tuple[str, str]]) -> list[str]:
    """requestIds das respostas que podem ser a imagem mostrada em `src`."""
    start = src.split("=")[0].split("?")[0]
    found = [rid for rid, url in responses if url == src] or [
        rid for rid, url in responses if url.startswith(start)
    ]
    if not found and BrowserConstants.GEMINI_DOWNLOAD_PATH in src:
        found = [rid for rid, url in responses if BrowserConstants.GEMINI_DOWNLOAD_PATH.lstrip("/") in url]
    return found


def largest(
    request_ids: Iterable[str], body: Callable[[str], bytes | None], refs_sha: set[str]
) -> bytes | None:
    """O maior corpo que não é uma referência anexada: a imagem inteira, não a miniatura."""
    best: bytes | None = None
    for request_id in request_ids:
        data = body(request_id)
        if data is None or hashlib.sha256(data).hexdigest() in refs_sha:
            continue
        if best is None or len(data) > len(best):
            best = data
    return best
