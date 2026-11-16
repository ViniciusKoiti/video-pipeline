#!/usr/bin/env bash
# Rotina diária de Shorts (ADR 036): uma execução por dia, com a máquina livre, até o pacote do Postiz.
# Chamado pelo timer systemd --user (short-diario.timer) ou à mão: deploy/rotina/short-diario.sh
set -euo pipefail
REPO="${REPO:-$HOME/projetos/auto-play}"
cd "$REPO"
mkdir -p data/rotina
LOG="data/rotina/$(date +%F).log"
exec 9>"data/rotina/.lock"
if ! flock -n 9; then echo "$(date -Iseconds) já há uma execução em andamento" >>"$LOG"; exit 0; fi
PROBE=$(.venv/bin/python -c "from app.pipeline.bench import cpu_probe; print(cpu_probe())")
echo "$(date -Iseconds) cpu_probe $PROBE" >>"$LOG"
if awk -v p="$PROBE" 'BEGIN{exit !(p>0.3)}'; then
  echo "$(date -Iseconds) máquina limitada: não roda hoje" >>"$LOG"; exit 0
fi
export HF_HUB_OFFLINE=1 EARSHOT_OFFLINE=1

# Rede: no WSL o DNS pode demorar a voltar (suspensão do Windows, VPN). Espera até 10 min antes de chamar o Claude.
espera_rede() {
  local i
  for i in $(seq 1 20); do
    if getent hosts api.anthropic.com >/dev/null 2>&1; then return 0; fi
    sleep 30
  done
  return 1
}

# claude -p: não interativo; as permissões vêm de .claude/settings.json e .claude/settings.local.json (allowlist);
# o schedule segue em ask.
RUN="data/rotina/$(date +%F).json"  # a resposta final, os turnos e o custo equivalente em USD (ADR 032)
MAX_TENTATIVAS=3
for TENTATIVA in $(seq 1 "$MAX_TENTATIVAS"); do
  if ! espera_rede; then
    echo "$(date -Iseconds) sem DNS para api.anthropic.com após 10 min (tentativa $TENTATIVA/$MAX_TENTATIVAS)" >>"$LOG"
    continue
  fi
  set +e
  "$HOME/.local/bin/claude" -p "/short-diario" --model claude-sonnet-5-5 --output-format json --max-turns 80 >"$RUN" 2>>"$LOG"
  RC=$?
  set -e
  # O código de saída vai antes de qualquer $(...): uma substituição de comando zera o $? da mesma linha.
  echo "$(date -Iseconds) claude saiu com código $RC (tentativa $TENTATIVA/$MAX_TENTATIVAS)" >>"$LOG"
  # Só repete quando a API nunca respondeu: api_error e nenhum token de saída. Qualquer outra falha (permissão,
  # limite de turnos) já pode ter produzido arquivos e não se repete (a skill evita refazer, mas não arrisca).
  if python3 - "$RUN" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(1)  # saída vazia ou ilegível (processo morto, queda no meio): pode haver arquivos feitos, não repete
saiu = (d.get("usage") or {}).get("output_tokens") or 0
sys.exit(0 if d.get("terminal_reason") == "api_error" and saiu == 0 else 1)
PY
  then
    echo "$(date -Iseconds) a API não respondeu; repete em 5 min" >>"$LOG"
    sleep 300
    continue
  fi
  break
done

if [ ! -s "$RUN" ]; then
  echo "$(date -Iseconds) a rotina não rodou hoje (sem resposta do Claude)" >>"$LOG"
  exit 1
fi
python3 - "$RUN" >>"$LOG" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("custo_usd_equivalente", d.get("total_cost_usd"), "| turnos", d.get("num_turns"),
      "| modelos", list((d.get("modelUsage") or {}).keys()), "| duracao_s", round((d.get("duration_ms") or 0) / 1000))
print(d.get("result", ""))
if d.get("is_error"):
    sys.exit(1)
PY
echo "$(date -Iseconds) fim" >>"$LOG"
