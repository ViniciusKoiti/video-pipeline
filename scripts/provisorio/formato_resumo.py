"""Leva o perfil de formato do nicho para a pasta de um episódio (provisório, ADR 031 parte B).

Uso: `.venv/bin/python scripts/provisorio/formato_resumo.py <episode-id> <formato-brief.json> [--atualizar]`

- O perfil é gravado pela skill `analise-de-formato` (`brief.py`), um por grupo do nicho; aqui ele é conferido
  pelo schema (`FormatBrief`) e copiado para `data/episodes/<id>/formato-brief.json`.
- É uma cópia datada: o roteiro, o `vp numeros` e o `vp check` leem a do episódio, e a análise pode mudar
  depois sem mudar o que este episódio usou.
- Não sobrescreve: com um perfil diferente já na pasta, só troca com `--atualizar`, e o anterior fica ao lado
  com a data dele no nome (nunca por cima de um guardado antes). A cópia é `app.pipeline.briefs.install_brief`
  (ADR 047): validada antes de escrever, gravada inteira e com o episódio travado; a pasta do episódio vem do
  `data_dir` das configurações, como no `radar_resumo.py`.
- É forma, nunca fonte (§2.2): nenhum número do perfil vai para a fala ou para a tela.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.pipeline.briefs import format_spec, install_brief  # noqa: E402
from app.pipeline.constants.numbers_constants import NumbersConstants  # noqa: E402
from app.pipeline.models.brief_action import BriefAction  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore  # noqa: E402


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("perfil", type=Path)
    parser.add_argument("--atualizar", action="store_true", help="troca o perfil que já está na pasta")
    args = parser.parse_args()

    text = args.perfil.read_text(encoding="utf-8")
    store = JsonFileStore(load_settings(ROOT).data_dir / "episodes")
    result = install_brief(store, args.episode_id, format_spec(), text, replace=args.atualizar)
    brief = result.brief
    target = store.path(args.episode_id, NumbersConstants.FORMAT_FILE)
    if result.action is BriefAction.UNCHANGED:
        print(f"{target}: já é este perfil")
        return
    if result.archived:
        print(f"perfil anterior guardado em {result.archived}")
    patterns = [name for name, m in brief.medidas.items() if m.forca == "pattern"]
    print(
        f"{target}: {brief.nicho}, grupo {brief.grupo}, {brief.data}, n = {brief.n}; "
        f"pattern: {', '.join(patterns) or 'nenhuma'}"
    )


if __name__ == "__main__":
    raise SystemExit(run("formato_resumo", main))
