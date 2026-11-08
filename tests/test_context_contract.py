"""RF4: `Context`, `LazyContext` e `FakeContext` declaram as mesmas capacidades, e tudo o que o CLI e os
scripts usam do contexto está declarado na porta."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.bootstrap import LazyContext
from app.bootstrap.registry import ConfigurationError
from app.pipeline.ports import Context
from tests.fakes import FakeBatchTTS, FakeContext, FakeTTS, InMemoryStore, make_settings

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = sorted(name for name in vars(Context) if not name.startswith("_"))  # declarados na porta


def has_member(owner: type, name: str) -> bool:
    return hasattr(owner, name) or name in getattr(owner, "__dataclass_fields__", {})


@pytest.mark.parametrize("owner", [LazyContext, FakeContext], ids=["lazy", "fake"])
def test_both_implementations_have_every_declared_capability(owner: type) -> None:
    assert [name for name in MEMBERS if not has_member(owner, name)] == []


def used_attributes() -> dict[str, set[str]]:
    """`context.<capacidade>` e `ctx.<capacidade>` no app e nos scripts, com os arquivos que usam."""
    found: dict[str, set[str]] = {}
    for path in [*(ROOT / "app").rglob("*.py"), *(ROOT / "scripts").rglob("*.py")]:
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in {"context", "ctx"}
            ):
                found.setdefault(node.attr, set()).add(str(path.relative_to(ROOT)))
    return found


def test_everything_the_cli_and_scripts_use_from_the_context_is_declared() -> None:
    undeclared = {name: sorted(files) for name, files in used_attributes().items() if name not in MEMBERS}
    assert undeclared == {}


def test_the_final_voice_falls_back_to_the_draft_voice_and_named_voices_are_checked(tmp_path: Path) -> None:
    context = FakeContext(settings=make_settings(tmp_path), store=InMemoryStore(tmp_path))
    assert context.tts_final is context.tts  # sem voz final configurada, a dos rascunhos
    final = FakeBatchTTS()
    context.final_tts, context.voices = final, {"gemini": FakeTTS()}
    assert context.tts_final is final and context.tts_named("gemini") is context.voices["gemini"]
    with pytest.raises(ConfigurationError, match="não existe"):
        context.tts_named("inexistente")
    with pytest.raises(ConfigurationError, match="não existe"):  # o mesmo erro no contexto real
        LazyContext(make_settings(tmp_path)).tts_named("inexistente")
