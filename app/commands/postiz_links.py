"""Conferência dos links das legendas do pacote Postiz; não agenda publicações."""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from app.commands.constants.postiz_links_constants import PostizLinksConstants

LinkFetch = Callable[[str], "int | None"]


def link_status(url: str) -> int | None:
    """Código HTTP do link (HEAD, depois GET se o HEAD não for aceito); None se não houve resposta."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "vp-postiz-pacote"})
        try:
            with urllib.request.urlopen(request, timeout=PostizLinksConstants.LINK_TIMEOUT_S) as response:
                status: int = response.status
                return status
        except urllib.error.HTTPError as error:
            if method == "GET" or error.code not in (403, 405, 501):
                return error.code
        except (urllib.error.URLError, TimeoutError, OSError):
            return None
    return None


def caption_links(text: str) -> list[str]:
    """Os links da legenda, sem pontuação final e sem repetição, na ordem em que aparecem."""
    return list(dict.fromkeys(url.rstrip(".,;:!?") for url in PostizLinksConstants.LINK.findall(text)))


def link_findings(posts: list[dict[str, Any]], fetch: LinkFetch) -> tuple[list[str], list[str]]:
    """(bloqueios, riscos) dos links das legendas: 404/410 bloqueia; outro erro ou sem resposta é risco."""
    blocking, risks, seen = [], [], {}
    for post in posts:
        for url in caption_links(post["legenda"]):
            if url not in seen:
                seen[url] = fetch(url)
            status = seen[url]
            if status is None:
                risks.append(f"Link da legenda de {post['canal']} sem resposta, não conferido: {url}")
            elif status in PostizLinksConstants.GONE:
                blocking.append(f"Link da legenda de {post['canal']} não abre (HTTP {status}): {url}")
            elif status >= 400:
                risks.append(f"Link da legenda de {post['canal']} respondeu HTTP {status}: {url}")
    return blocking, risks
