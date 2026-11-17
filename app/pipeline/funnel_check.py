"""Estágio do funil no roteiro (ADR 026 e emenda de 2026-11-16).

A chamada final (`cta`) pede o que o estágio pede e é dita na última cena; quando não é assim, o `vp check`
dá erro. Antes era alerta, e se perdia entre os outros: o `vazio-de-ter-tudo` (2026-11-15) saiu com a pergunta
dos comentários no lugar da chamada do topo. No vídeo longo, a pergunta para os comentários (`engagement`) vem
na última cena, antes da chamada; nos Shorts, um pedido só (ADR 028). A conferência é por palavras: acento,
caixa, pontuação e pausas não contam. Se a chamada funciona é julgamento do gate 2.
"""

from __future__ import annotations

import re
import unicodedata

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.constants.funnel_check_constants import FunnelCheckConstants as Constants
from app.pipeline.schemas import EndCardShot, ScenesManifest


def words(text: str) -> list[str]:
    """As palavras de uma fala, minúsculas e sem acento, sem pontuação nem marcas de pausa."""
    decomposed = unicodedata.normalize("NFD", strip_pauses(text).lower())
    plain = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", plain)


def find(haystack: list[str], part: list[str]) -> int:
    """Onde `part` começa em `haystack` (palavras seguidas), ou -1."""
    size = len(part)
    return next((i for i in range(len(haystack) - size + 1) if haystack[i : i + size] == part), -1)


def _asks(cta: list[str], entries: tuple[str, ...]) -> bool:
    """A chamada usa um dos pedidos do estágio: cada entrada é um ou mais começos de palavras seguidas."""
    for entry in entries:
        prefixes = entry.split()
        for i in range(len(cta) - len(prefixes) + 1):
            if all(cta[i + j].startswith(prefix) for j, prefix in enumerate(prefixes)):
                return True
    return False


def funnel_errors(scenes: ScenesManifest) -> list[str]:
    """A chamada não pede o que o estágio pede, não é dita na última cena, ou a pergunta dos comentários
    não é dita ali antes dela."""
    funnel = scenes.funnel
    if funnel is None:
        return []
    errors = []
    asks, entries = Constants.FUNNEL_ASKS[funnel.stage]
    cta = words(funnel.cta)
    if not _asks(cta, entries):
        errors.append(f'funil {funnel.stage}: a chamada "{funnel.cta}" não pede para {asks}')
    last = scenes.scenes[-1]
    spoken = words(last.narration)
    said_at = find(spoken, cta)
    if said_at < 0:
        errors.append(f'funil: a chamada "{funnel.cta}" não está na narração da última cena ({last.id})')
    if funnel.engagement is not None:
        asked_at = find(spoken, words(funnel.engagement))
        if asked_at < 0:
            errors.append(
                f'funil: a pergunta "{funnel.engagement}" não está na narração da última cena ({last.id})'
            )
        elif said_at >= 0 and asked_at > said_at:
            errors.append(f"funil: em {last.id}, a pergunta dos comentários vem depois da chamada, que fecha")
    return errors


def funnel_warnings(scenes: ScenesManifest) -> list[str]:
    """Falta o estágio (roteiros antigos continuam válidos), ou o cartão final não combina com ele."""
    funnel = scenes.funnel
    if funnel is None:
        return ["roteiro sem estágio do funil (topo, meio ou fundo; ADR 026)"]
    last = scenes.scenes[-1]
    card = last.shots[-1] if last.shots and isinstance(last.shots[-1], EndCardShot) else None
    if card is None:
        return []
    warnings = []
    expected = Constants.END_CARD_VARIANTS.get(funnel.stage)
    if card.variant != "next" and card.variant != expected:
        warnings.append(f"funil {funnel.stage}: cartão final {card.variant}; o estágio pede {expected}")
    spoken = strip_pauses(last.narration)
    if find(words(spoken[spoken.find(card.anchor) :]), words(funnel.cta)) < 0:
        warnings.append(f'funil: a chamada "{funnel.cta}" não é dita durante o cartão final ({last.id})')
    return warnings


def funnel_attention(scenes: ScenesManifest, chars_per_second: float) -> list[str]:
    """Vídeo longo sem a pergunta dos comentários no fecho: o dono decide no gate 2."""
    funnel = scenes.funnel
    if funnel is None or funnel.engagement is not None:
        return []
    if any(word.startswith(Constants.COMMENT_PREFIX) for word in words(funnel.cta)):
        return []
    seconds = sum(timeline_length(scene.narration) for scene in scenes.scenes) / chars_per_second
    if seconds < Constants.LONG_VIDEO_SECONDS:
        return []
    return [
        "funil: vídeo longo sem a pergunta dos comentários no fecho; ponha `funnel.engagement` e diga a "
        "pergunta na última cena, antes da chamada (emenda de 2026-11-16 da ADR 026)"
    ]


def funnel_summary(scenes: ScenesManifest) -> str | None:
    funnel = scenes.funnel
    if funnel is None:
        return None
    line = f"funil: {funnel.stage}"
    if funnel.engagement is not None:
        line += f"; pergunta: {funnel.engagement}"
    line += f"; chamada: {funnel.cta}"
    return f"{line}; oferta: {funnel.offer}" if funnel.offer else line
