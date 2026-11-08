"""`vp assets`: busca candidatos visuais e baixa os escolhidos do gate 3 (#20–#23, ADR 044).

- `vp assets search <id> <pedidos.json> [--limit N]`: usa os bancos da cascata de `config/providers.toml`
  que têm adapter e chave no `.env`; os outros são pulados com o motivo (o Coverr é só manual) e o arquivo
  de cada pedido registra os pulados. Nenhum banco disponível é erro (sai sem gravar), não uma busca vazia.
  Grava `candidatos/<pedido>.json` (ativo, miniatura no cache, largura, altura, duração, banco, consulta e
  mídia) e não baixa nada. Formato do pedido e regras: `app/pipeline/candidates.py`.
- `vp assets take <id> <cena> <asset-id>...`: lê o ativo em `candidatos/*.json` e baixa o arquivo final pelo
  adapter do banco, em `assets/<asset-id>.<ext>`, ainda em `needs_review` (a aprovação é humana, `vp approve
  <id> --step assets --asset <asset-id>`). Ativo já baixado e íntegro não é baixado de novo, a cena entra
  em `used_in_scenes` sem apagar as anteriores e ativo aprovado nunca é alterado (`AssetIntake`). Falha de
  um ativo não para os outros; o código de saída é 1 se algum falhou.

Só chama os bancos quando o dono pede na sessão (§14); a regra de custo zero vale (`PaidApiBlocked` para).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.bootstrap.archives import available_archives
from app.commands.constants.assets_command_constants import AssetsCommandConstants as Constants
from app.errors import PipelineError
from app.pipeline.assets import AssetError, AssetIntake, require_archives
from app.pipeline.candidates import count_by_bank, episode_orientation, search_request
from app.pipeline.constants.candidates_constants import CandidatesConstants
from app.pipeline.ports import Context
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import Asset


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="assets_command", required=True)
    search = commands.add_parser("search", help="busca candidatos nos bancos de imagem (não baixa nada)")
    search.add_argument("episode_id", metavar="id")
    search.add_argument("pedidos", type=Path)
    search.add_argument(
        "--limit",
        type=int,
        default=CandidatesConstants.DEFAULT_LIMIT,
        help="candidatos por chamada (padrão 5)",
    )
    take = commands.add_parser("take", help="baixa os candidatos escolhidos e cria assets/<id>.json")
    take.add_argument("episode_id", metavar="id")
    take.add_argument("scene_id", metavar="cena")
    take.add_argument("asset_ids", metavar="asset-id", nargs="+")


def run(args: argparse.Namespace, context: Context) -> int:
    return _search(args, context) if args.assets_command == "search" else _take(args, context)


def _search(args: argparse.Namespace, context: Context) -> int:
    root = context.settings.data_dir.parent
    out_dir = context.store.path(args.episode_id, "candidatos")
    availability = available_archives(context.settings)
    for skipped in availability.skipped:
        print(f"pulado: {skipped.name} ({skipped.reason})")
    archives = require_archives(availability)  # sem banco: erro, e nada é gravado
    out_dir.mkdir(parents=True, exist_ok=True)
    print("bancos:", ", ".join(a.info.name for a in archives))
    default = episode_orientation(context.store.path(args.episode_id, ""))
    for request in json.loads(args.pedidos.read_text())["pedidos"]:
        result, orientation = search_request(
            archives, availability.skipped, request, default, args.limit, root
        )
        (out_dir / f"{request['id']}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        )
        found, failures = len(result["candidatos"]), len(result["falhas"])
        print(
            f"{request['id']} ({orientation}): {found} candidatos {count_by_bank(result)}; falhas: {failures}"
        )
    return 0


def candidates(episode_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in sorted((episode_dir / "candidatos").glob("*.json")):
        data = json.loads(path.read_text())
        for record in data.get("candidatos", []) if isinstance(data, dict) else []:
            records[record["ativo"]["id"]] = record
    return records


def _take(args: argparse.Namespace, context: Context) -> int:
    store = context.store
    intake = AssetIntake(store, ReviewWriteGuard(store, context.review))
    records = candidates(store.path(args.episode_id, ""))
    availability = available_archives(context.settings)
    banks = {bank.info.name: bank for bank in require_archives(availability)}
    why = {s.name: s.reason for s in availability.skipped}
    failed = False
    for asset_id in args.asset_ids:
        try:
            if asset_id not in records:
                raise AssetError(f"{asset_id}: não está em candidatos/ (rode `vp assets search`)")
            asset = Asset.model_validate(records[asset_id]["ativo"])
            bank = asset.provider.value
            if bank not in banks:
                raise AssetError(
                    f"{asset_id}: o banco {bank} não está disponível ({why.get(bank, 'fora da cascata')})"
                )
            result = intake.take(args.episode_id, asset, args.scene_id, banks[bank])
        except PipelineError as error:  # recuperação por ativo: o erro de um não para os outros
            print(f"{asset_id}: ERRO {error}", file=sys.stderr)
            failed = True
            continue
        print(f"{asset_id}: {Constants.LABELS[result.action]}; cenas {result.asset.used_in_scenes}")
    return 1 if failed else 0
