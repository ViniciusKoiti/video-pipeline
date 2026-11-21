"""Composição da imagem pela tela de um site (ADR 065): escolhe o site do `[browser_image]` e monta o adapter.

Site sem bloco ou com `enabled = false` para aqui, antes de abrir o navegador. O adapter é importado dentro
da fábrica, como as outras do registro."""

from __future__ import annotations

from app.bootstrap.registry import ConfigurationError
from app.providers.image_gen.base import ImageGenProvider
from app.settings import Settings


def build_browser_image(settings: Settings) -> ImageGenProvider:
    from app.providers.image_gen.browser import BrowserImageGen
    from app.providers.image_gen.models.browser_site import BrowserSite

    config = settings.browser_image
    block = f"[browser_image.sites.{config.site}]"
    site = config.sites.get(config.site)
    if site is None:
        known = ", ".join(sorted(config.sites)) or "nenhum"
        raise ConfigurationError(f"browser_image.site = {config.site!r} sem bloco {block} (há: {known})")
    if not site.enabled:
        raise ConfigurationError(
            f"o site {config.site!r} está desligado (enabled = false em {block}): "
            "ligar só depois de conferir os termos de automação dele"
        )
    selectors = BrowserSite(**site.model_dump(exclude={"enabled"}))
    return BrowserImageGen(config.site, selectors, cdp_url=config.cdp_url, wait_s=config.wait_s)
