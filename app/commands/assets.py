"""`vp assets`: busca candidatos visuais e baixa os escolhidos do gate 3 (#20–#23, ADR 044).

- `vp assets search <id> <pedidos.json> [--limit N]`: usa os bancos da cascata de `config/providers.toml`
  que têm adapter e chave no `.env`; os outros são pulados com o motivo (o Coverr é só manual) e o arquivo
  de cada pedido registra os pulados. Nenhum banco disponível é erro (sai sem gravar), não uma busca vazia.
  Grava `candidatos/<pedido>.json` (ativo, miniatura no cache, largura, altura, duração, banco, consulta e
  mídia) e não baixa nada. Formato do pedido e regras: `app/pipeline/candidates.py`.
- `vp assets original <id> <cena> <arquivo.mp4> --asset-id ID --composicao ... --notas ...`: registra um clipe
  animado renderizado pelo projeto (licença Original, `media: clip`; ADR 007, emenda de 2026-11-09), sem banco
  nem rede; mesmo caminho do `take` (hash, cena, ativo aprovado intocável).
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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.bootstrap.archives import available_archives
from app.commands.constants.assets_command_constants import AssetsCommandConstants as Constants
from app.errors import PipelineError
from app.pipeline.assets import AssetError, AssetIntake, require_archives
from app.pipeline.candidates import count_by_bank, episode_orientation, search_request
from app.pipeline.constants.candidates_constants import CandidatesConstants
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.provider import Provider
from app.pipeline.models.status import Status
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
    original = commands.add_parser("original", help="registra um clipe animado do projeto como Original")
    original.add_argument("episode_id", metavar="id")
    original.add_argument("scene_id", metavar="cena")
    original.add_argument("arquivo", type=Path, help="o .mp4 já renderizado")
    original.add_argument("--asset-id", required=True)
    original.add_argument("--composicao", required=True, help="composição e arquivo de código do clipe")
    original.add_argument("--notas", required=True, help="props, duração e conferência do clipe")


def run(args: argparse.Namespace, context: Context) -> int:
    handlers = {"search": _search, "take": _take, "original": _original}
    return handlers[args.assets_command](args, context)


def _original(args: argparse.Namespace, context: Context) -> int:
    """Registra um clipe renderizado pelo projeto (ADR 001, item 5; emenda de 2026-11-09 da ADR 007)."""
    if not (args.composicao.strip() and args.notas.strip()):
        raise AssetError(f"{args.asset_id}: --composicao e --notas não podem ser vazios")
    asset = Asset(
        id=args.asset_id,
        provider=Provider.ORIGINAL,
        provider_id=args.asset_id,
        license_id=SchemasConstants.ORIGINAL_LICENSE,
        origin=args.composicao,
        usage_notes=args.notas,
        media="clip",
        retrieved_at=datetime.now(UTC),
        review_status=Status.NEEDS_REVIEW,
    )
    intake = AssetIntake(context.store, ReviewWriteGuard(context.store, context.review))
    result = intake.register_local(args.episode_id, asset, args.scene_id, args.arquivo)
    print(f"{asset.id}: {Constants.LABELS[result.action]}; cenas {result.asset.used_in_scenes}")
    return 0


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
