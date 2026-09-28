"""Baixa uma fonte, extrai o texto e registra em sources.json (provisório até `vp sources`, #26).

Uso: `.venv/bin/python scripts/provisorio/baixar_fonte.py <episode-id> <url> --title "..." --kind secondary
[--authors "Sobrenome, Nome; ..."] [--interested] [--notes "..."]`

- Só para serviços que o dono autorizou na sessão (§14). O transporte manda o User-Agent do projeto.
- Original em `sources/raw/source-NN.(html|pdf)`; texto em `sources/source-NN.txt`, um parágrafo por trecho
  (`app/pipeline/extract.py`); trechos numerados em `excerpts/source-NN.md`, como `vp excerpts`.
- O id é o próximo `source-NN` livre; nada existente é sobrescrito. Independência e interesse são registrados
  (`--authors`, `--interested`) e julgados no gate 1.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.excerpts import numbered_view  # noqa: E402
from app.pipeline.extract import as_source_text, decode_html, html_paragraphs, pdf_paragraphs  # noqa: E402
from app.pipeline.schemas import Source, SourceKind, SourcesManifest  # noqa: E402
from app.providers.http import download  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore  # noqa: E402


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
    args = parser.parse_args()

    store = JsonFileStore(load_settings(ROOT).data_dir / "episodes")
    manifest = store.read(args.episode_id, "sources.json", SourcesManifest)
    number = max((int(s.id.removeprefix("source-")) for s in manifest.sources), default=0) + 1
    source_id = f"source-{number:02d}"
    raw_dir = store.path(args.episode_id, "sources/raw")
    partial = download(args.url, raw_dir / f"{source_id}.download", {}, 120)
    is_pdf = partial.read_bytes()[:5] == b"%PDF-"
    raw = partial.rename(raw_dir / f"{source_id}.{'pdf' if is_pdf else 'html'}")
    if is_pdf:
        extracted = subprocess.run(["pdftotext", str(raw), "-"], capture_output=True, text=True, check=True)
        paragraphs = pdf_paragraphs(extracted.stdout)
    else:
        paragraphs = html_paragraphs(decode_html(raw.read_bytes()))
    if not paragraphs:
        raise SystemExit(f"{source_id}: nenhum texto extraído de {raw.name}; fonte não registrada")

    text = as_source_text(paragraphs)
    local_path = f"sources/{source_id}.txt"
    store.path(args.episode_id, local_path).write_text(text, encoding="utf-8")
    source = Source(
        id=source_id,
        title=args.title,
        url=args.url,
        kind=SourceKind(args.kind),
        retrieved_at=datetime.now().astimezone().replace(microsecond=0),
        local_path=local_path,
        notes=args.notes,
        interested=args.interested,
        authors=[a.strip() for a in args.authors.split(";") if a.strip()],
    )
    updated = manifest.model_copy(update={"sources": [*manifest.sources, source]})
    store.write(args.episode_id, "sources.json", updated)
    excerpts = store.path(args.episode_id, f"excerpts/{source_id}.md")
    excerpts.parent.mkdir(parents=True, exist_ok=True)
    excerpts.write_text(numbered_view(source, text), encoding="utf-8")
    print(f"{source_id}: {raw.name}, {len(paragraphs)} trechos -> {excerpts.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
