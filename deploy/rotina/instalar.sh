#!/usr/bin/env bash
# Copia as unidades para o systemd do usuário e liga o timer. Decisão do dono (ADR 036): rodar só quando ele quiser.
set -euo pipefail
mkdir -p "$HOME/.config/systemd/user"
cp "$(dirname "$0")"/short-diario.{service,timer} "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now short-diario.timer
systemctl --user list-timers short-diario.timer
echo "Para desligar: systemctl --user disable --now short-diario.timer"
