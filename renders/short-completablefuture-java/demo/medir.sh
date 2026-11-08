#!/usr/bin/env bash
# Mede CompletableFuture (Short Java): 15 rodadas de cada modo (sequencial, composto, timeout).
# Cada rodada é uma JVM nova; o tempo é medido dentro do programa, a partir do início de main.
# Uso: ./medir.sh > resultado.txt   (rodar com a máquina livre: cpu_probe antes, pelo chamador)
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
echo "# $(date -Iseconds) | $(java -version 2>&1 | head -1) | $CPU | $(nproc) processadores visiveis | consultas simuladas: preco 300 ms, estoque 200 ms; timeout: estoque 2000 ms com orTimeout 500 ms | pool fixo de 4 threads | $RODADAS rodadas por modo"
estat() {
  printf '%s\n' "$@" | sort -n | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
for modo in sequencial composto timeout; do
  tempos=()
  fins=()
  for r in $(seq 1 "$RODADAS"); do
    saida=$(java Demo.java "$modo")
    ms=$(echo "$saida" | sed -E 's/^ms=([0-9.]+).*/\1/')
    echo "modo=$modo rodada=$r $saida"
    tempos+=("$ms")
    if [ "$modo" = timeout ]; then
      fins+=("$(echo "$saida" | sed -E 's/.*tarefa_terminou_em_ms=([0-9.]+).*/\1/')")
    fi
  done
  echo "## resumo modo=$modo ms $(estat "${tempos[@]}")"
  if [ "$modo" = timeout ]; then
    echo "## resumo modo=$modo tarefa_terminou_em_ms $(estat "${fins[@]}")"
  fi
done
