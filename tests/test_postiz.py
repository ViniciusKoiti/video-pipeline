"""Contrato público do Postiz, sem rede nem credencial real."""

from __future__ import annotations

import copy
import io
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from app.providers import postiz
from app.providers.errors import ProviderError
from app.providers.http import JsonResponse, TransportError
from app.providers.postiz import PostizClient

API = "https://postiz.example/api"
KEY = "segredo-somente-no-header"
DATE = "2099-10-15T15:30:00.000Z"


def payload() -> dict:
    return {
        "type": "schedule",
        "date": DATE,
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": "instagram-id"},
                "value": [
                    {
                        "content": "Nabote: veja o episódio.",
                        "image": [
                            {"id": "media-id", "path": "https://postiz.example/uploads/reel.mp4"},
                        ],
                    }
                ],
                "settings": {"__type": "instagram-standalone", "post_type": "post"},
            }
        ],
    }


@pytest.fixture
def remote(monkeypatch):
    state = {
        "integrations": [
            {
                "id": "instagram-id",
                "name": "Nabote",
                "identifier": "instagram-standalone",
                "disabled": False,
                "profile": "nabote",
                "token": KEY,
                "headers": {"secret": KEY},
            }
        ],
        "posts": {"posts": []},
        "get": [],
        "post": [],
    }

    def get(url, headers, timeout):
        assert headers == {"Authorization": KEY}
        assert timeout == 30
        state["get"].append(url)
        path = urlsplit(url).path
        if path.endswith("/integrations"):
            result = state["integrations"]
        elif path.endswith("/posts"):
            result = state["posts"]
        elif "/social/" in path:
            result = state.get(
                "connect", {"url": "https://instagram.example/oauth?state=opaque&client_id=123"}
            )
        else:
            result = {"post_type": ["post", "story"]}
        return JsonResponse(result, {"authorization": KEY})

    def post(url, body, headers, timeout):
        assert headers == {"Authorization": KEY}
        assert timeout == 60
        state["post"].append((url, body))
        return [{"postId": "scheduled-id", "integration": "instagram-id", "token": KEY}]

    monkeypatch.setattr(postiz, "get_json", get)
    monkeypatch.setattr(postiz, "post_json_with_headers", post)
    return state


@pytest.mark.parametrize(
    "url",
    [
        "http://postiz.example/api",
        "https://user:password@postiz.example/api",
        "https://postiz.example/api?token=secret",
        "https://postiz.example/api#secret",
        "https://postiz.example:bad/api",
        "https://postiz.example/" + KEY,
    ],
)
def test_invalid_base_url_is_rejected_without_request(url):
    with pytest.raises(ProviderError) as raised:
        PostizClient(url, KEY)
    assert KEY not in str(raised.value) and url not in str(raised.value)


def test_http_auth_and_safe_projections(remote):
    client = PostizClient(API + "/", KEY)
    assert client.integrations() == [
        {
            "id": "instagram-id",
            "name": "Nabote",
            "identifier": "instagram-standalone",
            "disabled": False,
            "profile": "nabote",
        }
    ]
    remote["posts"]["posts"] = [
        {
            "id": "post-id",
            "content": "Nabote",
            "publishDate": DATE,
            "state": "QUEUE",
            "token": KEY,
            "integration": {
                "id": "instagram-id",
                "name": "Nabote",
                "providerIdentifier": "instagram-standalone",
                "token": KEY,
            },
        }
    ]
    result = client.posts("2099-10-15T12:30:00-03:00", "2099-10-16T12:30:00-03:00")
    assert result["posts"][0]["integration"] == {
        "id": "instagram-id",
        "name": "Nabote",
        "providerIdentifier": "instagram-standalone",
    }
    assert KEY not in json.dumps(result)
    assert remote["get"][0] == API + "/public/v1/integrations"
    assert parse_qs(urlsplit(remote["get"][1]).query)["startDate"] == ["2099-10-15T12:30:00-03:00"]
    assert KEY not in repr(client)


def test_connect_and_settings_quote_ids(remote):
    client = PostizClient(API, KEY)
    assert client.connect("instagram-standalone")["url"].startswith("https://instagram.example/")
    assert client.integration_settings("id/with?punctuation") == {"post_type": ["post", "story"]}
    assert remote["get"][-1].endswith("/integration-settings/id%2Fwith%3Fpunctuation")


@pytest.mark.parametrize(
    "start,end",
    [
        ("2099-10-15", "2099-10-16T00:00:00Z"),
        ("2099-10-15T12:30:00", "2099-10-16T00:00:00Z"),
        ("2099-10-16T00:00:00Z", "2099-10-15T00:00:00Z"),
        ("2099-10-15T00:00:00Z", "2099-10-15T00:00:00Z"),
    ],
)
def test_invalid_posts_interval_is_rejected_before_network(remote, start, end):
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).posts(start, end)
    assert remote["get"] == []


