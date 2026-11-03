#!/usr/bin/env bash
# Mede o índice no SQLite (Short "eu medi"): 15 rodadas de indice.py, cada uma num processo novo e
# num banco criado do zero. Antes de cada rodada roda cpu_probe() (máquina limitada =
# medida inválida); cada rodada espera a sonda abaixo de 0,12 s, com 10 s de pausa entre rodadas. Uso: ./medir.sh > resultado.txt  (rodar com a máquina livre: cpu_probe antes)
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
PY=${PY:-python3}
TMP=${TMP_INDICE:-../../../data/cache/short-indices-sqlite}
mkdir -p "$TMP"
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
VERS=$($PY -c 'import sqlite3,sys; print(f"SQLite {sqlite3.sqlite_version} | Python {sys.version.split()[0]}")')
echo "# $(date -Iseconds) | $VERS | $CPU | $(nproc) processadores visiveis | pedidos: 1000000 linhas, 100000 clientes, consulta WHERE cliente_id = ? | 20 consultas sem indice, 1000 com indice (ms por consulta) | 10000 insercoes por lote | banco em disco, cache do SO quente | sonda abaixo de ${LIVRE:-0.12} s antes de cada rodada, pausa de ${PAUSA:-10} s | $RODADAS rodadas"
estat() {
  printf '%s\n' "$@" | sort -n | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
CHAVES="sem_indice_ms com_indice_ms criar_indice_ms inserir_sem_indice_ms inserir_com_indice_ms tamanho_antes_mb tamanho_depois_mb"
RAIZ=$(cd ../../.. && pwd)
SONDA=${SONDA:-$RAIZ/.venv/bin/python}
sonda() { (cd "$RAIZ" && "$SONDA" -c "from app.pipeline.bench import cpu_probe; print(f'{cpu_probe():.3f}')"); }
declare -A valores
for r in $(seq 1 "$RODADAS"); do
  # Pausa para a CPU esfriar e espera a sonda abaixo de LIVRE (0,12 s), por até 5 minutos.
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
  if [ "$r" = 1 ]; then saida=$($PY indice.py "$TMP" --planos); else saida=$($PY indice.py "$TMP"); fi
  linha=$(echo "$saida" | head -1)
  echo "rodada=$r cpu_probe=$p $linha"
  [ "$r" = 1 ] && echo "$saida" | tail -2 | sed 's/^/## /'
  for k in $CHAVES; do
    valores[$k]="${valores[$k]:-} $(echo "$linha" | sed -E "s/.*(^| )$k=([0-9.]+).*/\2/")"
  done
done
echo "## cpu_probe ao fim: $(sonda)"
RESUMOS=""
for k in $CHAVES; do
  # shellcheck disable=SC2086
  l="## resumo $k $(estat ${valores[$k]})"
  echo "$l"; RESUMOS+="$l"$'\n'
done
echo "## razoes derivadas por razoes.sh (a partir das medianas acima)"
./razoes.sh <(printf '%s' "$RESUMOS")
