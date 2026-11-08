"""`vp sources`: registra uma fonte no `sources.json` do episódio (#26, ADR 043).

- `vp sources add <id> <url> --title ... --kind ...`: baixa a página ou o PDF, extrai o texto e registra.
  Com `--file`, usa um PDF salvo à mão no navegador (servidor que recusa o robô); `url` segue como
  origem. Só para serviços que o dono autorizou na sessão (§14); o transporte manda o User-Agent do projeto.
- `vp sources declared <id> <arquivo.md|.txt> --title ...`: material do próprio dono (receita, nota de
  compra), sem URL e sem rede; cada linha não vazia é um trecho. O `vp check` avisa e o dono responde por
  ela no gate 1.

O original vai para `sources/raw/source-NN.*`, o texto para `sources/source-NN.txt` e os trechos
numerados para `excerpts/source-NN.md`, como `vp excerpts`. O registro é `SourceRegistry`: id livre sob
lock, a mesma URL (ou o mesmo texto) não duplica, gate 1 aprovado recusa antes de escrever (`vp reopen
--step sources`) e o `sources.json` vai por último.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

from app.commands.constants.sources_command_constants import SourcesCommandConstants as Constants
from app.pipeline.models.extracted_source import ExtractedSource
from app.pipeline.models.source_draft import SourceDraft
from app.pipeline.ports import Context
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import SourceKind
from app.pipeline.sources import SourceRegistry, declared, fetch_url, from_file
from app.providers.http import download


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="sources_command", required=True)
    add = commands.add_parser("add", help="baixa uma fonte, extrai o texto e registra")
    add.add_argument("episode_id", metavar="id")
    add.add_argument("url")
    add.add_argument("--kind", required=True, choices=[kind.value for kind in SourceKind])
    add.add_argument("--file", type=Path, help="PDF baixado à mão (servidor que recusa o robô)")
    own = commands.add_parser("declared", help="registra material do próprio dono como fonte declarada")
    own.add_argument("episode_id", metavar="id")
    own.add_argument("file", type=Path, help="texto do dono (.md ou .txt), sem dado pessoal")
    for sub in (add, own):
        sub.add_argument("--title", required=True)
        sub.add_argument("--authors", default="", help="separados por ponto e vírgula")
        sub.add_argument("--notes", default="")
    add.add_argument("--interested", action="store_true", help="fonte da própria empresa ou família")


def pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout


def run(args: argparse.Namespace, context: Context) -> int:
    store = context.store
    guard = ReviewWriteGuard(store, context.review)
    registry = SourceRegistry(store, guard, lambda: datetime.now().astimezone().replace(microsecond=0))
    authors = tuple(name.strip() for name in args.authors.split(";") if name.strip())
    if args.sources_command == "declared":
        draft = SourceDraft(title=args.title, kind=SourceKind.DECLARED, authors=authors, notes=args.notes)
        extracted, exists, label = declared(args.file), "este texto já está registrado", "fonte declarada"
    else:
        draft = SourceDraft(
            title=args.title,
            kind=SourceKind(args.kind),
            url=args.url,
            authors=authors,
            interested=args.interested,
            notes=args.notes,
        )
        extracted = _extract(args)
        exists, label = "já registrada para esta URL", extracted.suffix
    result = registry.register(args.episode_id, draft, extracted)
    if not result.created:
        print(f"{result.source.id}: {exists}; nada foi escrito")
        return 0
    path = store.path(args.episode_id, f"excerpts/{result.source.id}.md")
    shown = os.path.relpath(path, context.settings.data_dir.parent)
    print(f"{result.source.id}: {label}, {len(extracted.paragraphs)} trechos -> {shown}")
    return 0


def _extract(args: argparse.Namespace) -> ExtractedSource:
    if args.file:
        return from_file(args.file, pdf_text)
    seconds = Constants.DOWNLOAD_TIMEOUT_S
    return fetch_url(args.url, lambda url, dest: download(url, dest, {}, seconds), pdf_text)
