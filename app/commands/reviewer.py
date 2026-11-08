"""Quem assina uma decisão humana (gates, reabertura): `--reviewer`, senão `VP_REVIEWER`, senão o git."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.settings import read_dotenv


def default_reviewer(root: Path) -> str:
    """`VP_REVIEWER` do ambiente ou do `.env`; senão o nome do git, com aviso: ele assina a decisão."""
    name = (os.environ.get("VP_REVIEWER") or read_dotenv(root / ".env").get("VP_REVIEWER", "")).strip()
    if name:
        return name
    name = _git_user()
    print(
        f"vp: decisão assinada como '{name}' (git config user.name); "
        "use --reviewer ou VP_REVIEWER para assinar com o seu nome",
        file=sys.stderr,
    )
    return name


def _git_user() -> str:
    result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=False)
    if not result.stdout.strip():
        raise SystemExit("vp: informe --reviewer (git config user.name está vazio)")
    return result.stdout.strip()
