"""Constantes de postiz_links; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class PostizLinksConstants:
    LINK: Final = re.compile("https?://[^\\s<>\\\"')]+")
    LINK_TIMEOUT_S: Final[int] = 8
    # o que um repositório privado ou apagado devolve a quem não está logado
    GONE: Final = (404, 410)
