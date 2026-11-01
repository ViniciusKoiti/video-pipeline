"""Registra material do próprio dono (receita, nota de compra) como fonte declarada (até `vp sources`, #26).

Uso: `.venv/bin/python scripts/provisorio/fonte_declarada.py <episode-id> <arquivo.md|.txt> --title "..."
[--authors "Sobrenome, Nome; ..."] [--notes "..."]`

- Fonte `kind: declared`, sem URL: o dono responde por ela, e o `vp check` avisa (gate 1). Sem dado pessoal.
- Não acessa rede. O original é copiado para `sources/raw/source-NN.md`; o texto vai para
  `sources/source-NN.txt`, **cada linha não vazia como um trecho** (receita e nota são listas: um ingrediente,
  um item, um trecho); trechos numerados em `excerpts/source-NN.md`, como `vp excerpts`.
- O registro é `app.pipeline.sources.SourceRegistry` (ADR 043): id livre sob lock, o mesmo texto não duplica,
  gate 1 aprovado recusa antes de escrever (`vp reopen --step sources`) e o `sources.json` vai por último.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.models.source_draft import SourceDraft  # noqa: E402
from app.pipeline.ports import EpisodeLocked, ImmutableManifest, ManifestNotFound  # noqa: E402
from app.pipeline.protection import ReviewWriteGuard  # noqa: E402
from app.pipeline.schemas import SourceKind  # noqa: E402
from app.pipeline.sources import SourceError, SourceRegistry, declared  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore, JsonReviewGate  # noqa: E402


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("file", help="texto do dono (.md ou .txt), sem dado pessoal")
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", default="", help="separados por ponto e vírgula")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    store = JsonFileStore(load_settings(ROOT).data_dir / "episodes")
    guard = ReviewWriteGuard(store, JsonReviewGate(store))
    registry = SourceRegistry(store, guard, lambda: datetime.now().astimezone().replace(microsecond=0))
    draft = SourceDraft(
        title=args.title,
        kind=SourceKind.DECLARED,
        authors=tuple(a.strip() for a in args.authors.split(";") if a.strip()),
        notes=args.notes,
    )
    try:
        extracted = declared(Path(args.file))
        result = registry.register(args.episode_id, draft, extracted)
    except (SourceError, ManifestNotFound, EpisodeLocked, ImmutableManifest) as error:
        raise SystemExit(f"{args.episode_id}: {error}") from error
    source = result.source
    if not result.created:
        print(f"{source.id}: este texto já está registrado; nada foi escrito")
        return
    excerpts = store.path(args.episode_id, f"excerpts/{source.id}.md").relative_to(ROOT)
    print(f"{source.id}: fonte declarada, {len(extracted.paragraphs)} trechos -> {excerpts}")


if __name__ == "__main__":
    main()
