"""Validação de agendamentos Postiz, sem transporte nem acesso a credenciais."""

from __future__ import annotations

from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any

from app.providers.errors import ProviderError

ScheduleKey = tuple[str, datetime, str]


def _error(message: str) -> ProviderError:
    return ProviderError("postiz", message)


def parse_instant(value: Any) -> datetime:
    try:
        instant = datetime.fromisoformat(value)
        if instant.utcoffset() is None:
            raise ValueError
        return instant.astimezone(UTC)
    except (TypeError, ValueError):
        raise _error("data deve ser ISO 8601 com fuso horário") from None


def require_future_date(instant: datetime, now: datetime) -> None:
    if instant <= now:
        raise _error("a data do agendamento deve estar no futuro")


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in {"p", "div", "br", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "br", "li"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def visible_text(content: str) -> str:
    parser = _VisibleText()
    parser.feed(content)
    parser.close()
    return " ".join("".join(parser.parts).split())


def validate_schedule(payload: dict, now: datetime) -> tuple[datetime, set[ScheduleKey]]:
    if not isinstance(payload, dict) or payload.get("type") != "schedule" or "id" in payload:
        raise _error("somente novos agendamentos (type=schedule) são aceitos")
    instant = parse_instant(payload.get("date"))
    require_future_date(instant, now)
    posts = payload.get("posts")
    if not isinstance(posts, list) or not posts:
        raise _error("informe ao menos um post")
    requested = set()
    for post in posts:
        if not isinstance(post, dict) or "id" in post:
            raise _error("post deve ser novo, sem ID existente")
        integration = post.get("integration")
        integration_id = integration.get("id") if isinstance(integration, dict) else None
        if not isinstance(integration_id, str) or not integration_id.strip():
            raise _error("cada post precisa do ID de integração")
        values = post.get("value")
        if not isinstance(values, list) or not values:
            raise _error("cada post precisa de value com conteúdo ou mídia")
        for value in values:
            if not isinstance(value, dict) or "id" in value or not isinstance(value.get("content"), str):
                raise _error("value precisa de content textual e não pode atualizar ID existente")
            images = value.get("image", [])
            if not isinstance(images, list) or any(
                not isinstance(media, dict)
                or not all(isinstance(media.get(k), str) and media[k].strip() for k in ("id", "path"))
                for media in images
            ):
                raise _error("mídia precisa do id e path retornados pelo upload")
            if not value["content"].strip() and not images:
                raise _error("post não pode ter conteúdo e mídia vazios")
        key = (integration_id, instant, visible_text(values[0]["content"]))
        if key in requested:
            raise _error("agendamento duplicado no payload")
        requested.add(key)
    return instant, requested


def require_active_integrations(requested: set[ScheduleKey], integrations: list[dict]) -> None:
    active = {item["id"] for item in integrations if not item["disabled"]}
    if any(integration_id not in active for integration_id, _, _ in requested):
        raise _error("integração inexistente ou desativada")


def reject_queued_duplicates(requested: set[ScheduleKey], posts: list[dict]) -> None:
    for post in posts:
        if post.get("state", "").upper() != "QUEUE":
            continue
        key = (post["integration"]["id"], parse_instant(post["publishDate"]), visible_text(post["content"]))
        if key in requested:
            raise _error("já existe agendamento com integração, data e conteúdo iguais")
