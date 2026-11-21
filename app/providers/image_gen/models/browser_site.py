from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class BrowserSite:
    """Seletores de um site de conversa que gera imagem (`[browser_image.sites.<nome>]`, ADR 065)."""

    url: str  # página de conversa nova
    prompt_box: str  # campo onde o prompt é digitado
    image: str  # imagens geradas dentro das respostas (a última é a baixada)
    send: str = ""  # botão de enviar; vazio = tecla Enter
    setup: tuple[str, ...] = ()  # cliques antes de tudo, em ordem (ex.: ligar a ferramenta de imagem)
    attach_input: str = "input[type='file']"  # recebe as referências quando `attach_clicks` está vazio
    attach_clicks: tuple[str, ...] = ()  # cliques que abrem o seletor de arquivos do sistema
    busy: str = ""  # elemento visível enquanto o site ainda gera
    download: Literal["image", "button"] = "image"  # lê a imagem mostrada ou clica no download do site
    download_button: str = ""
    block_urls: tuple[str, ...] = ()  # trechos de URL de login ou verificação: a rodada para
    block_texts: tuple[str, ...] = ()  # textos de limite, captcha ou recusa de conta: a rodada para
