"""Passos de um pedido na página de um site de conversa, só pelos seletores do `providers.toml` (ADR 065).

Login, captcha ou aviso de limite param a rodada (`AccessBlocked`); o adaptador não tenta passar por
verificação nem disfarça a automação. Pedido sem imagem vira `InvalidOutput` e a rodada segue.
"""

from __future__ import annotations

import base64
import contextlib
import time
from pathlib import Path
from typing import Any

from app.providers.errors import AccessBlocked, InvalidOutput
from app.providers.image_gen.browser_network import NetworkCapture, largest, matching
from app.providers.image_gen.constants.browser_constants import BrowserConstants as Constants
from app.providers.image_gen.models.browser_site import BrowserSite


def check_blocked(name: str, page: Any, site: BrowserSite) -> None:
    for fragment in site.block_urls:
        if fragment in page.url:
            raise AccessBlocked(name, f"o site foi para {fragment} (login ou verificação); rodada parada")
    for text in site.block_texts:
        if page.get_by_text(text, exact=False).first.is_visible():
            raise AccessBlocked(name, f"o site mostrou {text!r}; rodada parada")


def open_prompt_box(name: str, page: Any, site: BrowserSite) -> Any:
    page.goto(site.url, wait_until="domcontentloaded")
    box = page.locator(site.prompt_box).first
    try:
        box.wait_for(state="visible", timeout=Constants.PROMPT_BOX_TIMEOUT_MS)
    except Exception as error:  # noqa: BLE001 - o Playwright não é importado no topo
        check_blocked(name, page, site)
        raise InvalidOutput(name, f"não achei a caixa do prompt ({site.prompt_box})") from error
    check_blocked(name, page, site)
    return box


def prepare(name: str, page: Any, site: BrowserSite) -> None:
    """Cliques de preparo (ligar a ferramenta de imagem); o que já está ligado não é clicado de novo."""
    for selector in site.setup:
        check_blocked(name, page, site)  # o menu aberto pelo clique anterior pode trazer o aviso de limite
        target = page.locator(selector).first
        if target.get_attribute("aria-disabled") == "true":  # ferramenta desligada pelo site: limite de uso
            raise AccessBlocked(name, f"o site desativou {selector} (limite de uso?); rodada parada")
        if target.get_attribute("aria-checked") == "true":  # já ligado: clicar desligaria
            page.keyboard.press("Escape")
            continue
        target.click()
        page.wait_for_timeout(Constants.CLICK_PAUSE_MS)


def attach(page: Any, site: BrowserSite, refs: tuple[Path, ...]) -> None:
    files = [str(ref) for ref in refs]
    if not site.attach_clicks:
        page.locator(site.attach_input).first.set_input_files(files)
    else:
        with page.expect_file_chooser() as chooser:
            for selector in site.attach_clicks:
                page.locator(selector).first.click()
        chooser.value.set_files(files)
    page.wait_for_timeout(Constants.ATTACH_PAUSE_MS)


def send(page: Any, site: BrowserSite, box: Any, prompt: str) -> None:
    box.click()
    page.keyboard.insert_text(prompt)
    if site.send:
        page.locator(site.send).first.click()
    else:
        page.keyboard.press("Enter")


def wait_new_image(name: str, page: Any, site: BrowserSite, before: int, wait_s: int) -> None:
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        page.wait_for_timeout(Constants.POLL_MS)
        check_blocked(name, page, site)
        busy = bool(site.busy) and page.locator(site.busy).first.is_visible()
        if not busy and page.locator(site.image).count() > before:
            return
    raise InvalidOutput(name, f"sem imagem nova em {wait_s} s")


def download(name: str, page: Any, site: BrowserSite, capture: NetworkCapture, refs_sha: set[str]) -> bytes:
    if site.download == "button":
        with page.expect_download() as file:
            page.locator(site.download_button).last.click()
        return Path(file.value.path()).read_bytes()
    for _ in range(Constants.LOAD_TRIES):
        page.wait_for_timeout(Constants.POLL_MS)
        # imagem preguiçosa só carrega quando entra na tela; sem ela, tenta no próximo giro
        with contextlib.suppress(Exception):
            page.locator(site.image).last.scroll_into_view_if_needed(timeout=Constants.SCROLL_TIMEOUT_MS)
        try:
            encoded = page.locator(site.image).evaluate_all(Constants.READ_IMAGE)
        except Exception:  # noqa: BLE001 - canvas "tainted": imagem de outra origem sem CORS
            data = _from_network(page, site, capture, refs_sha)
        else:
            data = base64.b64decode(encoded) if encoded else None
        if data:
            return data
    raise InvalidOutput(name, f"nenhuma imagem carregada com {Constants.MIN_SIDE} px ou mais")


def _from_network(page: Any, site: BrowserSite, capture: NetworkCapture, refs_sha: set[str]) -> bytes | None:
    src = page.locator(site.image).evaluate_all(Constants.LAST_IMAGE)
    return largest(matching(src, capture.fresh()), capture.body, refs_sha) if src else None
