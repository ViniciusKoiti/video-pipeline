"""Leva o perfil de formato do nicho para a pasta de um episódio (provisório, ADR 031 parte B).

Uso: `.venv/bin/python scripts/provisorio/formato_resumo.py <episode-id> <formato-brief.json> [--atualizar]`

- O perfil é gravado pela skill `analise-de-formato` (`brief.py`), um por grupo do nicho; aqui ele é conferido
  pelo schema (`FormatBrief`) e copiado para `data/episodes/<id>/formato-brief.json`.
- É uma cópia datada: o roteiro, o `vp numeros` e o `vp check` leem a do episódio, e a análise pode mudar
  depois sem mudar o que este episódio usou.
- Não sobrescreve: com um perfil diferente já na pasta, só troca com `--atualizar`, e o anterior fica ao lado
  com a data dele no nome.
- É forma, nunca fonte (§2.2): nenhum número do perfil vai para a fala ou para a tela.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.numbers import FORMAT_FILE, FormatBrief  # noqa: E402


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("perfil", type=Path)
    parser.add_argument("--atualizar", action="store_true", help="troca o perfil que já está na pasta")
    args = parser.parse_args()

    text = args.perfil.read_text(encoding="utf-8")
    brief = FormatBrief.model_validate_json(text)
    target = ROOT / "data" / "episodes" / args.episode_id / FORMAT_FILE
    if not target.parent.is_dir():
        raise SystemExit(f"episódio {args.episode_id} não existe em data/episodes/")
    if target.is_file():
        if target.read_text(encoding="utf-8") == text:
            print(f"{target}: já é este perfil")
            return
        if not args.atualizar:
            raise SystemExit(f"{target} já existe com outro perfil: use --atualizar")
        old = FormatBrief.model_validate_json(target.read_text(encoding="utf-8"))
        target.rename(target.with_name(f"formato-brief-{old.data}.json"))
    target.write_text(text, encoding="utf-8")
    patterns = [name for name, m in brief.medidas.items() if m.forca == "pattern"]
    print(
        f"{target}: {brief.nicho}, grupo {brief.grupo}, {brief.data}, n = {brief.n}; "
        f"pattern: {', '.join(patterns) or 'nenhuma'}"
    )


if __name__ == "__main__":
    main()
