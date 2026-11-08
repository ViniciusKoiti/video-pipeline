#!/usr/bin/env bash
# Espera o render de outra sessao (um render por vez) terminar e roda medir.sh. Teto de 90 min de espera.
cd "$(dirname "$0")"
limite=$(( $(date +%s) + 5400 ))
while kill -0 100937 2>/dev/null; do
  [ "$(date +%s)" -ge "$limite" ] && { echo "render ainda em curso apos 90 min; medicao nao iniciada" > medir-espera.txt; exit 4; }
  sleep 30
done
echo "render terminou em $(date -Iseconds); iniciando medir.sh" > medir-espera.txt
./medir.sh > resultado.txt 2> medir.err
echo "medir.sh saiu com $? em $(date -Iseconds)" >> medir-espera.txt
