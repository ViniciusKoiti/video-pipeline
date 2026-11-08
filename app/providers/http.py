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
from pathlib import Path
from typing import Any

from app.errors import PipelineError
from app.providers.constants.http_constants import HttpConstants
from app.providers.models._http_types import JsonPayload as JsonPayload
from app.providers.models.json_response import JsonResponse as JsonResponse

# O "Python-urllib" padrão é barrado por proxies anti-robô (a API do Pexels responde 403, erro 1010).


JsonPost = Callable[[str, Mapping[str, Any], float], JsonPayload]  # url, corpo, timeout → JSON
AuthPost = Callable[[str, Mapping[str, Any], Mapping[str, str], float], JsonPayload]  # + cabeçalhos


def parse_json(raw: str | bytes) -> JsonPayload:
    value: object = json.loads(raw)
    if not isinstance(value, (dict, list)):
        raise ValueError("resposta JSON deve ser um objeto ou uma lista")
    return value


class TransportError(PipelineError):
    def __init__(self, status: int | None, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}" if status else message)
        self.status = status


def post_json(url: str, payload: Mapping[str, Any], timeout: float) -> JsonPayload:
    return post_json_with_headers(url, payload, {}, timeout)


def post_json_with_headers(
    url: str, payload: Mapping[str, Any], headers: Mapping[str, str], timeout: float
) -> JsonPayload:
    """POST com cabeçalhos (ex.: a chave da API, que nunca vai na URL, §2.7)."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": HttpConstants.USER_AGENT, **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return parse_json(response.read())
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


MultipartPost = Callable[  # url, campos, arquivos, cabeçalhos, timeout → JSON
    [str, Mapping[str, str], Mapping[str, Path], Mapping[str, str], float], JsonPayload
]


def post_multipart(
    url: str, fields: Mapping[str, str], files: Mapping[str, Path], headers: Mapping[str, str], timeout: float
) -> JsonPayload:
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
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": HttpConstants.USER_AGENT,
            **headers,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return parse_json(response.read())
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


JsonGet = Callable[[str, Mapping[str, str], float], JsonResponse]  # url, headers, timeout → JSON
FileGet = Callable[[str, Path, Mapping[str, str], float], Path]  # url, destino, headers, timeout


def get_json(url: str, headers: Mapping[str, str], timeout: float) -> JsonResponse:
    request = urllib.request.Request(
        url, headers={"User-Agent": HttpConstants.USER_AGENT, **headers}, method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            received = {name.lower(): value for name, value in response.headers.items()}
            return JsonResponse(parse_json(response.read()), received)
    except urllib.error.HTTPError as error:
        raise TransportError(error.code, error.read().decode(errors="replace")[:500]) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(None, str(getattr(error, "reason", error))) from None


def download(url: str, dest: Path, headers: Mapping[str, str], timeout: float) -> Path:
    """Grava em `<dest>.part` e renomeia no fim: um download interrompido não deixa arquivo pela metade."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(
        url, headers={"User-Agent": HttpConstants.USER_AGENT, **headers}, method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out, HttpConstants.CHUNK_BYTES)
    except urllib.error.HTTPError as error:
        partial.unlink(missing_ok=True)
        raise TransportError(error.code, "download recusado") from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        partial.unlink(missing_ok=True)
        raise TransportError(None, str(getattr(error, "reason", error))) from None
    partial.replace(dest)
    return dest