def test_invalid_disabled_type_is_rejected(remote):
    remote["integrations"][0]["disabled"] = "false"
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).schedule(payload())
    assert remote["post"] == []


def test_invalid_queue_state_is_rejected(remote):
    remote["posts"]["posts"] = [
        {
            "id": "bad-response",
            "content": "Nabote",
            "publishDate": DATE,
            "state": True,
            "integration": {"id": "instagram-id"},
        }
    ]
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).schedule(payload())
    assert remote["post"] == []


@pytest.mark.parametrize(
    "url",
    [
        "http://oauth.example/connect",
        "https://oauth.example/?access_token=hidden",
        "https://oauth.example/?client_secret=hidden",
        "https://oauth.example/?token=hidden",
        "https://oauth.example/?code=hidden",
        "https://oauth.example/#access_token=hidden",
        "https://user:password@oauth.example/connect",
        "https://oauth.example/?state=" + KEY,
    ],
)
def test_connect_rejects_credentials_in_returned_url(remote, url):
    remote["connect"] = {"url": url}
    with pytest.raises(ProviderError) as raised:
        PostizClient(API, KEY).connect("instagram")
    assert KEY not in str(raised.value) and "oauth.example" not in str(raised.value)


@pytest.mark.parametrize("method", ["get", "post"])
def test_http_errors_do_not_leak_key_url_or_remote_body(monkeypatch, method):
    calls = []

    def fail(*args):
        calls.append(args)
        raise TransportError(401, API + " token=" + KEY)

    monkeypatch.setattr(postiz, "get_json" if method == "get" else "post_json_with_headers", fail)
    client = PostizClient(API, KEY)
    with pytest.raises(ProviderError) as raised:
        if method == "get":
            client.integrations()
        else:
            client._post("/posts", payload())
    assert len(calls) == 1
    assert "401" in str(raised.value)
    assert KEY not in str(raised.value) and API not in str(raised.value)


@pytest.mark.parametrize(
    "changes",
    [
        {"type": "now"},
        {"type": "draft"},
        {"id": "existing"},
        {"date": "2099-10-15T15:30:00"},
        {"date": "2000-01-01T15:30:00Z"},
        {"date": "bad"},
        {"posts": []},
    ],
)
def test_invalid_schedule_is_rejected_before_network(remote, changes):
    body = {**payload(), **changes}
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).schedule(body)
    assert remote["get"] == [] and remote["post"] == []


@pytest.mark.parametrize(
    "change",
    [
        {"id": "existing-post"},
        {"integration": {}},
        {"value": []},
        {"value": [{"content": "", "image": []}]},
        {"value": [{"content": "Nabote", "image": [{"id": "missing-path"}]}]},
        {"value": [{"id": "existing-value", "content": "Nabote"}]},
    ],
)
def test_invalid_post_is_rejected_before_network(remote, change):
    body = payload()
    body["posts"][0].update(change)
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).schedule(body)
    assert remote["get"] == [] and remote["post"] == []


@pytest.mark.parametrize("disabled", [True, "missing"])
def test_schedule_rejects_disabled_or_unknown_integration(remote, disabled):
    remote["integrations"] = [] if disabled == "missing" else [{"id": "instagram-id", "disabled": True}]
    with pytest.raises(ProviderError, match="inexistente ou desativada"):
        PostizClient(API, KEY).schedule(payload())
    assert remote["post"] == []


def test_duplicate_queue_uses_equivalent_instant_not_date_string(remote):
    remote["posts"]["posts"] = [
        {
            "id": "already-scheduled",
            "content": payload()["posts"][0]["value"][0]["content"],
            "publishDate": "2099-10-15T12:30:00-03:00",
            "state": "QUEUE",
            "integration": {"id": "instagram-id"},
        }
    ]
    with pytest.raises(ProviderError, match="já existe agendamento"):
        PostizClient(API, KEY).schedule(payload())
    assert remote["post"] == []


