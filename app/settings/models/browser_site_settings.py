from __future__ import annotations

from typing import Literal

from app.settings.models._settings_model import _Model


class BrowserSiteSettings(_Model):
    """Um bloco `[browser_image.sites.<nome>]`: os seletores da tela do site (ADR 065)."""

    enabled: bool = False  # site desligado não roda: termos de automação conferidos pelo dono antes
    url: str
    prompt_box: str
    image: str
    send: str = ""
    setup: tuple[str, ...] = ()
    attach_input: str = "input[type='file']"
    attach_clicks: tuple[str, ...] = ()
    busy: str = ""
    download: Literal["image", "button"] = "image"
    download_button: str = ""
    block_urls: tuple[str, ...] = ()
    block_texts: tuple[str, ...] = ()
