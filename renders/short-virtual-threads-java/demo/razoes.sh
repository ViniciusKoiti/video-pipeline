#!/usr/bin/env bash
# Razoes entre as medianas de um resultado.txt de medir.sh (derivadas, nao medidas a parte).
# Uso: ./razoes.sh resultado.txt   (medir.sh chama no fim; imprime linhas "## razao ...")
set -euo pipefail
med() { grep "^## resumo $1 " "$2" | sed -E 's/.*mediana=([0-9.]+).*/\1/'; }
f=$1
awk -v p="$(med plataforma_ms "$f")" -v v="$(med virtual_ms "$f")" -v c="$(med virtual_com_pool_ms "$f")" 'BEGIN{
  printf "## razao plataforma/virtual (medianas) = %.1f\n", p/v
  printf "## razao virtual-com-pool/virtual (medianas) = %.1f\n", c/v
  printf "## razao virtual-com-pool/plataforma (medianas) = %.2f\n", c/p
  printf "## esperado teorico plataforma = 10000/200*100 ms = 5000 ms; com pool = 10000/50*100 ms = 20000 ms\n"
}'
