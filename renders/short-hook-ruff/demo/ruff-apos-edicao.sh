#!/usr/bin/env bash
# Hook PostToolUse: depois de editar um .py, roda o ruff e devolve o aviso ao agente (exit 2 mostra o stderr).
f=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["tool_input"].get("file_path", ""))')
case "$f" in
  *.py)
    out=$(ruff check --isolated "$f" 2>&1) || { echo "$out" >&2; exit 2; }
    ;;
esac
exit 0
