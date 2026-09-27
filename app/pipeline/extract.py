"""Texto de uma fonte baixada em parágrafos separados por linha em branco (um parágrafo = um trecho, ADR 009).

Funções puras: o download e a chamada ao `pdftotext` ficam fora do pipeline (script provisório até
`vp sources`, #26).
- HTML: um parágrafo por bloco de texto (p, títulos, itens de lista, citações, células), sem script, estilo,
  navegação, cabeçalho e rodapé.
- PDF: a saída do `pdftotext` já separa blocos por linha em branco; aqui as linhas de cada bloco viram uma
  só, e a hifenização no fim da linha é desfeita.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser

BLOCKS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "td", "th", "figcaption", "dt", "dd", "pre",
}
SKIPPED = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form", "button", "select"}
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")


class _Paragraphs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: list[str] = []
        self._buffer: list[str] = []
        self._depth = 0  # dentro de um bloco
        self._skip = 0  # dentro de um elemento ignorado

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED:
            self._skip += 1
        elif tag in BLOCKS:
            if self._depth == 0:
                self._flush()
            self._depth += 1
        elif tag == "br":
            self._buffer.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED and self._skip:
            self._skip -= 1
        elif tag in BLOCKS and self._depth:
            self._depth -= 1
            if self._depth == 0:
                self._flush()

    def handle_data(self, data: str) -> None:
        if not self._skip and self._depth:
            self._buffer.append(data)

    def _flush(self) -> None:
        text = " ".join("".join(self._buffer).split())
        if text:
            self.paragraphs.append(text)
        self._buffer = []

    def close(self) -> None:
        super().close()
        self._flush()


def html_paragraphs(html: str) -> list[str]:
    parser = _Paragraphs()
    parser.feed(html)
    parser.close()
    return parser.paragraphs


def pdf_paragraphs(pdftotext_output: str) -> list[str]:
    text = _HYPHEN_BREAK.sub(r"\1\2", pdftotext_output.replace("\f", "\n\n"))
    return [" ".join(block.split()) for block in re.split(r"\n\s*\n", text) if block.strip()]


def as_source_text(paragraphs: list[str]) -> str:
    """Um parágrafo por bloco, separados por linha em branco: o formato que `vp excerpts` numera."""
    return "\n\n".join(paragraphs) + "\n"


_CHARSET = re.compile(rb"""<meta[^>]+charset=["']?([\w-]+)""", re.IGNORECASE)


def decode_html(raw: bytes) -> str:
    """Decodifica pelo charset declarado no <meta> (sites antigos usam latin-1); sem declaração, UTF-8."""
    match = _CHARSET.search(raw[:4096])
    encoding = match.group(1).decode("ascii") if match else "utf-8"
    try:
        return raw.decode(encoding, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")
