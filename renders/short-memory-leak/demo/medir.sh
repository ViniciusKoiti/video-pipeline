#!/usr/bin/env bash
# Mede o memory leak (pauta 1): 15 rodadas de cada versão, 10 s cada; a série segundo a segundo da primeira
# rodada de cada versão fica inteira no resultado, as outras só com o RSS aos 10 s; a mediana no fim.
# Uso: ./medir.sh > resultado.txt   (rodar com a máquina livre: cpu_probe antes, pelo chamador)
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
gcc -O2 -o vazamento vazamento.c
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
echo "# $(date -Iseconds) | $(gcc --version | head -1) -O2 | $CPU | bloco 64 KB a cada 1 ms, 10 s | $RODADAS rodadas por versao"
for versao in vaza libera; do
  flag=""; [ "$versao" = libera ] && flag="--libera"
  finais=()
  for r in $(seq 1 "$RODADAS"); do
    saida=$(./vazamento $flag)
    if [ "$r" -eq 1 ]; then
      echo "## serie versao=$versao rodada=1"
      echo "$saida" | grep '^t=' | sed "s/^/versao=$versao rodada=1 /"
    fi
    fim=$(echo "$saida" | grep ' fim$' | sed -E 's/.*rss_mb=([0-9.]+).*/\1/')
    iter=$(echo "$saida" | grep ' fim$' | sed -E 's/.*iteracoes=([0-9]+).*/\1/')
    echo "versao=$versao rodada=$r rss_10s_mb=$fim iteracoes=$iter"
    finais+=("$fim")
  done
  mediana=$(printf '%s\n' "${finais[@]}" | sort -n | awk '{a[NR]=$1} END{if(NR%2){print a[(NR+1)/2]}else{printf "%.1f\n",(a[NR/2]+a[NR/2+1])/2}}')
  minimo=$(printf '%s\n' "${finais[@]}" | sort -n | head -1)
  maximo=$(printf '%s\n' "${finais[@]}" | sort -n | tail -1)
  echo "## resumo versao=$versao rss_10s_mb mediana=$mediana minimo=$minimo maximo=$maximo"
done
