"""`vp evolucao` (era scripts/provisorio/evolucao.py): guardar, a sonda de CPU e o commit do template."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import build_parser
from app.commands import evolucao
from app.media import evolution
from app.storage.json_files import JsonFileStore
from tests.fakes import make_root
from tests.test_evolution import episode, video

KIT = '{"dependencies": {"@viniciusk/motion-kit": "file:vendor/viniciusk-motion-kit-0.4.0.tgz"}}'


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, SimpleNamespace]:
    """Projeto com config, `video/package.json` num repositório git e o episódio com `episode.json`."""
    # Dentro do hook de pré-commit, as GIT_* (GIT_DIR, GIT_INDEX_FILE) apontam para o repositório real: sem
    # limpar, o `git init` daqui grava core.bare nele e o `git add` troca o índice (aconteceu em 2026-11-20).
    for name in [key for key in os.environ if key.startswith("GIT_")]:
        monkeypatch.delenv(name)
    root = make_root(tmp_path)
    (root / "video").mkdir()
    (root / "video" / "package.json").write_text(KIT)
    git(root, "init", "-q")
    git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
    folder = root / "data" / "episodes" / "regua"
    (folder / "renders").mkdir(parents=True)
    (folder / "episode.json").write_text(episode().model_dump_json())
    (root / "data" / "benchmarks").mkdir()  # no repositório, a pasta do registro já existe
    monkeypatch.chdir(root)
    return root, SimpleNamespace(store=JsonFileStore(root / "data" / "episodes"))


def args(*argv: str) -> argparse.Namespace:
    return build_parser().parse_args(["evolucao", *argv])


def test_guardar_keeps_the_preview_as_a_version_and_appends_the_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, context = project(tmp_path, monkeypatch)
    video(root / "data" / "episodes" / "regua" / "renders" / "preview.mp4", "red")
    keep = args("guardar", "regua", "--nota", "primeira")
    code = evolucao.run(keep, context, template_hash=lambda _: "f" * 64)
    assert code == 0
    assert (root / "data" / "episodes" / "regua" / "renders" / "evolucao" / "v1.mp4").is_file()
    registry = (root / "data" / "benchmarks" / "evolucao-template.md").read_text()
    assert "primeira" in registry and "0.4.0" in registry
    assert capsys.readouterr().out.startswith("v1: 3 planos, commit ")


def test_gerar_refuses_with_a_slow_cpu_before_rendering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, context = project(tmp_path, monkeypatch)
    monkeypatch.setattr(evolucao, "cpu_probe", lambda: 1.0)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("não devia renderizar"))
    with pytest.raises(evolution.EvolutionError, match="CPU limitada"):
        evolucao.run(args("gerar", "regua", "--nota", "x"), context, template_hash=lambda _: "f" * 64)


def test_template_info_marks_local_changes_in_video(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _ = project(tmp_path, monkeypatch)
    commit, template, kit = evolucao.template_info(root, None, lambda project: f"hash de {project.name}")
    assert template == "hash de video" and kit == "0.4.0" and "alterações" not in commit
    (root / "video" / "package.json").write_text(KIT + "\n")
    assert evolucao.template_info(root, None, lambda _: "h")[0].endswith(" + alterações locais em video/")


def test_parser_has_the_four_verbs_of_the_old_script() -> None:
    assert args("comparar", "regua", "--versoes", "v1,v3").versoes == "v1,v3"
    assert args("lado-a-lado", "regua", "v1", "v2").depois == "v2"
    assert args("guardar", "regua", "--nota", "n", "--commit", "abc", "--tempo-s", "12.5").tempo_s == 12.5
