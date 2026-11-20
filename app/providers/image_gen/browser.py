"""Imagem gerada pela tela de um site de conversa (Gemini), no Chrome que o dono abriu e logou (ADR 065).

O dono abre o Chrome com a porta de depuração e um perfil só para isto, e faz o login à mão:
    chromium --remote-debugging-port=9222 --user-data-dir=$HOME/.cache/chrome-imagens
O adaptador conecta pelo CDP (`[browser_image] cdp_url`), abre uma aba nova e faz um pedido por conversa nova:
liga a ferramenta de imagem, anexa as referências, digita o prompt, espera a imagem e grava os bytes.
Sem API e sem custo por chamada; os termos do site para uso automatizado da tela não foram conferidos e o
risco é da conta do dono (decisão de 2026-11-11, mantida em 2026-11-20). O Playwright (extra `navegador`)
só é carregado na primeira chamada.
"""

from __future__ import annotations

import hashlib
import importlib
from collections.abc import Callable
from typing import Any

from app.errors import PipelineError
from app.providers.base import ProviderInfo
from app.providers.image_gen import browser_page as steps
from app.providers.image_gen.browser_network import NetworkCapture
from app.providers.image_gen.constants.browser_constants import BrowserConstants
from app.providers.image_gen.image_bytes import write_image
from app.providers.image_gen.models.browser_site import BrowserSite
from app.providers.image_gen.models.cost_estimate import CostEstimate
from app.providers.image_gen.models.generated_image import GeneratedImage
from app.providers.image_gen.models.image_request import ImageRequest

Connect = Callable[[str], tuple[Any, Any]]  # cdp_url -> (sessão do Playwright, aba nova)


class BrowserImageGen:
    def __init__(
        self, name: str, site: BrowserSite, *, cdp_url: str, wait_s: int, connect: Connect | None = None
    ) -> None:
        self.info = ProviderInfo(name, remote=True, usd_per_call=0.0)
        self._site, self._cdp_url, self._wait_s = site, cdp_url, wait_s
        self._connect = connect or connect_over_cdp
        self._session: tuple[Any, Any, NetworkCapture] | None = None

    def estimate_cost(self, request: ImageRequest) -> CostEstimate:
        return CostEstimate(units=1.0, unit="imagem", usd=0.0)  # conta do dono, sem API

    def generate_image(self, request: ImageRequest) -> GeneratedImage:
        page, capture = self._page()
        name, site = self.info.name, self._site
        box = steps.open_prompt_box(name, page, site)
        steps.prepare(name, page, site)
        if request.refs:
            steps.attach(page, site, request.refs)
        before = page.locator(site.image).count()
        capture.mark()  # só respostas depois do envio: nunca o anexo de referência
        steps.send(page, site, box, request.prompt)
        steps.wait_new_image(name, page, site, before, self._wait_s)
        refs_sha = {hashlib.sha256(ref.read_bytes()).hexdigest() for ref in request.refs}
        data = steps.download(name, page, site, capture, refs_sha)
        path = write_image(name, request.out_path, data)
        return GeneratedImage(path=path, generator=name, origin=str(page.url))

    def map_page(self) -> list[str]:
        """O que cada seletor encontra e os botões e campos visíveis, para conferir e corrigir o toml."""
        page, _ = self._page()
        page.goto(self._site.url, wait_until="domcontentloaded")
        page.wait_for_timeout(BrowserConstants.MAP_PAUSE_MS)
        lines = [f"url atual: {page.url}"]
        for field in BrowserConstants.MAPPED_FIELDS:
            selector = getattr(self._site, field)
            if selector:
                lines.append(f"  {field:15} {page.locator(selector).count():3} elemento(s)  {selector}")
        lines.append("botões e campos visíveis (tag | type | aria-label | data-testid | texto):")
        lines.extend(f"  {line}" for line in page.evaluate(BrowserConstants.LIST_CONTROLS))
        return lines

    def close(self) -> None:
        if self._session is not None:
            playwright, page, _ = self._session
            self._session = None
            page.close()
            playwright.stop()

    def _page(self) -> tuple[Any, NetworkCapture]:
        if self._session is None:
            playwright, page = self._connect(self._cdp_url)
            self._session = (playwright, page, NetworkCapture(page))
        return self._session[1], self._session[2]


def connect_over_cdp(cdp_url: str) -> tuple[Any, Any]:
    """Conecta ao Chrome do dono e abre uma aba nova nele, sem baixar navegador."""
    try:
        api = importlib.import_module("playwright.sync_api")
    except ModuleNotFoundError as error:
        raise PipelineError("Playwright ausente: rode `uv sync --extra navegador`") from error
    playwright = api.sync_playwright().start()
    try:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
    except api.Error as error:
        playwright.stop()
        raise PipelineError(
            f"não conectei ao Chrome em {cdp_url}; abra-o com --remote-debugging-port e faça o login"
        ) from error
    return playwright, browser.contexts[0].new_page()
