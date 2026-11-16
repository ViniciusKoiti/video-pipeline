#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
DEMO="$(dirname "$(realpath "$0")")"
ROOT="$(realpath "$DEMO/../../..")"
exec > >(tee "$DEMO/resultado.txt") 2>&1
trap 'status=$?; printf "fim=%s status_execucao=%s\n" "$(date --iso-8601=seconds)" "$status"' EXIT
printf 'inicio=%s\n' "$(date --iso-8601=seconds)"
printf 'ambiente='; uname -a
lscpu
java -version
java -m jdk.compiler/com.sun.tools.javac.Main -version
"$ROOT/.venv/bin/python" --version
bash --version
sha256sum "$DEMO/Demo.java" "$DEMO/LimitadorTest.java" "$DEMO/medir.sh" "$ROOT/app/pipeline/bench.py"
printf '%s\n' \
    'cenario=servico de tras com 10 vagas simultaneas, 50 ms por requisicao, fila FIFO' \
    'normais=5 clientes, cada um 10 por segundo (50/s no total), 300 requisicoes em 6000 ms' \
    'robo=1000 requisicoes de uma vez, em 1000 ms' \
    'limite=token bucket por cliente: capacidade 100 fichas, enche 20 fichas/s, uma ficha por requisicao; sem ficha = 429 sem chamar o servico de tras' \
    'Simulacao local com Thread.sleep e threads virtuais; nao e benchmark de producao, rede, banco ou biblioteca.' \
    'Latencia em ms desde a chegada programada ate a resposta, so dos clientes normais (300 por rodada).' \
    'mediana_ms=elemento de indice n/2 (superior); p99_ms=nearest-rank ceil(n*0.99).' \
    'robo_aceitas e robo_recusadas: requisicoes do robo que passaram ou levaram 429.' \
    'fila_max: maior numero de requisicoes esperando uma vaga no servico de tras.' \
    '15 rodadas por modo, JVM nova sem aquecimento; ordem alternada por par, execucao sequencial.' \
    'cpu_probe original antes de CADA rodada; >0.3 s interrompe; sonda nao garante ausencia de ruido.' \
    'Resumo: mediana e extremos dos valores de cada rodada; nao percentis agrupados de 4500 requisicoes.'
mkdir -p "$DEMO/classes"
java -m jdk.compiler/com.sun.tools.javac.Main -d "$DEMO/classes" "$DEMO/Demo.java" "$DEMO/LimitadorTest.java"
java -cp "$DEMO/classes" LimitadorTest
: > "$DEMO/rodadas.tsv"
for rodada in $(seq 1 15); do
    modos=(sem-limite com-limite)
    if (( rodada % 2 == 0 )); then modos=(com-limite sem-limite); fi
    for modo in "${modos[@]}"; do
        probe=$(PYTHONPATH="$ROOT" "$ROOT/.venv/bin/python" -c 'from app.pipeline.bench import cpu_probe; print(cpu_probe())')
        printf 'rodada=%s modo=%s data=%s cpu_probe_s=%s\n' "$rodada" "$modo" "$(date --iso-8601=seconds)" "$probe"
        if ! awk -v p="$probe" 'BEGIN { exit !(p <= 0.3) }'; then
            printf 'INTERROMPIDO CPU limitada; rodada nao executada; resumos incompletos nao publicados.\n'
            exit 2
        fi
        linha=$(java -cp "$DEMO/classes" Demo "$modo")
        printf 'rodada=%s %s\n' "$rodada" "$linha" | tee -a "$DEMO/rodadas.tsv"
    done
done
for modo in sem-limite com-limite; do
    for metrica in normais_mediana_ms normais_p99_ms normais_max_ms normais_recusadas robo_aceitas robo_recusadas servico_atendidas fila_max total_ms; do
        mapfile -t valores < <(awk -v m="$modo" -v k="$metrica" '
            $2 == "modo=" m { for (i=3; i<=NF; i++) { split($i,a,"="); if(a[1]==k) print a[2] } }
        ' "$DEMO/rodadas.tsv" | sort -n)
        if (( ${#valores[@]} != 15 )); then printf 'ERRO numero de rodadas\n'; exit 3; fi
        printf 'RESUMO modo=%s metrica=%s n=15 mediana=%s min=%s max=%s\n' \
            "$modo" "$metrica" "${valores[7]}" "${valores[0]}" "${valores[14]}"
    done
done
printf 'medicoes=30 status=COMPLETO\n'
