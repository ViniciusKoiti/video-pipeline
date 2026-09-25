#!/usr/bin/env bash
# Verifica o ambiente do video-pipeline (etapa 1, CLAUDE.md §3). Só acessa 127.0.0.1.
# Uso: scripts/check_env.sh   → sai com 1 se algum item obrigatório falhar.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIN_MEM_GB="${MIN_MEM_GB:-11}"     # .wslconfig memory=12GB aparece como ~11,7 GB
MIN_CPUS="${MIN_CPUS:-8}"
MIN_DISK_GB="${MIN_DISK_GB:-20}"
FAIL=0

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=1; }

# Lê uma variável do .env sem executar o arquivo.
env_get() { [[ -f "$ROOT/.env" ]] && grep -E "^$1=" "$ROOT/.env" | tail -1 | cut -d= -f2- | tr -d '"'"'" ; }

echo "Local e recursos"
[[ "$ROOT" == /mnt/* ]] && bad "projeto em $ROOT; mover para o filesystem Linux" || ok "projeto em $ROOT"
mem_gb=$(awk '/MemTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo)
awk "BEGIN{exit !($mem_gb >= $MIN_MEM_GB)}" && ok "memória do WSL: ${mem_gb} GB" \
  || bad "memória do WSL: ${mem_gb} GB (< ${MIN_MEM_GB}); ajuste o .wslconfig e rode 'wsl --shutdown'"
cpus=$(nproc)
(( cpus >= MIN_CPUS )) && ok "CPUs: $cpus" || warn "CPUs: $cpus (< $MIN_CPUS); LLM e TTS ficam mais lentos"
disk_gb=$(df -BG --output=avail "$ROOT" | tail -1 | tr -dc '0-9')
(( disk_gb >= MIN_DISK_GB )) && ok "disco livre: ${disk_gb} GB" || bad "disco livre: ${disk_gb} GB (< ${MIN_DISK_GB})"

echo "Ferramentas"
for cmd in git ffmpeg ffprobe espeak-ng ollama; do
  command -v "$cmd" >/dev/null && ok "$cmd" || bad "$cmd não encontrado"
done

echo "Python (.venv)"
PY="$ROOT/.venv/bin/python"
if [[ -x "$PY" ]]; then
  pyver=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  [[ "$pyver" == 3.11 || "$pyver" == 3.12 ]] && ok "Python $pyver" || bad "Python $pyver (Kokoro exige 3.10–3.12)"
  "$PY" -c 'import kokoro, torch' 2>/dev/null \
    && ok "kokoro + torch importam" || bad "kokoro/torch não importam no .venv"
  "$PY" -c 'import en_core_web_sm' 2>/dev/null \
    && ok "modelo spaCy en_core_web_sm instalado" || bad "en_core_web_sm ausente (o misaki baixaria em tempo de execução)"
else
  bad ".venv ausente; criar com: uv venv --python 3.12 .venv"
fi
[[ -d "${HF_HOME:-$HOME/.cache/huggingface}/hub/models--hexgrad--Kokoro-82M" ]] \
  && ok "pesos do Kokoro-82M em cache" || warn "pesos do Kokoro-82M ainda não baixados"

echo "Ollama"
base="$(env_get OLLAMA_BASE_URL)"; base="${base:-http://127.0.0.1:11434}"
model="$(env_get OLLAMA_MODEL)"
if tags=$(curl -sf --max-time 3 "$base/api/tags"); then
  ok "API em $base ($(curl -sf "$base/api/version" | tr -dc '0-9.'))"
  if [[ -n "$model" ]]; then
    grep -q "\"name\":\"$model\"" <<<"$tags" && ok "modelo $model disponível" || bad "modelo $model não baixado (ollama pull $model)"
  else
    warn "OLLAMA_MODEL vazio no .env"
  fi
else
  bad "Ollama não responde em $base (systemctl --user start ollama)"
fi

echo "Custo zero (§2.1)"
if [[ -f "$ROOT/.env" ]]; then
  [[ "$(env_get MAX_API_SPEND_USD)" == 0 ]] && ok "MAX_API_SPEND_USD=0" || bad "MAX_API_SPEND_USD precisa ser 0"
  [[ "$(env_get ALLOW_PAID_API)" == false ]] && ok "ALLOW_PAID_API=false" || bad "ALLOW_PAID_API precisa ser false"
else
  bad ".env ausente; copiar de .env.example"
fi

echo
(( FAIL == 0 )) && echo "Ambiente OK." || echo "Há itens obrigatórios pendentes."
exit "$FAIL"
