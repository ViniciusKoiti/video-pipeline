"""Constantes de text_fit; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class TextFitConstants:
    # painel sobre a imagem, até 1100 px, letra 32; com 2 linhas cobre a imagem
    NUMBER_OVER_MEDIA: Final = (60, 1)
    # número em tela cheia, 1200 px, letra 44
    NUMBER_FULL: Final = (54, 2)
    # metade de 1600 px menos o espaço do meio, letra 36 (ValueCompare)
    COMPARE_LABEL: Final = (44, 2)
    # caixa de 457 px (0,88 × 520), letra 30 (YearTimeline)
    TIMELINE_LABEL: Final = (31, 3)
    # 46% da tela menos as margens (831 px), letra 44 em negrito (LowerThird)
    LOWER_THIRD_NAME: Final = (34, 1)
    # a mesma caixa, letra 27
    LOWER_THIRD_ROLE: Final = (60, 2)
    # letra 21 em negrito
    NODE_LABEL_PER_LINE: Final[int] = 23
    # letra 17
    NODE_ROLE_PER_LINE: Final[int] = 30
    # nome + papel de um nó com seta saindo: com mais, o bloco encosta no texto dessa seta
    NODE_LINES: Final[int] = 2
    # etiqueta sobre a seta, letra 17 fixa no kit (~450 px)
    EDGE_LABEL_CHARS: Final[int] = 40
    # valor na seta, letra 16 fixa no kit
    EDGE_VALUE_CHARS: Final[int] = 24
    READING_CHARS_PER_SECOND: Final[float] = 17.0
