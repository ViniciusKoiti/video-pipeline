from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model
from app.settings.models.browser_site_settings import BrowserSiteSettings


class BrowserImageSettings(_Model):
    """`[browser_image]`: imagem gerada pela tela de um site, no Chrome do dono (ADR 065)."""

    cdp_url: str = "http://127.0.0.1:9222"  # porta de depuração do Chrome aberto pelo dono
    site: str = "gemini"  # o site usado; precisa de bloco em `sites` com enabled = true
    interval_s: int = Field(default=45, ge=0)  # pausa entre pedidos: uma imagem por vez
    wait_s: int = Field(default=180, gt=0)  # espera máxima de cada imagem
    sites: dict[str, BrowserSiteSettings] = {}
