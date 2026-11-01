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

from pydantic import ValidationError

from app.errors import PipelineError
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.affiliate_constants import AffiliateConstants
from app.pipeline.models._affiliate_model import _Model as _Model
from app.pipeline.models.affiliate_update import AffiliateUpdate
from app.pipeline.models.book import Book as Book
from app.pipeline.models.book_list import BookList as BookList
from app.pipeline.ports import ManifestStore

# Texto exigido pelo contrato do Programa de Associados da Amazon.com.br (cláusula 5)

# O bloco vai para o YouTube como está: começa no título visível e termina no aviso, sem marcador escondido


class AffiliateError(PipelineError, ValueError):
    """Lista de livros, link ou tag que não servem; a mensagem diz qual. Nada foi escrito."""


def channel_tag(root: Path) -> str:
    """A tag do associado (`[amazon] tag` em `config/canal.toml`)."""
    path = root / AffiliateConstants.CHANNEL_FILE
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise AffiliateError(f"{AffiliateConstants.CHANNEL_FILE}: não foi possível ler ({error})") from error
    except tomllib.TOMLDecodeError as error:
        raise AffiliateError(f"{AffiliateConstants.CHANNEL_FILE}: TOML inválido ({error})") from error
    tag = str(data.get("amazon", {}).get("tag", "")).strip()
    if not tag:
        raise AffiliateError(f"{AffiliateConstants.CHANNEL_FILE}: falta [amazon] tag")
    return tag


def amazon_link(book: Book, tag: str) -> str:
    if book.link:
        parts = urlsplit(book.link)
        if parts.hostname not in AffiliateConstants.AMAZON_HOSTS:
            raise AffiliateError(f"{book.titulo}: link fora da Amazon ({parts.hostname})")
        if parts.hostname == "amzn.to":
            return book.link  # link curto da SiteStripe: a tag já vai dentro dele
        query = [(k, v) for k, v in parse_qsl(parts.query) if k != "tag"] + [("tag", tag)]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))
    terms = book.busca or f"{book.titulo} {book.autor}"
    return f"https://www.amazon.com.br/s?k={quote_plus(terms)}&tag={quote_plus(tag)}"


def books_block(books: BookList, tag: str) -> str:
    lines = [AffiliateConstants.BLOCK_START]
    lines += [f"- {book.autor}, {book.titulo}: {amazon_link(book, tag)}" for book in books.livros]
    lines += [AffiliateConstants.BLOCK_END]
    return "\n".join(lines)


def with_block(text: str, block: str) -> str:
    """O texto com o bloco trocado; sem bloco, acrescenta no fim. Fora dos marcadores nada muda."""
    start, end = text.find(AffiliateConstants.BLOCK_START), text.find(AffiliateConstants.BLOCK_END)
    if start >= 0 and end > start:
        return text[:start] + block + text[end + len(AffiliateConstants.BLOCK_END) :]
    if not text.strip():
        return block + "\n"  # descrição que ainda não existe: sem linhas em branco na frente
    return text.rstrip("\n") + "\n\n" + block + "\n"


def apply_books(store: ManifestStore, episode_id: str, tag: str) -> AffiliateUpdate:
    """Lê `livros.json` do episódio e põe o bloco no `description.txt`; o resto da descrição não muda e rodar
    de novo só troca o bloco. Valida tudo antes de escrever, que é inteira e sob o lock do episódio."""
    source = store.path(episode_id, AffiliateConstants.BOOKS_FILE)
    if not source.is_file():
        raise AffiliateError(f"{episode_id}/{AffiliateConstants.BOOKS_FILE} não existe")
    try:
        books = BookList.model_validate_json(source.read_text(encoding="utf-8"))
    except ValidationError as error:
        raise AffiliateError(
            f"{AffiliateConstants.BOOKS_FILE}: fora do formato ({error.error_count()} erro(s))"
        ) from error
    block = books_block(books, tag)
    path = store.path(episode_id, AffiliateConstants.DESCRIPTION_FILE)
    with store.lock(episode_id):
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        new = with_block(text, block)
        if new != text:
            write_atomic(path, new.encode("utf-8"))
    return AffiliateUpdate(block, path, new != text)
