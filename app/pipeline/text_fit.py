"""Quanto texto cabe em cada peça da tela: alertas do `vp check` (ADR 011, emenda de 2026-09-29).

Cada limite é a largura da caixa ÷ (tamanho da letra × ~0,5, a largura média de um caractere da Inter;
~0,55 em negrito), em px de 1080p, medida no template (`video/src/Editorial.tsx`) e no motion-kit, e
conferida nos quadros do vídeo-régua (`votorantim-dinheiro`, v3): a linha do tempo quebra por volta de 31
caracteres, a comparação aceita 42 numa linha, o painel do número sobre a imagem aceita 59 e o nome do nó
da rede quebra depois de 23. É estimativa: "WWW" ocupa mais que "iii". Alerta não bloqueia; a revisão
humana decide.
"""

from __future__ import annotations

from app.pipeline.schemas import CompareShot, LowerThirdShot, NetworkShot, NumberShot, Shot, TimelineShot

# (caracteres por linha, linhas que cabem)
NUMBER_OVER_MEDIA = (60, 1)  # painel sobre a imagem, até 1100 px, letra 32; com 2 linhas cobre a imagem
NUMBER_FULL = (54, 2)  # número em tela cheia, 1200 px, letra 44
COMPARE_LABEL = (44, 2)  # metade de 1600 px menos o espaço do meio, letra 36 (ValueCompare)
TIMELINE_LABEL = (31, 3)  # caixa de 457 px (0,88 × 520), letra 30 (YearTimeline)
LOWER_THIRD_NAME = (34, 1)  # 46% da tela menos as margens (831 px), letra 44 em negrito (LowerThird)
LOWER_THIRD_ROLE = (60, 2)  # a mesma caixa, letra 27
# Rede, na tela de 1280×720 em que ela é desenhada: caixa de 260 px (ExpandingNetwork).
NODE_LABEL_PER_LINE = 23  # letra 21 em negrito
NODE_ROLE_PER_LINE = 30  # letra 17
NODE_LINES = 2  # nome + papel de um nó com seta saindo: com mais, o bloco encosta no texto dessa seta
EDGE_LABEL_CHARS = 40  # etiqueta sobre a seta, letra 17 fixa no kit (~450 px)
EDGE_VALUE_CHARS = 24  # valor na seta, letra 16 fixa no kit
# Texto na tela que a narração não lê junto precisa de tempo: ritmo usual de legenda para adultos.
READING_CHARS_PER_SECOND = 17.0


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
        fit(shot.label, NUMBER_OVER_MEDIA if over_media else NUMBER_FULL, f"texto do número {where}")
    elif isinstance(shot, CompareShot):
        for side in (shot.left, shot.right):
            fit(side.label, COMPARE_LABEL, "texto da comparação")
    elif isinstance(shot, LowerThirdShot):
        fit(shot.name, LOWER_THIRD_NAME, "nome da tarja")
        fit(shot.role, LOWER_THIRD_ROLE, "cargo da tarja")
    elif isinstance(shot, TimelineShot):
        for event in shot.events:
            fit(event.label, TIMELINE_LABEL, f"evento {event.date!r} da linha do tempo")
        chars = sum(len(e.label) for e in shot.events)
        readable = READING_CHARS_PER_SECOND * ms / 1000
        if chars > readable:
            found.append(f"{scene_id}: linha do tempo com {chars} caracteres de texto em ~{ms / 1000:.1f} s; "
                         f"dá para ler ~{readable:.0f}")
    elif isinstance(shot, NetworkShot):
        # Nas camadas as setas descem: o nome pende só sobre as setas que saem do nó (no radial, sobre todas).
        sources = {edge.from_ for edge in shot.edges}
        for node in shot.nodes:
            if shot.layout == "layered" and node.id not in sources:
                continue
            used = lines(node.label, NODE_LABEL_PER_LINE)
            used += lines(node.role, NODE_ROLE_PER_LINE) if node.role else 0
            if used > NODE_LINES:
                found.append(f"{scene_id}: nó {node.label!r} ocupa {used} linhas com o papel, "
                             f"cabem {NODE_LINES}; use um nome curto (a sigla, apresentada antes)")
        for edge in shot.edges:
            arrow = f"{edge.from_}→{edge.to}"
            if len(edge.label) > EDGE_LABEL_CHARS:
                found.append(f"{scene_id}: texto da seta {arrow} com {len(edge.label)} caracteres, "
                             f"cabem ~{EDGE_LABEL_CHARS}: {edge.label!r}")
            if len(edge.value) > EDGE_VALUE_CHARS:
                found.append(f"{scene_id}: valor da seta {arrow} com {len(edge.value)} caracteres, "
                             f"cabem ~{EDGE_VALUE_CHARS}: {edge.value!r}")
    return found
