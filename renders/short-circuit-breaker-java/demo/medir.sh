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
printf 'Compilador via modulo jdk.compiler: javac ausente no PATH na tentativa inicial (nenhuma rodada executada).\n'
java -m jdk.compiler/com.sun.tools.javac.Main -version
"$ROOT/.venv/bin/python" --version
bash --version
sha256sum "$DEMO/Demo.java" "$DEMO/BreakerTest.java" "$DEMO/medir.sh" "$ROOT/app/pipeline/bench.py"
printf '%s\n' \
    'cenario=300 requisicoes; 50/s (intervalo 20 ms, ultima chegada 5980 ms); 20 threads' \
    'falha=[0,3000) ms determinada na entrada da dependencia; timeout=1000 ms; normal=50 ms' \
    'breaker=5 falhas consecutivas na ordem de conclusao; aberto=2000 ms; uma sonda meio-aberto' \
    'Cenario existente preservado; pauta menciona 2 s como proposta, demo existente usa 3 s.' \
    'Simulacao local com Thread.sleep e fila ilimitada; nao e benchmark de producao, rede, banco ou biblioteca.' \
    'Latencia em ms desde chegada programada: inclui fila, atraso do produtor, erros e recusas.' \
    'mediana_ms=elemento de indice n/2 (superior); p99_ms=nearest-rank ceil(n*0.99).' \
    'Recusas sao erros rapidos, nao pagamentos bem-sucedidos; erros inclui recusas.' \
    'recusadas_pos_falha: chegada programada >=3000 ms, mesmo com dependencia saudavel.' \
    'volta_ms: chegada da primeira requisicao pos-falha com sucesso e latencia <=200 ms, menos 3000.' \
    'volta_resposta_ms: conclusao dessa mesma requisicao menos 3000; nao prova recuperacao sustentada.' \
    'volta=-1 indica recuperacao nao observada; agregacao a preserva, sem imputacao.' \
    '15 rodadas por modo, JVM nova sem aquecimento; ordem alternada por par, execucao sequencial.' \
    'cpu_probe original antes de CADA rodada; >0.3 s interrompe; sonda nao garante ausencia de ruido.' \
    'Resumo: mediana e extremos dos valores de cada rodada; nao percentis agrupados de 4500 requisicoes.'
mkdir -p "$DEMO/classes"
java -m jdk.compiler/com.sun.tools.javac.Main -d "$DEMO/classes" "$DEMO/Demo.java" "$DEMO/BreakerTest.java"
java -cp "$DEMO/classes" BreakerTest
: > "$DEMO/rodadas.tsv"
for rodada in $(seq 1 15); do
    modos=(sem-breaker com-breaker)
    if (( rodada % 2 == 0 )); then modos=(com-breaker sem-breaker); fi
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
for modo in sem-breaker com-breaker; do
    for metrica in mediana_ms p99_ms chamadas_na_falha erros recusadas recusadas_pos_falha volta_ms volta_resposta_ms total_ms; do
        mapfile -t valores < <(awk -v m="$modo" -v k="$metrica" '
            $2 == "modo=" m { for (i=3; i<=NF; i++) { split($i,a,"="); if(a[1]==k) print a[2] } }
        ' "$DEMO/rodadas.tsv" | sort -n)
        if (( ${#valores[@]} != 15 )); then printf 'ERRO numero de rodadas\n'; exit 3; fi
        printf 'RESUMO modo=%s metrica=%s n=15 mediana=%s min=%s max=%s\n' \
            "$modo" "$metrica" "${valores[7]}" "${valores[0]}" "${valores[14]}"
    done
done
printf 'medicoes=30 status=COMPLETO\n'
