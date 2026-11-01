"""`vp briefs`: leva o resumo do radar e o perfil de formato do nicho para a pasta de um episódio (ADR 047).

- `vp briefs radar <id> <nicho> [--radar PASTA] [--atualizar]` (ADR 018): lê `<radar>/briefs/<nicho>.json`
  (`script_brief.v1`, gravado pelo reels-radar com `radar brief niches/<nicho>.toml`) e copia para
  `radar-brief.json` do episódio. A pasta do reels-radar vem de `--radar` ou de `RADAR_DIR` no ambiente ou
  no `.env`. Não roda coleta nem chama rede: gerar o resumo é no reels-radar, e coleta que gasta crédito é
  decisão do dono. O resumo é observação de forma em amostra pequena; nunca é fonte de fato (§2.2).
- `vp briefs formato <id> <formato-brief.json> [--atualizar]` (ADR 031, parte B): confere o perfil gravado
  pela skill `analise-de-formato` (`FormatBrief`) e copia para `formato-brief.json`. É forma, nunca fonte:
  nenhum número do perfil vai para a fala ou para a tela.

As duas cópias são datadas e não sobrescrevem: com um conteúdo diferente já na pasta, só trocam com
`--atualizar`, e o anterior fica ao lado com a data dele no nome. A cópia é `install_brief`: validada antes
de escrever, gravada inteira e com o episódio travado.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.pipeline.briefs import BriefError, format_spec, install_brief, radar_spec
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.models.brief_action import BriefAction
from app.pipeline.numbers import FormatBrief
from app.pipeline.ports import Context
from app.pipeline.radar import RadarBrief, brief_summary
from app.settings import read_dotenv


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="briefs_command", required=True)
    radar = commands.add_parser("radar", help="resumo do nicho do reels-radar -> radar-brief.json")
    radar.add_argument("episode_id", metavar="id")
    radar.add_argument("niche", help="nome do nicho, como em briefs/<nicho>.json")
    radar.add_argument("--radar", help="pasta do reels-radar (padrão: RADAR_DIR)")
    own = commands.add_parser("formato", help="perfil de formato do nicho -> formato-brief.json")
    own.add_argument("episode_id", metavar="id")
    own.add_argument("perfil", type=Path)
    for sub in (radar, own):
        sub.add_argument("--atualizar", action="store_true", help="troca o que já está no episódio")


def run(args: argparse.Namespace, context: Context) -> int:
    if args.briefs_command == "radar":
        return _radar(args, context)
    return _format(args, context)


def _radar_dir(given: str | None, root: Path) -> Path:
    value = given or os.environ.get("RADAR_DIR") or read_dotenv(root / ".env").get("RADAR_DIR")
    if not value:
        raise BriefError("pasta do reels-radar ausente: use --radar ou RADAR_DIR no .env")
    return Path(value).expanduser()


def _radar(args: argparse.Namespace, context: Context) -> int:
    source = _radar_dir(args.radar, context.settings.data_dir.parent) / "briefs" / f"{args.niche}.json"
    if not source.is_file():
        raise BriefError(
            f"{source} não existe: gere com `radar brief niches/{args.niche}.toml` no reels-radar"
        )
    text = source.read_text(encoding="utf-8")
    brief = RadarBrief.model_validate_json(text)
    result = install_brief(context.store, args.episode_id, radar_spec(), text, replace=args.atualizar)
    if result.action is BriefAction.UNCHANGED:
        print(f"já está atualizado: {brief_summary(brief)}")
        return 0
    if result.archived:
        print(f"resumo anterior guardado em {result.archived}")
    print(brief_summary(brief))
    return 0


def _format(args: argparse.Namespace, context: Context) -> int:
    text = args.perfil.read_text(encoding="utf-8")
    result = install_brief(context.store, args.episode_id, format_spec(), text, replace=args.atualizar)
    brief = FormatBrief.model_validate_json(text)  # já conferido por `install_brief`
    target = context.store.path(args.episode_id, NumbersConstants.FORMAT_FILE)
    if result.action is BriefAction.UNCHANGED:
        print(f"{target}: já é este perfil")
        return 0
    if result.archived:
        print(f"perfil anterior guardado em {result.archived}")
    patterns = [name for name, m in brief.medidas.items() if m.forca == "pattern"]
    print(
        f"{target}: {brief.nicho}, grupo {brief.grupo}, {brief.data}, n = {brief.n}; "
        f"pattern: {', '.join(patterns) or 'nenhuma'}"
    )
    return 0
