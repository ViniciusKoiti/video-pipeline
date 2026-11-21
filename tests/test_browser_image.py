"""Adaptador de imagem pela tela de um site (ADR 065), com uma página falsa no lugar do Playwright."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.bootstrap import ConfigurationError, build_context
from app.providers.errors import AccessBlocked, InvalidOutput
from app.providers.image_gen.browser import BrowserImageGen
from app.providers.image_gen.browser_network import largest, matching
from app.providers.image_gen.constants.browser_constants import BrowserConstants
from app.providers.image_gen.image_bytes import write_image
from app.providers.image_gen.models.browser_site import BrowserSite
from app.providers.image_gen.models.image_request import ImageRequest
from app.settings import load_settings
from tests.fakes import make_root

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64
SITE = BrowserSite(
    url="https://site.test/app",
    prompt_box="#caixa",
    image="article img",
    send="#enviar",
    setup=("#ferramentas", "#criar-imagem"),
    busy="#parar",
    block_urls=("/login",),
    block_texts=("atingiu o limite",),
)


class Locator:
    def __init__(self, page: Page, selector: str) -> None:
        self.page, self.selector = page, selector
        self.first = self.last = self

    def count(self) -> int:
        return self.page.counts.get(self.selector, 0)

    def wait_for(self, state: str, timeout: int) -> None:
        if self.selector not in self.page.present:
            raise TimeoutError(self.selector)

    def click(self) -> None:
        self.page.clicks.append(self.selector)
        if self.selector == SITE.send:  # o site responde com a imagem
            self.page.counts[SITE.image] = self.page.counts.get(SITE.image, 0) + 1

    def get_attribute(self, name: str) -> str | None:
        return self.page.attributes.get((self.selector, name))

    def is_visible(self) -> bool:
        return self.selector in self.page.visible

    def evaluate_all(self, script: str) -> str | None:
        return base64.b64encode(PNG).decode() if script == BrowserConstants.READ_IMAGE else None

    def set_input_files(self, files: list[str]) -> None:
        self.page.attached = files

    def scroll_into_view_if_needed(self, timeout: int) -> None:
        return None


class Page:
    def __init__(self) -> None:
        self.url, self.clicks, self.typed, self.keys, self.attached = "", [], [], [], []  # type: ignore[var-annotated]
        self.present = {SITE.prompt_box, SITE.image}
        self.counts: dict[str, int] = {SITE.prompt_box: 1}
        self.attributes: dict[tuple[str, str], str] = {}
        self.visible: set[str] = set()
        self.texts: set[str] = set()
        self.closed = False
        self.keyboard = SimpleNamespace(insert_text=self.typed.append, press=self.keys.append)
        self.context = SimpleNamespace(
            new_cdp_session=lambda page: SimpleNamespace(send=lambda *a: {}, on=lambda *a: None)
        )

    def goto(self, url: str, wait_until: str) -> None:
        self.url = url

    def locator(self, selector: str) -> Locator:
        return Locator(self, selector)

    def get_by_text(self, text: str, exact: bool) -> Any:
        return SimpleNamespace(first=SimpleNamespace(is_visible=lambda: text in self.texts))

    def wait_for_timeout(self, ms: int) -> None:
        return None

    def evaluate(self, script: str) -> list[str]:
        return ["button | submit | Enviar mensagem |  | "]

    def close(self) -> None:
        self.closed = True


def adapter(page: Page, connections: list[str] | None = None, wait_s: int = 5) -> BrowserImageGen:
    calls = [] if connections is None else connections
    playwright = SimpleNamespace(stop=lambda: calls.append("stop"))

    def connect(url: str) -> tuple[Any, Any]:
        calls.append(url)
        return playwright, page

    return BrowserImageGen("gemini", SITE, cdp_url="http://127.0.0.1:9222", wait_s=wait_s, connect=connect)


def test_generates_one_image_per_new_conversation_and_keeps_the_conversation(tmp_path: Path) -> None:
    (tmp_path / "folha.png").write_bytes(PNG)
    page = Page()
    provider = adapter(page)
    image = provider.generate_image(
        ImageRequest("um pátio", tmp_path / "s03", refs=(tmp_path / "folha.png",))
    )
    assert image.path == tmp_path / "s03.png" and image.path.read_bytes() == PNG
    assert (image.generator, image.generation, image.origin) == ("gemini", None, "https://site.test/app")
    assert page.clicks == ["#ferramentas", "#criar-imagem", "#caixa", "#enviar"] and page.typed == [
        "um pátio"
    ]
    assert page.attached == [str(tmp_path / "folha.png")]
    assert provider.estimate_cost(ImageRequest("x", tmp_path / "x")).usd == 0


def test_tool_already_on_is_not_clicked_off(tmp_path: Path) -> None:
    page = Page()
    page.attributes[("#criar-imagem", "aria-checked")] = "true"
    adapter(page).generate_image(ImageRequest("x", tmp_path / "a"))
    assert "#criar-imagem" not in page.clicks and page.keys == ["Escape"]


@pytest.mark.parametrize(
    ("setup", "message"),
    [
        (lambda p: p.texts.add("atingiu o limite"), "o site mostrou 'atingiu o limite'"),
        (
            lambda p: p.attributes.update({("#criar-imagem", "aria-disabled"): "true"}),
            "desativou #criar-imagem",
        ),
    ],
)
def test_limit_or_disabled_tool_blocks_the_round(tmp_path: Path, setup: Any, message: str) -> None:
    page = Page()
    setup(page)
    with pytest.raises(AccessBlocked, match=message):
        adapter(page).generate_image(ImageRequest("x", tmp_path / "a"))
    assert not list(tmp_path.iterdir())


def test_login_page_blocks_even_without_the_prompt_box(tmp_path: Path) -> None:
    page = Page()
    page.present.discard(SITE.prompt_box)
    provider = adapter(page)
    with pytest.raises(InvalidOutput, match=r"não achei a caixa do prompt \(#caixa\)"):
        provider.generate_image(ImageRequest("x", tmp_path / "a"))
    page.goto = lambda url, wait_until: setattr(page, "url", "https://site.test/login")  # type: ignore[method-assign]
    with pytest.raises(AccessBlocked, match="login ou verificação"):
        provider.generate_image(ImageRequest("x", tmp_path / "a"))


def test_no_new_image_in_time_is_an_invalid_output(tmp_path: Path) -> None:
    with pytest.raises(InvalidOutput, match="sem imagem nova em 0 s"):
        adapter(Page(), wait_s=0).generate_image(ImageRequest("x", tmp_path / "a"))


def test_connects_once_and_close_releases_the_browser(tmp_path: Path) -> None:
    calls: list[str] = []
    page = Page()
    provider = adapter(page, calls)
    provider.generate_image(ImageRequest("x", tmp_path / "a"))
    provider.generate_image(ImageRequest("y", tmp_path / "b"))
    provider.close()
    provider.close()
    assert calls == ["http://127.0.0.1:9222", "stop"] and page.closed


def test_map_page_lists_what_each_selector_finds() -> None:
    lines = adapter(Page()).map_page()
    assert lines[0] == "url atual: https://site.test/app"
    assert "  prompt_box        1 elemento(s)  #caixa" in lines
    assert lines[-1] == "  button | submit | Enviar mensagem |  | "


def test_network_fallback_takes_the_largest_new_body_that_is_not_a_reference() -> None:
    src = "https://lh3.test/gg-dl/abc=s1024"
    responses = [
        ("1", "https://lh3.test/rd-gg-dl/abc=s512"),
        ("2", "https://outro.test/x"),
        ("3", "https://lh3.test/rd-gg-dl/abc"),
    ]
    assert matching(src, responses) == ["1", "3"]
    assert matching("https://cdn.test/img?w=10", [("9", "https://cdn.test/img?w=2000")]) == ["9"]
    bodies = {"1": b"ref", "3": b"imagem-inteira", "4": b"maior-porem-fora"}
    refs = {hashlib.sha256(b"ref").hexdigest()}
    assert largest(["1", "3"], bodies.get, refs) == b"imagem-inteira"
    assert largest(["1"], bodies.get, refs) is None


def test_image_bytes_keep_the_type_and_refuse_a_login_page(tmp_path: Path) -> None:
    assert write_image("gemini", tmp_path / "a", b"RIFF0000WEBP").name == "a.webp"
    with pytest.raises(InvalidOutput, match="não é PNG, JPEG nem WebP"):
        write_image("gemini", tmp_path / "b", b"<html>entre na sua conta</html>")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.webp"]


def test_project_config_turns_on_only_gemini(tmp_path: Path) -> None:
    settings = load_settings(make_root(tmp_path), environ={})
    assert settings.providers.image_gen == "browser_image"
    assert {name: site.enabled for name, site in settings.browser_image.sites.items()} == {
        "gemini": True,
        "chatgpt": False,
    }
    provider = build_context(make_root(tmp_path), environ={}).image_gen
    assert isinstance(provider, BrowserImageGen) and provider.info.name == "gemini"


def with_site(tmp_path: Path, site: str) -> Path:
    config = make_root(tmp_path) / "config" / "providers.toml"
    config.write_text(config.read_text().replace('site = "gemini"', f'site = "{site}"', 1))
    return tmp_path


@pytest.mark.parametrize(
    ("site", "message"),
    [("chatgpt", "o site 'chatgpt' está desligado"), ("midjourney", r"sem bloco .* \(há: chatgpt, gemini\)")],
)
def test_disabled_or_unknown_site_stops_before_the_browser(tmp_path: Path, site: str, message: str) -> None:
    root = with_site(tmp_path, site)
    with pytest.raises(ConfigurationError, match=message):
        _ = build_context(root, environ={}).image_gen
