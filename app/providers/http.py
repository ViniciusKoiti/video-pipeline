"""HTTP mínimo com a biblioteca padrão, compartilhado pelos adapters (sem dependência nova).

As mensagens de erro nunca incluem URL nem headers: podem carregar tokens (§2.7).
"""

from __future__ import annotations

import json
import mimetypes
import shutil
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CHUNK_BYTES = 1 << 20
# O "Python-urllib" padrão é barrado por proxies anti-robô (a API do Pexels responde 403, erro 1010).
USER_AGENT = "video-pipeline/0.1"

JsonPost = Callable[[str, Mapping[str, Any], float], dict[str, Any]]  # url, corpo, timeout → JSON
AuthPost = Callable[[str, Mapping[str, Any], Mapping[str, str], float], dict[str, Any]]  # + cabeçalhos


class TransportError(Exception):
    def __init__(self, status: int | None, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}" if status else message)
        self.status = status



def post_json(url: str, payload: Mapping[str, Any], timeout: float) -> dict[str, Any]:
    return post_json_with_headers(url, payload, {}, timeout)


def post_json_with_headers(
    url: str, payload: Mapping[str, Any], headers: Mapping[str, str], timeout: float
) -> dict[str, Any]:
    """POST com cabeçalhos (ex.: a chave da API, que nunca vai na URL, §2.7)."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


MultipartPost = Callable[  # url, campos, arquivos, cabeçalhos, timeout → JSON
    [str, Mapping[str, str], Mapping[str, Path], Mapping[str, str], float], dict[str, Any]
]


def post_multipart(
    url: str, fields: Mapping[str, str], files: Mapping[str, Path], headers: Mapping[str, str], timeout: float
) -> dict[str, Any]:
    """POST `multipart/form-data` (ex.: um áudio para transcrição), com a biblioteca padrão."""
    boundary = f"----video-pipeline-{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
    for name, path in files.items():
        kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body += (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'
            f"Content-Type: {kind}\r\n\r\n"
        ).encode()
        body += path.read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    request = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": USER_AGENT, **headers
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


@dataclass(frozen=True)
class JsonResponse:
    data: dict[str, Any]
    headers: Mapping[str, str]  # nomes em minúsculas (ex.: "x-ratelimit-remaining")


JsonGet = Callable[[str, Mapping[str, str], float], JsonResponse]  # url, headers, timeout → JSON
FileGet = Callable[[str, Path, Mapping[str, str], float], Path]  # url, destino, headers, timeout


def get_json(url: str, headers: Mapping[str, str], timeout: float) -> JsonResponse:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            received = {name.lower(): value for name, value in response.headers.items()}
            return JsonResponse(json.loads(response.read()), received)
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


def download(url: str, dest: Path, headers: Mapping[str, str], timeout: float) -> Path:
    """Grava em `<dest>.part` e renomeia no fim: um download interrompido não deixa arquivo pela metade."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out, CHUNK_BYTES)
    except urllib.error.HTTPError as error:
        partial.unlink(missing_ok=True)
        raise TransportError(error.code, "download recusado") from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        partial.unlink(missing_ok=True)
        raise TransportError(None, str(getattr(error, "reason", error))) from None
    partial.replace(dest)
    return dest
