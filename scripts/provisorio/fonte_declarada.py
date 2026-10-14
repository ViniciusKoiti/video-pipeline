"""Registra material do próprio dono (receita, nota de compra) como fonte declarada (até `vp sources`, #26).

Uso: `.venv/bin/python scripts/provisorio/fonte_declarada.py <episode-id> <arquivo.md|.txt> --title "..."
[--authors "Sobrenome, Nome; ..."] [--notes "..."]`

- Fonte `kind: declared`, sem URL: o dono responde por ela, e o `vp check` avisa (gate 1). Sem dado pessoal.
- Não acessa rede. O original é copiado para `sources/raw/source-NN.md`; o texto vai para
  `sources/source-NN.txt`, **cada linha não vazia como um trecho** (receita e nota são listas: um ingrediente,
  um item, um trecho); trechos numerados em `excerpts/source-NN.md`, como `vp excerpts`.
- O id é o próximo `source-NN` livre; nada existente é sobrescrito.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.excerpts import numbered_view  # noqa: E402
from app.pipeline.extract import as_source_text  # noqa: E402
from app.pipeline.schemas import Source, SourceKind, SourcesManifest  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore  # noqa: E402


def line_paragraphs(text: str) -> list[str]:
    """Cada linha não vazia vira um trecho; espaços repetidos são juntados."""
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("file", help="texto do dono (.md ou .txt), sem dado pessoal")
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", default="", help="separados por ponto e vírgula")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    original = Path(args.file)
    if not original.is_file():
        raise SystemExit(f"{original} não existe")
    paragraphs = line_paragraphs(original.read_text(encoding="utf-8"))
    if not paragraphs:
        raise SystemExit(f"{original}: nenhum texto; fonte não registrada")

    store = JsonFileStore(load_settings(ROOT).data_dir / "episodes")
    manifest = store.read(args.episode_id, "sources.json", SourcesManifest)
    number = max((int(s.id.removeprefix("source-")) for s in manifest.sources), default=0) + 1
    source_id = f"source-{number:02d}"
    raw = store.path(args.episode_id, f"sources/raw/{source_id}{original.suffix or '.txt'}")
    raw.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, raw)

    text = as_source_text(paragraphs)
    local_path = f"sources/{source_id}.txt"
    store.path(args.episode_id, local_path).write_text(text, encoding="utf-8")
    source = Source(
        id=source_id,
        title=args.title,
        url=None,
        kind=SourceKind.DECLARED,
        retrieved_at=datetime.now().astimezone().replace(microsecond=0),
        local_path=local_path,
        notes=args.notes,
        authors=[a.strip() for a in args.authors.split(";") if a.strip()],
    )
    updated = manifest.model_copy(update={"sources": [*manifest.sources, source]})
    store.write(args.episode_id, "sources.json", updated)
    excerpts = store.path(args.episode_id, f"excerpts/{source_id}.md")
    excerpts.parent.mkdir(parents=True, exist_ok=True)
    excerpts.write_text(numbered_view(source, text), encoding="utf-8")
    print(f"{source_id}: fonte declarada, {len(paragraphs)} trechos -> {excerpts.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
