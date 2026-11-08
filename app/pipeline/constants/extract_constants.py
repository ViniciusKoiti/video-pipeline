"""Constantes de extract; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class ExtractConstants:
    BLOCKS: Final = frozenset(
        (
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "blockquote",
            "td",
            "th",
            "figcaption",
            "dt",
            "dd",
            "pre",
        )
    )
    SKIPPED: Final = frozenset(
        ("script", "style", "nav", "header", "footer", "noscript", "svg", "form", "button", "select")
    )
    _HYPHEN_BREAK: Final = re.compile("(\\w)-\\n(\\w)")
    _CHARSET: Final = re.compile(b"<meta[^>]+charset=[\"']?([\\w-]+)", re.IGNORECASE)
