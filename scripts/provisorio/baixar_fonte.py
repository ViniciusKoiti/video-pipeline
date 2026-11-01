"""Baixa uma fonte, extrai o texto e registra em sources.json (provisório até `vp sources`, #26).

Uso: `.venv/bin/python scripts/provisorio/baixar_fonte.py <episode-id> <url> --title "..." --kind secondary
[--authors "Sobrenome, Nome; ..."] [--interested] [--notes "..."] [--file arquivo.pdf]`

- `--file`: PDF salvo à mão no navegador, para o servidor que recusa o robô (403); `url` segue como origem.
- Só para serviços que o dono autorizou na sessão (§14). O transporte manda o User-Agent do projeto.
- Original em `sources/raw/source-NN.(html|pdf)`; texto em `sources/source-NN.txt`, um parágrafo por trecho
  (`app/pipeline/extract.py`); trechos numerados em `excerpts/source-NN.md`, como `vp excerpts`.
- O registro é `app.pipeline.sources.SourceRegistry` (ADR 043): id livre sob lock, a mesma URL não duplica,
  gate 1 aprovado recusa antes de escrever (`vp reopen --step sources`) e o `sources.json` vai por último.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.pipeline.models.source_draft import SourceDraft  # noqa: E402
from app.pipeline.protection import ReviewWriteGuard  # noqa: E402
from app.pipeline.schemas import SourceKind  # noqa: E402
from app.pipeline.sources import SourceRegistry, fetch_url, from_file  # noqa: E402
from app.providers.http import download  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore, JsonReviewGate  # noqa: E402


def pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("url")
    parser.add_argument("--title", required=True)
    parser.add_argument("--kind", required=True, choices=[k.value for k in SourceKind])
    parser.add_argument("--authors", default="", help="separados por ponto e vírgula")
    parser.add_argument("--interested", action="store_true", help="fonte da própria empresa ou família")
    parser.add_argument("--notes", default="")
    parser.add_argument("--file", help="PDF baixado à mão (servidor que recusa o robô); `url` é só a origem")
    args = parser.parse_args()

    store = JsonFileStore(load_settings(ROOT).data_dir / "episodes")
    guard = ReviewWriteGuard(store, JsonReviewGate(store))
    registry = SourceRegistry(store, guard, lambda: datetime.now().astimezone().replace(microsecond=0))
    draft = SourceDraft(
        title=args.title,
        kind=SourceKind(args.kind),
        url=args.url,
        authors=tuple(a.strip() for a in args.authors.split(";") if a.strip()),
        interested=args.interested,
        notes=args.notes,
    )
    if args.file:
        extracted = from_file(Path(args.file), pdf_text)
    else:
        extracted = fetch_url(args.url, lambda url, dest: download(url, dest, {}, 120), pdf_text)
    result = registry.register(args.episode_id, draft, extracted)
    source = result.source
    if not result.created:
        print(f"{source.id}: já registrada para esta URL; nada foi escrito")
        return
    excerpts = store.path(args.episode_id, f"excerpts/{source.id}.md").relative_to(ROOT)
    print(f"{source.id}: {extracted.suffix}, {len(extracted.paragraphs)} trechos -> {excerpts}")


if __name__ == "__main__":
    raise SystemExit(run("baixar_fonte", main))
