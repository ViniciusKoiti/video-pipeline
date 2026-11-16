#!/usr/bin/env bash
# Mede o consistent hashing (Short "eu medi"): 15 rodadas de Demo.java em quatro modos (módulo e anel com 1, 10 e
# 100 pontos por servidor), cada execução num processo novo. As frações de chaves movidas e a carga são
# determinísticas (semente fixa, MD5); o que varia entre rodadas é só o tempo da busca. Antes de cada rodada roda
# cpu_probe() (máquina limitada = medida inválida): espera a sonda abaixo de 0,12 s, com 10 s de pausa entre
# rodadas. Uso: bash medir.sh > resultado.txt
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
JAVA=${JAVA:-java}
RAIZ=$(cd ../../.. && pwd)
SONDA=${SONDA:-$RAIZ/.venv/bin/python}
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
VERS=$($JAVA -version 2>&1 | head -1)
echo "# $(date -Iseconds) | $VERS | $CPU | $(nproc) processadores visiveis | 100000 ids de sessao (semente 42), hash = 4 primeiros bytes do MD5, servidores 4 -> 5, anel em TreeMap, 20 conjuntos de nomes de servidor por modo do anel | tempo da busca so em memoria | sonda abaixo de ${LIVRE:-0.12} s antes de cada rodada, pausa de ${PAUSA:-10} s | $RODADAS rodadas"
estat() {
  printf '%s\n' "$@" | sort -g | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
sonda() { (cd "$RAIZ" && "$SONDA" -c "from app.pipeline.bench import cpu_probe; print(f'{cpu_probe():.3f}')"); }
CHAVES="movidas_pct movidas_pct_min movidas_pct_max fora_do_novo desvio_pct desvio_pct_max carga_max_pct_do_ideal carga_min_pct_do_ideal ns_por_busca"
MODOS="modulo anel-1 anel-10 anel-100"
declare -A valores
for r in $(seq 1 "$RODADAS"); do
  # Pausa para a CPU esfriar e espera a sonda abaixo de LIVRE, por até 5 minutos.
  [ "$r" = 1 ] || sleep "${PAUSA:-10}"
  limite=$(( $(date +%s) + 300 ))
  p=$(sonda)
  while awk -v p="$p" -v l="${LIVRE:-0.12}" 'BEGIN{exit !(p >= l)}'; do
    if [ "$(date +%s)" -ge "$limite" ]; then
      echo "## abortado na rodada=$r: cpu_probe=$p acima de ${LIVRE:-0.12} s por 5 minutos (maquina limitada); medida invalida" >&2
      exit 3
    fi
    sleep 10; p=$(sonda)
  done
  for modo in $MODOS; do
    case "$modo" in
      modulo) linha=$($JAVA Demo.java modulo) ;;
      anel-*) linha=$($JAVA Demo.java anel "${modo#anel-}") ;;
    esac
    echo "rodada=$r cpu_probe=$p $linha"
    for k in $CHAVES; do
      v=$(echo "$linha" | sed -E "s/.*(^| )$k=([0-9.]+).*/\2/")
      valores[$modo-$k]="${valores[$modo-$k]:-} $v"
    done
  done
done
echo "## cpu_probe ao fim: $(sonda)"
for modo in $MODOS; do
  for k in $CHAVES; do
    echo "## resumo $modo $k $(estat ${valores[$modo-$k]})"
  done
done
