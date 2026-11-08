"""`vp export`: o que sai do episódio para publicar (#18). Primeira fatia: os livros citados.

- `vp export livros <id>`: lê `livros.json` do episódio (`{"livros": [{"titulo", "autor", "link"?,
  "busca"?}]}`) e a tag de associado em `config/canal.toml` (`[amazon] tag`) e grava o bloco "Livros citados
  no vídeo" no `description.txt`, do título até o aviso exigido pela Amazon, sem marcador escondido (o texto
  vai para o YouTube como está). O resto da descrição não muda e rodar de novo só troca o bloco. Link do
  produto copiado da barra SiteStripe é usado como está (com a tag); sem link, sai uma busca na Amazon com a
  tag. Não visita a Amazon nem inventa produto.

O `final.mp4`, o `captions.srt` e o `credits.txt` do export completo ainda não existem como comando.
"""

from __future__ import annotations

import argparse

from app.pipeline.affiliate import apply_books, channel_tag
from app.pipeline.ports import Context


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="export_command", required=True)
    books = commands.add_parser("livros", help="livros citados com link de afiliado -> description.txt")
    books.add_argument("episode_id", metavar="id")


def run(args: argparse.Namespace, context: Context) -> int:
    tag = channel_tag(context.settings.data_dir.parent)
    update = apply_books(context.store, args.episode_id, tag)
    print(update.block)
    print(f"{update.path}: {'gravado' if update.changed else 'já estava em dia'}")
    return 0
