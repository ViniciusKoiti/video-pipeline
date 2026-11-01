"""O gate agrega lint, tipagem e testes; a tipagem verifica compatibilidade de uma porta real."""

from __future__ import annotations

import os
import subprocess
import sys
from itertools import product
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_qualidade.sh"


@pytest.mark.parametrize(("lint_code", "typing_code", "test_code"), list(product((0, 1), repeat=3)))
def test_quality_gate_runs_all_checks_and_preserves_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, lint_code: int, typing_code: int, test_code: int
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        '#!/bin/sh\nprintf "%s|%s\\n" "$PWD" "$*" >> "$QUALITY_TEST_LOG"\n'
        'case "$3" in\n'
        '  ruff) exit "$QUALITY_TEST_LINT_RC" ;;\n'
        '  mypy) exit "$QUALITY_TEST_TYPING_RC" ;;\n'
        '  pytest) exit "$QUALITY_TEST_TEST_RC" ;;\n'
        '  *) exit 99 ;;\n'
        'esac\n'
    )
    uv.chmod(0o755)
    log = tmp_path / "calls.txt"
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("QUALITY_TEST_LOG", str(log))
    monkeypatch.setenv("QUALITY_TEST_LINT_RC", str(lint_code))
    monkeypatch.setenv("QUALITY_TEST_TYPING_RC", str(typing_code))
    monkeypatch.setenv("QUALITY_TEST_TEST_RC", str(test_code))

    result = subprocess.run(["bash", str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == int(bool(lint_code or typing_code or test_code))
    assert log.read_text().splitlines() == [
        f"{ROOT}|run --no-sync ruff check .",
        f"{ROOT}|run --no-sync mypy",
        f"{ROOT}|run --no-sync pytest -q",
    ]
    verdict = "reprovada" if lint_code or typing_code or test_code else "aprovada"
    assert f"Qualidade: {verdict}." in result.stdout


@pytest.mark.parametrize("compatible", [True, False])
def test_mypy_checks_adapter_against_the_real_tts_protocol(tmp_path: Path, compatible: bool) -> None:
    result_type = "SpeechResult" if compatible else "str"
    result_value = 'SpeechResult(request.out_path, "test", "test")' if compatible else '"invalid"'
    source = tmp_path / "adapter.py"
    source.write_text(
        "from app.bootstrap import DEFAULT_REGISTRY\n"
        "from app.bootstrap_registry import Registration, Registry\n"
        "from app.providers.base import ProviderInfo\n"
        "from app.providers.tts.base import SpeechRequest, SpeechResult, TTSProvider\n"
        "class Adapter:\n"
        "    def __init__(self) -> None:\n"
        '        self.info = ProviderInfo("test", remote=False)\n'
        '        self.identity = "test"\n'
        "    def fingerprint(self, request: SpeechRequest) -> str:\n"
        '        return "test"\n'
        f"    def synthesize_speech(self, request: SpeechRequest) -> {result_type}:\n"
        f"        return {result_value}\n"
        "def use(provider: TTSProvider) -> None:\n"
        "    pass\n"
        "use(Adapter())\n"
        'registry: Registry = {**DEFAULT_REGISTRY, "tts": {"test": Registration(0, lambda _: Adapter())}}\n'
    )
    result = subprocess.run(
        [
            sys.executable, "-m", "mypy", "--config-file", str(ROOT / "pyproject.toml"),
            "--follow-imports=silent", "--cache-dir", str(tmp_path / "cache"), str(source),
        ],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == (0 if compatible else 1), result.stdout + result.stderr
    if not compatible:
        assert 'incompatible type "Adapter"; expected "TTSProvider"' in result.stdout
        assert "[arg-type]" in result.stdout
