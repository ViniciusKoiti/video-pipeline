"""O hook de pré-commit recusa arquivo grande demais no índice (o GitHub rejeita o push acima de 100 MB)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_tamanho.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=repo, capture_output=True, text=True)


def test_small_files_pass_and_big_staged_file_is_refused(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    (tmp_path / "pequeno.txt").write_text("ok")
    (tmp_path / "grande.bin").write_bytes(b"x" * 3 * 1024 * 1024)
    git(tmp_path, "add", "pequeno.txt")
    assert run(tmp_path, "--limite-mb=1").returncode == 0
    git(tmp_path, "add", "grande.bin")
    result = run(tmp_path, "--limite-mb=1")
    assert result.returncode == 1
    assert "grande.bin tem 3 MB" in result.stderr
    assert "pequeno.txt" not in result.stderr


def test_file_under_the_limit_is_accepted(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    (tmp_path / "medio.bin").write_bytes(b"x" * 1024 * 1024)
    git(tmp_path, "add", "medio.bin")
    assert run(tmp_path, "--limite-mb=2").returncode == 0
