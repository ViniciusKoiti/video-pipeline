#!/usr/bin/env bash
# Gate único local e do CI: lint, tipagem, arquitetura, tamanho e regressão.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

failed=0
printf '\nLint\n'
uv run --no-sync ruff check . || failed=1

printf '\nTipagem estática (Mypy estrito em app/)\n'
uv run --no-sync mypy || failed=1

printf '\nTestes (incluem arquitetura e tamanho 200/50)\n'
uv run --no-sync pytest -q || failed=1

if (( failed )); then
  printf '\nQualidade: reprovada. Corrija as falhas acima antes de avançar.\n'
else
  printf '\nQualidade: aprovada.\n'
fi
exit "$failed"
