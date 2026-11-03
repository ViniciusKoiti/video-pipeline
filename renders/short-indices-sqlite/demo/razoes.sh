#!/usr/bin/env bash
# Razões entre as medianas de um resultado.txt de medir.sh (derivadas, não medidas à parte).
# Uso: ./razoes.sh resultado.txt   (medir.sh chama no fim; imprime linhas "## razao ...")
set -euo pipefail
med() { grep "^## resumo $1 " "$2" | sed -E 's/.*mediana=([0-9.]+).*/\1/'; }
f=$1
awk -v s="$(med sem_indice_ms "$f")" -v c="$(med com_indice_ms "$f")" \
    -v is="$(med inserir_sem_indice_ms "$f")" -v ic="$(med inserir_com_indice_ms "$f")" \
    -v ta="$(med tamanho_antes_mb "$f")" -v td="$(med tamanho_depois_mb "$f")" 'BEGIN{
  printf "## razao consulta sem/com indice (medianas) = %.1f\n", s/c
  printf "## razao inserir com/sem indice (medianas) = %.2f\n", ic/is
  printf "## diferenca tamanho depois-antes (medianas) mb = %.1f\n", td-ta
}'
