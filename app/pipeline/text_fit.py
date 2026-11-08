"""Quanto texto cabe em cada peça da tela: alertas do `vp check` (ADR 011, emenda de 2026-09-29).

Cada limite é a largura da caixa ÷ (tamanho da letra × ~0,5, a largura média de um caractere da Inter;
~0,55 em negrito), em px de 1080p, medida no template (`video/src/Editorial.tsx`) e no motion-kit, e
conferida nos quadros do vídeo-régua (`votorantim-dinheiro`, v3): a linha do tempo quebra por volta de 31
caracteres, a comparação aceita 42 numa linha, o painel do número sobre a imagem aceita 59 e o nome do nó
da rede quebra depois de 23. É estimativa: "WWW" ocupa mais que "iii". Alerta não bloqueia; a revisão
humana decide.
"""

from __future__ import annotations

from app.pipeline.constants.text_fit_constants import TextFitConstants
from app.pipeline.schemas import CompareShot, LowerThirdShot, NetworkShot, NumberShot, Shot, TimelineShot

# (caracteres por linha, linhas que cabem)
# Rede, na tela de 1280×720 em que ela é desenhada: caixa de 260 px (ExpandingNetwork).
# Texto na tela que a narração não lê junto precisa de tempo: ritmo usual de legenda para adultos.


def lines(text: str, per_line: int) -> int:
    """Linhas que o texto ocupa, quebrando entre palavras (uma palavra maior que a linha ocupa uma)."""
    count, width = 1, 0
    for word in text.split():
        if width and width + 1 + len(word) > per_line:
            count, width = count + 1, len(word)
        else:
            width += len(word) + (1 if width else 0)
    return count


def text_fit_warnings(scene_id: str, shot: Shot, ms: float, over_media: bool) -> list[str]:
    """Texto que não cabe na peça, ou que não dá para ler no tempo do plano. `ms` é a duração estimada;
    `over_media`: o plano é desenhado sobre a foto ou o B-roll da cena."""
    found: list[str] = []

    def fit(text: str, box: tuple[int, int], what: str) -> None:
        per_line, allowed = box
        used = lines(text, per_line)
        if used > allowed:
            found.append(f"{scene_id}: {what} em {used} linhas, cabe{'m' if allowed > 1 else ''} {allowed} "
                         f"(~{per_line} caracteres por linha): {text!r}")

    if isinstance(shot, NumberShot):
        where = "sobre a imagem" if over_media else "em tela cheia"
        fit(
            shot.label,
            TextFitConstants.NUMBER_OVER_MEDIA if over_media else TextFitConstants.NUMBER_FULL,
            f"texto do número {where}",
        )
    elif isinstance(shot, CompareShot):
        for side in (shot.left, shot.right):
            fit(side.label, TextFitConstants.COMPARE_LABEL, "texto da comparação")
    elif isinstance(shot, LowerThirdShot):
        fit(shot.name, TextFitConstants.LOWER_THIRD_NAME, "nome da tarja")
        fit(shot.role, TextFitConstants.LOWER_THIRD_ROLE, "cargo da tarja")
    elif isinstance(shot, TimelineShot):
        for event in shot.events:
            fit(event.label, TextFitConstants.TIMELINE_LABEL, f"evento {event.date!r} da linha do tempo")
        chars = sum(len(e.label) for e in shot.events)
        readable = TextFitConstants.READING_CHARS_PER_SECOND * ms / 1000
        if chars > readable:
            found.append(f"{scene_id}: linha do tempo com {chars} caracteres de texto em ~{ms / 1000:.1f} s; "
                         f"dá para ler ~{readable:.0f}")
    elif isinstance(shot, NetworkShot):
        # Nas camadas as setas descem: o nome pende só sobre as setas que saem do nó (no radial, sobre todas).
        sources = {edge.from_ for edge in shot.edges}
        for node in shot.nodes:
            if shot.layout == "layered" and node.id not in sources:
                continue
            used = lines(node.label, TextFitConstants.NODE_LABEL_PER_LINE)
            used += lines(node.role, TextFitConstants.NODE_ROLE_PER_LINE) if node.role else 0
            if used > TextFitConstants.NODE_LINES:
                found.append(
                    f"{scene_id}: nó {node.label!r} ocupa {used} linhas com o papel, "
                    f"cabem {TextFitConstants.NODE_LINES}; use um nome curto (a sigla, apresentada antes)"
                )
        for edge in shot.edges:
            arrow = f"{edge.from_}→{edge.to}"
            if len(edge.label) > TextFitConstants.EDGE_LABEL_CHARS:
                found.append(f"{scene_id}: texto da seta {arrow} com {len(edge.label)} caracteres, "
                             f"cabem ~{TextFitConstants.EDGE_LABEL_CHARS}: {edge.label!r}")
            if len(edge.value) > TextFitConstants.EDGE_VALUE_CHARS:
                found.append(f"{scene_id}: valor da seta {arrow} com {len(edge.value)} caracteres, "
                             f"cabem ~{TextFitConstants.EDGE_VALUE_CHARS}: {edge.value!r}")
    return found
