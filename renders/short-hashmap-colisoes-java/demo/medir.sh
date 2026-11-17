#!/usr/bin/env bash
# Mede HashMap e colisões (Short "eu medi"): 15 rodadas de Demo.java nos modos bom, fraco, constante e
# constante-comparable, cada execução num processo novo (com aquecimento da JVM dentro do processo).
# Antes de cada rodada roda cpu_probe() (máquina limitada = medida inválida); espera a sonda abaixo de 0,12 s,
# com 10 s de pausa entre rodadas. Uso: bash medir.sh (grava resultado.txt)
set -euo pipefail
cd "$(dirname "$0")"
# A saída vai direto para resultado.txt e os avisos de erro para medir.err (uso: bash medir.sh).
exec > resultado.txt 2> medir.err
RODADAS=${RODADAS:-15}
JAVA=${JAVA:-java}
RAIZ=$(cd ../../.. && pwd)
SONDA=${SONDA:-$RAIZ/.venv/bin/python}
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
VERS=$($JAVA -version 2>&1 | head -1)
echo "# $(date -Iseconds) | $VERS | $CPU | $(nproc) processadores visiveis | 20000 chaves ChaveSessao(usuario, dispositivo), mesmas 20000 buscas em ordem embaralhada (semente 42) com instancias novas das chaves | aquecimento de 200 ciclos com 2000 chaves antes de medir | tempo so em memoria (sem rede, sem banco) | sonda abaixo de ${LIVRE:-0.12} s antes de cada rodada, pausa de ${PAUSA:-10} s | $RODADAS rodadas"
estat() {
  printf '%s\n' "$@" | sort -g | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
sonda() { (cd "$RAIZ" && "$SONDA" -c "from app.pipeline.bench import cpu_probe; print(f'{cpu_probe():.3f}')"); }
MODOS="bom fraco constante constante-comparable"
CHAVES="hashes_distintos maior_grupo equals_por_busca ms_insercao ms_busca ns_por_busca"
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
    linha=$($JAVA Demo.java "$modo")
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
med() { echo "$1" | sed -E 's/.*mediana=([0-9.]+).*/\1/'; }
base=$(med "$(estat ${valores[bom-ns_por_busca]})")
for modo in fraco constante constante-comparable; do
  t=$(med "$(estat ${valores[$modo-ns_por_busca]})")
  echo "## razao ns por busca $modo/bom (medianas) = $(awk -v a="$t" -v b="$base" 'BEGIN{printf "%.1f", a/b}')"
done
