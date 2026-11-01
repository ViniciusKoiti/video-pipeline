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
# claude -p: não interativo; as permissões vêm de .claude/settings.json (allowlist), o schedule segue em ask.
RUN="data/rotina/$(date +%F).json"  # a resposta final, os turnos e o custo equivalente em USD (ADR 032)
"$HOME/.local/bin/claude" -p "/short-diario" --model claude-sonnet-5-5 --output-format json --max-turns 80 >"$RUN" 2>>"$LOG" || {
  echo "$(date -Iseconds) a rotina saiu com erro $?" >>"$LOG"; exit 0; }
python3 - "$RUN" >>"$LOG" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("custo_usd_equivalente", d.get("total_cost_usd"), "| turnos", d.get("num_turns"),
      "| modelos", list((d.get("modelUsage") or {}).keys()), "| duracao_s", round((d.get("duration_ms") or 0) / 1000))
print(d.get("result", ""))
PY
echo "$(date -Iseconds) fim" >>"$LOG"
