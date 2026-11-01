"""A raiz do projeto, para os comandos que leem `.env` e `config/` (CLAUDE.md §3)."""

from __future__ import annotations

from pathlib import Path

from app.settings.constants.settings_constants import SettingsConstants


def project_root(start: Path) -> Path:
    """Primeira pasta, subindo a partir de `start`, que tem `config/providers.toml`."""
    for folder in (start, *start.parents):
        if (folder / SettingsConstants.CONFIG_FILE).is_file():
            return folder
    raise SystemExit(f"vp: {SettingsConstants.CONFIG_FILE} não encontrado a partir de {start}")
