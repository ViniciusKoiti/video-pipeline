"""Livros citados com link de afiliado da Amazon na descrição do vídeo (Programa de Associados).

O episódio lista as obras citadas em `livros.json`; a tag do associado fica em `config/canal.toml`. O bloco
gerado vai para o `description.txt` entre marcadores, com o aviso que o contrato da Amazon pede, e é refeito
sem tocar no resto do texto. Link explícito (o da barra SiteStripe) ganha a tag se não tiver; sem link, sai
uma busca na Amazon com a tag, que nunca aponta para um produto que ninguém conferiu.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field

BOOKS_FILE = "livros.json"
CHANNEL_FILE = "config/canal.toml"
AMAZON_HOSTS = ("amazon.com.br", "www.amazon.com.br", "amzn.to")
# Texto exigido pelo contrato do Programa de Associados da Amazon.com.br (cláusula 5)
DISCLOSURE = (
    "Como participante do Programa de Associados da Amazon, "
    "sou remunerado pelas compras qualificadas efetuadas."
)
# O bloco vai para o YouTube como está: começa no título visível e termina no aviso, sem marcador escondido
BLOCK_START = "📚 Livros citados no vídeo:"
BLOCK_END = DISCLOSURE


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Book(_Model):
    titulo: str = Field(min_length=1)
    autor: str = Field(min_length=1)
    link: str | None = None  # link do produto copiado da SiteStripe; sem ele, uma busca
    busca: str | None = None  # termos da busca; padrão: título e autor


class BookList(_Model):
    livros: list[Book]


def channel_tag(root: Path) -> str:
    """A tag do associado (`[amazon] tag` em `config/canal.toml`)."""
    data = tomllib.loads((root / CHANNEL_FILE).read_text(encoding="utf-8"))
    tag = str(data.get("amazon", {}).get("tag", "")).strip()
    if not tag:
        raise ValueError(f"{CHANNEL_FILE}: falta [amazon] tag")
    return tag


def amazon_link(book: Book, tag: str) -> str:
    if book.link:
        parts = urlsplit(book.link)
        if parts.hostname not in AMAZON_HOSTS:
            raise ValueError(f"{book.titulo}: link fora da Amazon ({parts.hostname})")
        if parts.hostname == "amzn.to":
            return book.link  # link curto da SiteStripe: a tag já vai dentro dele
        query = [(k, v) for k, v in parse_qsl(parts.query) if k != "tag"] + [("tag", tag)]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))
    terms = book.busca or f"{book.titulo} {book.autor}"
    return f"https://www.amazon.com.br/s?k={quote_plus(terms)}&tag={quote_plus(tag)}"


def books_block(books: BookList, tag: str) -> str:
    lines = [BLOCK_START]
    lines += [f"- {book.autor}, {book.titulo}: {amazon_link(book, tag)}" for book in books.livros]
    lines += [BLOCK_END]
    return "\n".join(lines)


def with_block(text: str, block: str) -> str:
    """O texto com o bloco trocado; sem bloco, acrescenta no fim. Fora dos marcadores nada muda."""
    start, end = text.find(BLOCK_START), text.find(BLOCK_END)
    if start >= 0 and end > start:
        return text[:start] + block + text[end + len(BLOCK_END) :]
    return text.rstrip("\n") + "\n\n" + block + "\n"
