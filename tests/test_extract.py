"""Extração do texto de fontes baixadas (um parágrafo = um trecho, ADR 009), sem rede."""

from app.pipeline.excerpts import split_excerpts
from app.pipeline.extract import as_source_text, decode_html, html_paragraphs, pdf_paragraphs

PAGE = """<html><head><title>t</title><style>p{}</style><script>var x = "<p>não</p>";</script></head>
<body><nav><p>Menu</p></nav><header><h1>Cabeçalho do site</h1></header>
<article><h1>Título do artigo</h1>
<p>Primeiro parágrafo,<br>com quebra e <em>ênfase</em>.</p>
<blockquote><p>Citação dentro de bloco.</p></blockquote>
<ul><li>Item um</li><li>Item &amp; dois</li></ul>
<table><tr><td>1918</td><td>5 mil contos</td></tr></table></article>
<footer><p>Rodapé</p></footer></body></html>"""


def test_html_keeps_article_blocks_and_drops_page_chrome() -> None:
    assert html_paragraphs(PAGE) == [
        "Título do artigo",
        "Primeiro parágrafo, com quebra e ênfase.",
        "Citação dentro de bloco.",
        "Item um",
        "Item & dois",
        "1918",
        "5 mil contos",
    ]


def test_pdf_blocks_become_paragraphs_and_hyphenation_is_undone() -> None:
    output = (
        "Primeira linha do bloco\ncontinua aqui com hifeni-\nzação.\n\n"
        "Segundo bloco.\fTerceiro, na página seguinte.\n"
    )
    assert pdf_paragraphs(output) == [
        "Primeira linha do bloco continua aqui com hifenização.",
        "Segundo bloco.",
        "Terceiro, na página seguinte.",
    ]


def test_source_text_round_trips_through_excerpt_numbering() -> None:
    paragraphs = ["Um.", "Dois, com   espaços.", "Três."]
    assert split_excerpts(as_source_text(paragraphs)) == ["Um.", "Dois, com espaços.", "Três."]


def test_html_charset_from_meta() -> None:
    raw = '<meta charset="iso-8859-1"><p>Fábrica de tecidos</p>'.encode("latin-1")
    assert html_paragraphs(decode_html(raw)) == ["Fábrica de tecidos"]
    assert decode_html("<p>ção</p>".encode()) == "<p>ção</p>"
