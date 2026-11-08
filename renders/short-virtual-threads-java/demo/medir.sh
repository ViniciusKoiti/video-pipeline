#!/usr/bin/env bash
# Mede virtual threads em Java (Short "eu medi"): 15 rodadas, cada modo num processo (JVM) novo. Antes de cada
# rodada roda cpu_probe() (maquina limitada = medida invalida): espera a sonda abaixo de 0,12 s, pausa de 10 s entre
# rodadas. Uso: ./medir.sh > resultado.txt  (rodar com a maquina livre)
set -euo pipefail
cd "$(dirname "$0")"
RODADAS=${RODADAS:-15}
CPU=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')
JDK=$(java -version 2>&1 | head -1)
echo "# $(date -Iseconds) | $JDK | $(java -XshowSettings:properties -version 2>&1 | sed -n 's/.*java.vm.name = //p') | $CPU | $(nproc) processadores visiveis | 10000 tarefas, espera simulada de 100 ms (Thread.sleep) | plataforma: pool fixo de 200 threads | virtual: uma virtual thread por tarefa | virtual-com-pool: virtuais com Semaphore de 50 conexoes | JVM nova por modo e por rodada, flags padrao | sonda abaixo de ${LIVRE:-0.12} s antes de cada rodada, pausa de ${PAUSA:-10} s | $RODADAS rodadas"
estat() {
  printf '%s\n' "$@" | sort -n | awk '{a[NR]=$1} END{m=(NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2; printf "mediana=%s minimo=%s maximo=%s", m, a[1], a[NR]}'
}
RAIZ=$(cd ../../.. && pwd)
SONDA=${SONDA:-$RAIZ/.venv/bin/python}
sonda() { (cd "$RAIZ" && "$SONDA" -c "from app.pipeline.bench import cpu_probe; print(f'{cpu_probe():.3f}')"); }
MODOS="plataforma virtual virtual-com-pool"
declare -A valores
for r in $(seq 1 "$RODADAS"); do
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
  linha="rodada=$r cpu_probe=$p"
  for m in $MODOS; do
    saida=$(java Demo.java "$m" | head -1)
    ms=$(echo "$saida" | sed -E 's/.*total_ms=([0-9.]+).*/\1/')
    ok=$(echo "$saida" | sed -E 's/.*concluidas=([0-9]+).*/\1/')
    k=$(echo "$m" | tr - _)
    linha+=" ${k}_ms=$ms ${k}_concluidas=$ok"
    valores[$k]="${valores[$k]:-} $ms"
  done
  echo "$linha"
done
echo "## cpu_probe ao fim: $(sonda)"
RESUMOS=""
for m in $MODOS; do
  k=$(echo "$m" | tr - _)
  # shellcheck disable=SC2086
  l="## resumo ${k}_ms $(estat ${valores[$k]})"
  echo "$l"; RESUMOS+="$l"$'\n'
done
echo "## razoes derivadas por razoes.sh (a partir das medianas acima)"
R=$(mktemp); printf '%s' "$RESUMOS" > "$R"; ./razoes.sh "$R"; rm -f "$R"
