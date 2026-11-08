#!/usr/bin/env bash
# Mede a idempotência (Short "eu medi"): 15 rodadas de Demo.java nos modos sem-chave e com-chave, cada
# execução num processo novo. Antes de cada rodada roda cpu_probe() (máquina limitada = medida inválida);
# espera a sonda abaixo de 0,12 s, com 10 s de pausa entre rodadas. Uso: ./medir.sh > resultado.txt
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
JAVA=${JAVA:-java}
RAIZ=$(cd ../../.. && pwd)
SONDA=${SONDA:-$RAIZ/.venv/bin/python}
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
VERS=$($JAVA -version 2>&1 | head -1)
echo "# $(date -Iseconds) | $VERS | $CPU | $(nproc) processadores visiveis | pagamentos: 10000, perda simulada de 30% das respostas (semente 42), ate 10 tentativas por pagamento | tempo por pedido so em memoria (sem rede, sem banco) | sonda abaixo de ${LIVRE:-0.12} s antes de cada rodada, pausa de ${PAUSA:-10} s | $RODADAS rodadas"
estat() {
  printf '%s\n' "$@" | sort -g | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
sonda() { (cd "$RAIZ" && "$SONDA" -c "from app.pipeline.bench import cpu_probe; print(f'{cpu_probe():.3f}')"); }
CHAVES="duplicadas cobrancas pedidos chaves_guardadas us_por_pedido"
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
  for modo in sem-chave com-chave; do
    linha=$($JAVA Demo.java "$modo")
    echo "rodada=$r cpu_probe=$p $linha"
    for k in $CHAVES; do
      v=$(echo "$linha" | sed -E "s/.*(^| )$k=([0-9.]+).*/\2/")
      valores[$modo-$k]="${valores[$modo-$k]:-} $v"
    done
  done
done
echo "## cpu_probe ao fim: $(sonda)"
for modo in sem-chave com-chave; do
  for k in $CHAVES; do
    echo "## resumo $modo $k $(estat ${valores[$modo-$k]})"
  done
done
med() { echo "$1" | sed -E 's/.*mediana=([0-9.]+).*/\1/'; }
tempo_sem=$(med "$(estat ${valores[sem-chave-us_por_pedido]})")
tempo_com=$(med "$(estat ${valores[com-chave-us_por_pedido]})")
echo "## razao tempo por pedido com/sem chave (medianas) = $(awk -v a="$tempo_com" -v b="$tempo_sem" 'BEGIN{printf "%.2f", a/b}')"
