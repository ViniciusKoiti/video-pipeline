"""Constantes do adaptador de imagem pela tela de um site (ADR 065); dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final


class BrowserConstants:
    MIN_SIDE: Final[int] = 256  # imagem menor que isto é ícone ou miniatura, não a gerada
    PROMPT_BOX_TIMEOUT_MS: Final[int] = 30_000
    CLICK_PAUSE_MS: Final[int] = 800
    ATTACH_PAUSE_MS: Final[int] = 3_000
    POLL_MS: Final[int] = 2_000
    LOAD_TRIES: Final[int] = 45  # a imagem aparece na conversa antes de terminar de carregar
    SCROLL_TIMEOUT_MS: Final[int] = 2_000
    MAP_PAUSE_MS: Final[int] = 5_000
    # buffers da escuta de rede (CDP): a imagem original chega a dezenas de MB
    NETWORK_BUFFERS: Final = MappingProxyType(
        {"maxTotalBufferSize": 200_000_000, "maxResourceBufferSize": 50_000_000}
    )
    GEMINI_DOWNLOAD_PATH: Final[str] = "/gg-dl/"  # Gemini: <img> em gg-dl, resposta em rd-gg-dl
    MAPPED_FIELDS: Final = ("prompt_box", "send", "attach_input", "image", "busy", "download_button")
    # Última imagem carregada da resposta, em base64. Lê o arquivo pelo endereço; se o endereço já não
    # responde (blob revogado), copia os pixels já decodificados para um PNG.
    READ_IMAGE: Final[str] = f"""async (imgs) => {{
  const boas = imgs.filter(i => i.complete && i.naturalWidth >= {MIN_SIDE});
  if (!boas.length) return null;
  const img = boas[boas.length - 1];
  const base64 = async (blob) => {{
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let texto = '';
    for (let i = 0; i < bytes.length; i += 32768) {{
      texto += String.fromCharCode(...bytes.subarray(i, i + 32768));
    }}
    return btoa(texto);
  }};
  try {{
    return await base64(await (await fetch(img.src)).blob());
  }} catch (erro) {{
    const tela = document.createElement('canvas');
    tela.width = img.naturalWidth;
    tela.height = img.naturalHeight;
    tela.getContext('2d').drawImage(img, 0, 0);
    return await base64(await new Promise(feito => tela.toBlob(feito, 'image/png')));
  }}
}}"""
    LAST_IMAGE: Final[str] = f"""(imgs) => {{
  const boas = imgs.filter(i => i.complete && i.naturalWidth >= {MIN_SIDE});
  return boas.length ? (boas[boas.length - 1].currentSrc || boas[boas.length - 1].src) : null;
}}"""
    LIST_CONTROLS: Final[str] = """() => [...document.querySelectorAll(
    'button, [role=button], input, textarea, [contenteditable=true]')]
  .filter(e => e.offsetParent !== null || e.type === 'file')
  .map(e => [e.tagName.toLowerCase(), e.type || '', e.getAttribute('aria-label') || '',
             e.getAttribute('data-testid') || '', (e.innerText || '').trim().slice(0, 40)].join(' | '))"""
    SIGNATURES: Final = ((b"\x89PNG", ".png"), (b"\xff\xd8\xff", ".jpg"), (b"RIFF", ".webp"))
