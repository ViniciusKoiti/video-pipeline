"""Livros citados com link de afiliado da Amazon no `description.txt` (provisório até `vp export`, #18).

Uso: `.venv/bin/python scripts/provisorio/livros_afiliado.py <episode-id>`

- Lê `data/episodes/<id>/livros.json` (`{"livros": [{"titulo", "autor", "link"?, "busca"?}]}`) e a tag de
  associado em `config/canal.toml` (`[amazon] tag`).
- Grava o bloco "Livros citados no vídeo" no `description.txt`, do título até o aviso exigido pela Amazon,
  sem marcador escondido (o texto vai para o YouTube como está); o resto da descrição não muda. Rodar de novo
  só troca o bloco.
- Link do produto copiado da barra SiteStripe é usado como está (com a tag); sem link, sai uma busca na Amazon
  com a tag. O script não visita a Amazon nem inventa produto.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.affiliate import BOOKS_FILE, BookList, books_block, channel_tag, with_block  # noqa: E402


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    args = parser.parse_args()
    folder = ROOT / "data" / "episodes" / args.episode_id
    books = BookList.model_validate_json((folder / BOOKS_FILE).read_text(encoding="utf-8"))
    block = books_block(books, channel_tag(ROOT))
    description = folder / "description.txt"
    text = description.read_text(encoding="utf-8") if description.is_file() else ""
    new = with_block(text, block)
    if new != text:
        description.write_text(new, encoding="utf-8")
    print(block)
    print(f"{description}: {'gravado' if new != text else 'já estava em dia'}")


if __name__ == "__main__":
    main()
