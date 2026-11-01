"""Baixa os candidatos escolhidos no gate 3 e cria `assets/<id>.json` (provisório até `vp assets`, #20–#23).

Uso: `.venv/bin/python scripts/provisorio/baixar_escolhidos.py <episode-id> <cena> <asset-id>...`

- Lê o ativo em `candidatos/*.json` (gravado por `buscar_candidatos.py`) e baixa o arquivo final pelo adapter
  do banco (sem a chave; o Unsplash avisa o download antes), em `assets/<asset-id>.<ext>`.
- Grava `assets/<asset-id>.json` com o `sha256` do arquivo e a cena em `used_in_scenes`, ainda em
  `needs_review`: a conferência de pessoas, marcas e texto vai em `usage_notes`, e a aprovação é humana, com
  `vp approve <id> --step assets --asset <asset-id>` (§2.5, ADR 007).
- A entrada é `app.pipeline.assets.AssetIntake` (ADR 044): ativo já baixado e íntegro não é baixado de novo, a
  cena entra em `used_in_scenes` sem apagar as anteriores, repetir é idempotente e ativo aprovado nunca é
  alterado (o uso em outra cena fica no `asset_id` do `scenes.json`). Falha de um ativo não para os outros;
  o código de saída é 1 se algum falhou.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap.archives import available_archives  # noqa: E402
from app.commands.errors import run  # noqa: E402
from app.errors import PipelineError  # noqa: E402
from app.pipeline.assets import AssetError, AssetIntake, require_archives  # noqa: E402
from app.pipeline.models.intake_action import IntakeAction  # noqa: E402
from app.pipeline.protection import ReviewWriteGuard  # noqa: E402
from app.pipeline.schemas import Asset  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore, JsonReviewGate  # noqa: E402

LABELS = {
    IntakeAction.DOWNLOADED: "baixado",
    IntakeAction.REPAIRED: "mídia refeita (a anterior não batia com o sha256)",
    IntakeAction.SCENE_ADDED: "já baixado; cena acrescentada",
    IntakeAction.UNCHANGED: "já baixado; nada a fazer",
    IntakeAction.APPROVED_UNTOUCHED: "aprovado; não alterado (use o asset_id no scenes.json)",
}


def candidates(episode_dir: Path) -> dict[str, dict]:
    records = {}
    for path in sorted((episode_dir / "candidatos").glob("*.json")):
        data = json.loads(path.read_text())
        for record in data.get("candidatos", []) if isinstance(data, dict) else []:
            records[record["ativo"]["id"]] = record
    return records


def main() -> int:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("scene_id")
    parser.add_argument("asset_ids", nargs="+")
    args = parser.parse_args()
    settings = load_settings(ROOT)
    store = JsonFileStore(settings.data_dir / "episodes")
    intake = AssetIntake(store, ReviewWriteGuard(store, JsonReviewGate(store)))
    records = candidates(store.path(args.episode_id, ""))
    availability = available_archives(settings)
    banks = {bank.info.name: bank for bank in require_archives(availability)}
    failed = False
    for asset_id in args.asset_ids:
        try:
            if asset_id not in records:
                raise AssetError(f"{asset_id}: não está em candidatos/ (rode buscar_candidatos.py)")
            asset = Asset.model_validate(records[asset_id]["ativo"])
            if asset.provider.value not in banks:
                bank = asset.provider.value
                why = {s.name: s.reason for s in availability.skipped}.get(bank, "fora da cascata")
                raise AssetError(f"{asset_id}: o banco {bank} não está disponível ({why})")
            result = intake.take(args.episode_id, asset, args.scene_id, banks[asset.provider.value])
        except PipelineError as error:  # recuperação por ativo: o erro de um não para os outros
            print(f"{asset_id}: ERRO {error}", file=sys.stderr)
            failed = True
            continue
        print(f"{asset_id}: {LABELS[result.action]}; cenas {result.asset.used_in_scenes}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run("baixar_escolhidos", main))
