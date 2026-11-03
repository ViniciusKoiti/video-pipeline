#!/usr/bin/env bash
# Mede a concorrência (pauta 2): 15 rodadas de cada versão (sem proteção, mutex, atomic); total e tempo de cada
# rodada; mediana, mínimo e máximo no fim. Antes, mostra no objdump o laço da função soma.
# Uso: ./medir.sh > resultado.txt   (rodar com a máquina livre: cpu_probe antes, pelo chamador)
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
gcc -O2 -pthread -o contador contador.c
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
echo "# $(date -Iseconds) | $(gcc --version | head -1) -O2 -pthread | $CPU | $(nproc) processadores visiveis | 2 threads x 1000000 somas | $RODADAS rodadas por versao"
echo "## objdump da funcao soma (laco presente)"
objdump -d --no-show-raw-insn contador | awk '/<soma>:/{p=1} p{print} p&&/ret/{exit}' | sed 's/^/objdump /'
estat() {
  printf '%s\n' "$@" | sort -n | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
for versao in sem mutex atomic; do
  flag=""
  [ "$versao" != sem ] && flag="--$versao"
  totais=()
  tempos=()
  for r in $(seq 1 "$RODADAS"); do
    saida=$(./contador $flag)
    total=$(echo "$saida" | sed -E 's/.*total=([0-9]+).*/\1/')
    ms=$(echo "$saida" | sed -E 's/.*ms=([0-9.]+).*/\1/')
    echo "versao=$versao rodada=$r total=$total ms=$ms"
    totais+=("$total")
    tempos+=("$ms")
  done
  echo "## resumo versao=$versao total $(estat "${totais[@]}")"
  echo "## resumo versao=$versao ms $(estat "${tempos[@]}")"
done
