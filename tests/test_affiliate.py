"""Livros citados com link de afiliado da Amazon na descrição."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from app.pipeline.affiliate import (
    BLOCK_END,
    BLOCK_START,
    DISCLOSURE,
    Book,
    BookList,
    amazon_link,
    books_block,
    channel_tag,
    with_block,
)

TAG = "canal-20"


def test_search_link_carries_the_tag_and_never_a_made_up_product() -> None:
    link = amazon_link(Book(titulo="O Príncipe", autor="Maquiavel"), TAG)
    parts = urlsplit(link)
    assert parts.netloc == "www.amazon.com.br" and parts.path == "/s"
    assert parse_qs(parts.query) == {"k": ["O Príncipe Maquiavel"], "tag": [TAG]}


def test_product_link_gets_the_tag_once() -> None:
    book = Book(
        titulo="O Príncipe", autor="Maquiavel", link="https://www.amazon.com.br/dp/X1?tag=outro-20&ref=a"
    )
    query = parse_qs(urlsplit(amazon_link(book, TAG)).query)
    assert query == {"ref": ["a"], "tag": [TAG]}
    short = Book(titulo="A", autor="B", link="https://amzn.to/abc")
    assert amazon_link(short, TAG) == "https://amzn.to/abc"


def test_link_outside_amazon_is_refused() -> None:
    with pytest.raises(ValueError, match="fora da Amazon"):
        amazon_link(Book(titulo="A", autor="B", link="https://exemplo.com/livro"), TAG)


def test_block_has_the_disclosure_and_replaces_only_itself() -> None:
    books = BookList(livros=[Book(titulo="A República", autor="Platão")])
    block = books_block(books, TAG)
    assert block.startswith(BLOCK_START) and block.endswith(BLOCK_END) and DISCLOSURE in block
    text = "Resumo do vídeo.\n\nFontes: ver credits.txt\n"
    once = with_block(text, block)
    assert with_block(once, block) == once
    assert once.startswith(text.rstrip("\n"))
    middle = "Antes\n\n" + block + "\n\nDepois\n"
    assert with_block(middle, block.replace("Platão", "PLATÃO")).endswith("\n\nDepois\n")


def test_tag_comes_from_the_channel_config(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "canal.toml").write_text('[amazon]\ntag = "canal-20"\n', encoding="utf-8")
    assert channel_tag(tmp_path) == "canal-20"
    (tmp_path / "config" / "canal.toml").write_text("[amazon]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="tag"):
        channel_tag(tmp_path)


def test_the_repository_config_has_a_tag() -> None:
    assert channel_tag(Path(__file__).resolve().parents[1])
