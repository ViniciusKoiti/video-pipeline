"""Postiz público: credencial no header, respostas reduzidas e POST sem repetição automática."""

from __future__ import annotations

import json
import mimetypes
import re
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit
from uuid import uuid4

from app.providers.errors import ProviderError
from app.providers.http import USER_AGENT, TransportError, get_json, post_json_with_headers
from app.providers.postiz_validation import (
    parse_instant,
    reject_queued_duplicates,
    require_active_integrations,
    require_future_date,
    validate_schedule,
)


def _error(message: str = "resposta inesperada da API") -> ProviderError:
    return ProviderError("postiz", message)


def _fields(data: dict, names: tuple[str, ...]) -> dict:
    return {name: data[name] for name in names if name in data and isinstance(data[name], str)}


class PostizClient:
    def __init__(self, api_url: str, api_key: str) -> None:
        try:
            base = urlsplit(api_url)
            valid = (
                base.scheme == "https"
                and base.hostname
                and not base.username
                and not base.password
                and not base.query
                and not base.fragment
            )
            _ = base.port  # valida porta antes de qualquer requisição
        except ValueError:
            valid = False
        if not valid:
            raise _error("POSTIZ_API_URL deve ser HTTPS, sem credenciais, query ou fragmento")
        if not api_key.strip() or "\n" in api_key or "\r" in api_key:
            raise _error("POSTIZ_API_KEY ausente ou inválida")
        if api_key in unquote(api_url):
            raise _error("POSTIZ_API_URL não pode conter a credencial")
        self._api = api_url.rstrip("/") + "/public/v1"
        self._headers = {"Authorization": api_key}

    def _get(self, path: str) -> Any:
        try:
            return get_json(self._api + path, self._headers, 30).data
        except (TransportError, ValueError, TypeError) as error:
            status = getattr(error, "status", None)
            raise _error(f"consulta falhou (HTTP {status})" if status else "consulta falhou") from None

    def _post(self, path: str, payload: dict) -> Any:
        try:
            return post_json_with_headers(self._api + path, payload, self._headers, 60)
        except (TransportError, ValueError, TypeError) as error:
            status = getattr(error, "status", None)
            message = f"envio falhou (HTTP {status})" if status else "envio falhou"
            raise _error(message + "; consulte a fila antes de repetir") from None

    def integrations(self) -> list[dict]:
        data = self._get("/integrations")
        if not isinstance(data, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not isinstance(item.get("disabled"), bool)
            for item in data
        ):
            raise _error()
        return [
            {**_fields(item, ("id", "name", "identifier", "profile")), "disabled": item["disabled"]}
            for item in data
        ]

    def posts(self, start: str, end: str) -> dict:
        if parse_instant(start) >= parse_instant(end):
            raise _error("início do intervalo deve ser anterior ao fim")
        data = self._get("/posts?" + urlencode({"startDate": start, "endDate": end}))
        if not isinstance(data, dict) or not isinstance(data.get("posts"), list):
            raise _error()
        posts = []
        for item in data["posts"]:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("integration"), dict)
                or not all(isinstance(item.get(k), str) for k in ("id", "content", "publishDate", "state"))
                or not isinstance(item["integration"].get("id"), str)
            ):
                raise _error()
            post = _fields(item, ("id", "content", "publishDate", "state"))
            post["integration"] = _fields(
                item["integration"], ("id", "name", "providerIdentifier", "profile")
            )
            posts.append(post)
        return {"posts": posts}

    def connect(self, provider: str) -> dict:
        if not isinstance(provider, str) or not provider.strip():
            raise _error("informe o identificador da rede")
        data = self._get("/social/" + quote(provider, safe=""))
        url = data.get("url") if isinstance(data, dict) else None
        if not isinstance(url, str):
            raise _error()
        try:
            parsed = urlsplit(url)
            sensitive = {"access_token", "client_secret", "token", "code"}
            valid = (
                parsed.scheme == "https"
                and parsed.hostname
                and not parsed.username
                and not parsed.password
                and not parsed.fragment
                and not sensitive.intersection(k.lower() for k, _ in parse_qsl(parsed.query))
                and self._headers["Authorization"] not in unquote(url)
            )
            _ = parsed.port
        except ValueError:
            valid = False
        if not valid:
            raise _error("URL de conexão insegura na resposta")
        return {"url": url}

    def integration_settings(self, integration_id: str) -> dict:
        if not isinstance(integration_id, str) or not integration_id.strip():
            raise _error("informe o ID da integração")
        data = self._get("/integration-settings/" + quote(integration_id, safe=""))
        if not isinstance(data, dict):
            raise _error()
        return data

    def upload(self, path: Path) -> dict:
        media_type = mimetypes.guess_type(path.name)[0] or ""
        if not media_type.startswith(("image/", "video/")):
            raise _error("upload aceita somente arquivo de imagem ou vídeo")
        try:
            size = path.stat().st_size
            if not path.is_file() or not size:
                raise _error("arquivo de mídia deve existir e não estar vazio")
            boundary = uuid4().hex
            filename = re.sub(r"[^A-Za-z0-9._-]", "_", path.name)
            head = (
                f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                f"Content-Type: {media_type}\r\n\r\n"
            ).encode()
            tail = f"\r\n--{boundary}--\r\n".encode()
            with path.open("rb") as source:
                body = chain([head], iter(lambda: source.read(1 << 20), b""), [tail])
                request = urllib.request.Request(
                    self._api + "/upload",
                    data=body,
                    method="POST",
                    headers={
                        **self._headers,
                        "User-Agent": USER_AGENT,
                        "Content-Type": f"multipart/form-data; boundary={boundary}",
                        "Content-Length": str(len(head) + size + len(tail)),
                    },
                )
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = json.loads(response.read())
        except urllib.error.HTTPError as error:
            error.close()
            raise _error(f"upload falhou (HTTP {error.code})") from None
        except (OSError, ValueError, TypeError):
            raise _error("não foi possível enviar o arquivo de mídia") from None
        if not isinstance(data, dict) or not all(
            isinstance(data.get(k), str) and data[k] for k in ("id", "path")
        ):
            raise _error()
        return {"id": data["id"], "path": data["path"]}

    def check_schedule(self, payload: dict) -> dict:
        """Todas as defesas do agendamento, só com consultas: nada é criado (pacote de decisão)."""
        instant, requested = validate_schedule(payload, datetime.now(UTC))
        integrations = self.integrations()
        require_active_integrations(requested, integrations)
        queued = self.posts(
            (instant - timedelta(days=1)).isoformat(), (instant + timedelta(days=1)).isoformat()
        )
        reject_queued_duplicates(requested, queued["posts"])
        used = {integration_id for integration_id, _, _ in requested}
        return {
            "date": instant.isoformat(),
            "integrations": {i["id"]: i.get("name", i["id"]) for i in integrations if i["id"] in used},
        }

    def schedule(self, payload: dict) -> list[dict]:
        instant = parse_instant(self.check_schedule(payload)["date"])
        # shortcut: consulta/criação não são atômicas; usar idempotência do servidor com vários escritores.
        require_future_date(instant, datetime.now(UTC))
        data = self._post("/posts", payload)
        if (
            not isinstance(data, list)
            or not data
            or any(
                not isinstance(item, dict)
                or not all(isinstance(item.get(k), str) and item[k] for k in ("postId", "integration"))
                for item in data
            )
        ):
            raise _error("resposta inesperada após envio; consulte a fila antes de repetir")
        return [_fields(item, ("postId", "integration")) for item in data]
