"""Baixa os candidatos escolhidos no gate 3 e cria `assets/<id>.json` (provisório até `vp assets`, #20–#23).

Uso: `.venv/bin/python scripts/provisorio/baixar_escolhidos.py <episode-id> <cena> <asset-id>...`

- Lê o ativo em `candidatos/*.json` (gravado por `buscar_candidatos.py`) e baixa o arquivo final pelo adapter
  do banco (sem a chave; o Unsplash avisa o download antes), em `assets/<asset-id>.<ext>`.
- Grava `assets/<asset-id>.json` com o `sha256` do arquivo e a cena em `used_in_scenes`, ainda em
  `needs_review`: a conferência de pessoas, marcas e texto vai em `usage_notes`, e a aprovação é humana, com
  `vp approve <id> --step assets --asset <asset-id>` (§2.5, ADR 007).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap import DEFAULT_REGISTRY  # noqa: E402
from app.pipeline.schemas import Asset  # noqa: E402
from app.providers.archives.stock import sha256_file  # noqa: E402
from app.settings import load_settings  # noqa: E402

SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("scene_id")
    parser.add_argument("asset_ids", nargs="+")
    args = parser.parse_args()
    settings = load_settings(ROOT)
    episode_dir = settings.data_dir / "episodes" / args.episode_id
    records = {}
    for path in sorted((episode_dir / "candidatos").glob("*.json")):
        data = json.loads(path.read_text())
        for record in data.get("candidatos", []) if isinstance(data, dict) else []:
            records[record["ativo"]["id"]] = record
    for asset_id in args.asset_ids:
        asset = Asset.model_validate(records[asset_id]["ativo"])
        archive = DEFAULT_REGISTRY["archives"][asset.provider.value].factory(settings)  # type: ignore[misc]
        suffix = Path(urlparse(asset.original_url or "").path).suffix.lower()
        suffix = suffix if suffix in SUFFIXES else (".mp4" if "-video-" in asset.id else ".jpg")
        media = archive.download_asset(asset, episode_dir / "assets" / f"{asset.id}{suffix}")
        final = asset.model_copy(update={"sha256": sha256_file(media), "used_in_scenes": [args.scene_id]})
        (episode_dir / "assets" / f"{asset.id}.json").write_text(final.model_dump_json(indent=2) + "\n")
        print(f"{asset.id}: {media.relative_to(ROOT)} ({media.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