@pytest.mark.parametrize("incoming_html", [False, True])
def test_duplicate_queue_matches_visible_html_to_plain_text(remote, incoming_html):
    html = (
        "<div><p>Oi <b>Nabote</b> &amp; amigos &lt;3</p><p>Segundo<br>Terceiro</p>"
        "<ul><li>Quarto</li></ul></div>\n"
    )
    plain = "Oi Nabote & amigos <3\nSegundo\nTerceiro\nQuarto"
    body = payload()
    body["posts"][0]["value"][0]["content"] = html if incoming_html else plain
    original = copy.deepcopy(body)
    remote["posts"]["posts"] = [
        {
            "id": "already-scheduled",
            "content": plain if incoming_html else html,
            "publishDate": DATE,
            "state": "QUEUE",
            "integration": {"id": "instagram-id"},
        }
    ]
    with pytest.raises(ProviderError, match="já existe agendamento"):
        PostizClient(API, KEY).schedule(body)
    assert body == original
    assert remote["post"] == []


def test_distinct_visible_text_preserves_literal_characters_and_sends_original(remote):
    body = payload()
    body["posts"][0]["value"][0]["content"] = "Oi Nabote & amigos <3\nSegundo"
    original = copy.deepcopy(body)
    remote["posts"]["posts"] = [
        {
            "id": "different-post",
            "content": "<p>Oi <b>Nabote</b> &amp; amigos &lt;4</p><p>Segundo</p>",
            "publishDate": DATE,
            "state": "QUEUE",
            "integration": {"id": "instagram-id"},
        }
    ]
    PostizClient(API, KEY).schedule(body)
    assert body == original
    assert remote["post"] == [(API + "/public/v1/posts", original)]


def test_duplicate_in_same_payload_is_rejected_before_network(remote):
    body = payload()
    body["posts"].append(copy.deepcopy(body["posts"][0]))
    with pytest.raises(ProviderError, match="duplicado no payload"):
        PostizClient(API, KEY).schedule(body)
    assert remote["get"] == [] and remote["post"] == []


def test_schedule_sends_native_payload_once_and_returns_only_created_ids(remote):
    body = payload()
    original = copy.deepcopy(body)
    assert PostizClient(API, KEY).schedule(body) == [
        {"postId": "scheduled-id", "integration": "instagram-id"}
    ]
    assert body == original
    assert remote["post"] == [(API + "/public/v1/posts", original)]
    assert len(remote["get"]) == 2


def test_schedule_rechecks_future_date_after_remote_queries(remote, monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            minute = 31 if remote["get"] else 29
            return datetime(2099, 10, 15, 15, minute, tzinfo=UTC)

    monkeypatch.setattr(postiz, "datetime", Clock)
    with pytest.raises(ProviderError, match="data do agendamento deve estar no futuro"):
        PostizClient(API, KEY).schedule(payload())
    assert len(remote["get"]) == 2
    assert remote["post"] == []


def test_upload_streams_binary_and_sanitizes_filename(remote, monkeypatch, tmp_path: Path):
    media = tmp_path / 'reel"\r\n.mp4'
    binary = b"\x00\xff\x80video\x00" * 100
    media.write_bytes(binary)
    received = []

    def upload(request, timeout):
        assert request.full_url == API + "/public/v1/upload"
        assert request.get_header("Authorization") == KEY
        assert timeout == 120
        body = b"".join(request.data)
        assert int(request.get_header("Content-length")) == len(body)
        assert b'filename="reel___.mp4"' in body
        assert binary in body and b"Content-Type: video/mp4\r\n" in body
        received.append(request)
        return io.BytesIO(
            json.dumps({"id": "media-id", "path": "https://postiz.example/reel.mp4", "token": KEY}).encode()
        )

    monkeypatch.setattr(postiz.urllib.request, "urlopen", upload)
    assert PostizClient(API, KEY).upload(media) == {
        "id": "media-id",
        "path": "https://postiz.example/reel.mp4",
    }
    assert len(received) == 1


@pytest.mark.parametrize("name,data", [("empty.mp4", b""), ("secret.env", b"secret")])
def test_upload_rejects_empty_or_nonmedia_files(tmp_path: Path, monkeypatch, name, data):
    path = tmp_path / name
    path.write_bytes(data)
    monkeypatch.setattr(
        postiz.urllib.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("rede inesperada")
    )
    with pytest.raises(ProviderError):
        PostizClient(API, KEY).upload(path)


def test_upload_http_error_is_safe_and_is_not_retried(monkeypatch, tmp_path: Path):
    path = tmp_path / "reel.mp4"
    path.write_bytes(b"video")
    calls = []

    def fail(*args, **kwargs):
        calls.append(args)
        raise urllib.error.HTTPError(API + KEY, 403, KEY, {}, io.BytesIO(KEY.encode()))

    monkeypatch.setattr(postiz.urllib.request, "urlopen", fail)
    with pytest.raises(ProviderError) as raised:
        PostizClient(API, KEY).upload(path)
    assert "403" in str(raised.value) and KEY not in str(raised.value) and API not in str(raised.value)
    assert len(calls) == 1
