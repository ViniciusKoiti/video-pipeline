"""Traz o resumo de um nicho do reels-radar para a pasta de um episódio (provisório, ADR 018).

Uso: `.venv/bin/python scripts/provisorio/radar_resumo.py <episode-id> <nicho> [--radar PASTA] [--atualizar]`

- Lê `<radar>/briefs/<nicho>.json` (`script_brief.v1`), que o reels-radar grava com `radar brief
  niches/<nicho>.toml`, e copia para `data/episodes/<id>/radar-brief.json`. A pasta do reels-radar vem de
  `--radar` ou de `RADAR_DIR` no `.env`.
- É uma cópia datada: o roteiro e o `vp check` leem a do episódio, e o resumo de lá pode mudar depois sem
  mudar o que este episódio usou.
- Não sobrescreve: com um resumo diferente já na pasta, só troca com `--atualizar`, e o anterior fica ao lado
  com a data dele no nome.
- Não roda coleta nem chama rede: gerar ou atualizar o resumo é no reels-radar, e coleta que gasta crédito é
  decisão do dono.
- O resumo é observação de forma em amostra pequena; nunca é fonte de fato (§2.2).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.radar import BRIEF_FILE, RadarBrief, brief_summary  # noqa: E402
from app.settings import load_settings, read_dotenv  # noqa: E402


def radar_dir(given: str | None) -> Path:
    value = given or os.environ.get("RADAR_DIR") or read_dotenv(ROOT / ".env").get("RADAR_DIR")
    if not value:
        raise SystemExit("pasta do reels-radar ausente: use --radar ou RADAR_DIR no .env")
    return Path(value).expanduser()


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("niche", help="nome do nicho, como em briefs/<nicho>.json")
    parser.add_argument("--radar", help="pasta do reels-radar (padrão: RADAR_DIR)")
    parser.add_argument("--atualizar", action="store_true", help="troca o resumo que já está no episódio")
    args = parser.parse_args()

    source = radar_dir(args.radar) / "briefs" / f"{args.niche}.json"
    if not source.is_file():
        how = f"`radar brief niches/{args.niche}.toml`"
        raise SystemExit(f"{source} não existe: gere com {how} no reels-radar")
    text = source.read_text(encoding="utf-8")
    brief = RadarBrief.model_validate_json(text)  # contrato errado para aqui, antes de gravar

    episode_dir = load_settings(ROOT).data_dir / "episodes" / args.episode_id
    if not episode_dir.is_dir():
        raise SystemExit(f"episódio {args.episode_id} não existe em {episode_dir.parent}")
    target = episode_dir / BRIEF_FILE
    if target.is_file():
        current = target.read_text(encoding="utf-8")
        if current == text:
            print(f"já está atualizado: {brief_summary(brief)}")
            return
        if not args.atualizar:
            old = RadarBrief.model_validate_json(current)
            raise SystemExit(
                f"{target} já tem outro resumo ({old.niche}, de {old.generated_at:%d/%m/%Y}); "
                "use --atualizar para trocar"
            )
        old = RadarBrief.model_validate_json(current)
        kept = episode_dir / f"radar-brief.{old.generated_at:%Y%m%d-%H%M%S}.json"
        target.rename(kept)
        print(f"resumo anterior guardado em {kept.name}")
    target.write_text(text, encoding="utf-8")
    print(brief_summary(brief))


if __name__ == "__main__":
    main()
