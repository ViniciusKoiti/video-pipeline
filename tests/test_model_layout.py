"""Convenção da ADR 037: objetos de dados por área, uma classe por arquivo."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"


def symbol(node: ast.expr) -> str:
    if isinstance(node, ast.Call):
        return symbol(node.func)
    if isinstance(node, ast.Subscript):
        return symbol(node.value)
    if isinstance(node, ast.Attribute):
        return node.attr
    return node.id if isinstance(node, ast.Name) else ""


def layout_problems(sources: dict[str, str]) -> list[str]:
    trees = {path: ast.parse(source) for path, source in sources.items()}
    model_names = {"BaseModel", "Enum", "IntEnum", "StrEnum", "TypedDict"}
    decorators = {"dataclass"}
    # Inclui bases privadas e nomes importados com alias, inclusive via módulos de compatibilidade.
    changed = True
    while changed:
        before = model_names.copy(), decorators.copy()
        for tree in trees.values():
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name in model_names:
                            model_names.add(alias.asname or alias.name)
                        if alias.name in decorators:
                            decorators.add(alias.asname or alias.name)
                elif isinstance(node, ast.ClassDef) and (
                    any(symbol(base) in model_names for base in node.bases)
                    or any(symbol(dec) in decorators for dec in node.decorator_list)
                ):
                    model_names.add(node.name)
        changed = before != (model_names, decorators)
    problems = []
    for path, tree in trees.items():
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if "models" in Path(path).parts:
            if Path(path).parts[0] == "models" and classes:
                problems.append(f"{path}: app/models/ só mantém reexports; use models/ da área")
            if len(classes) > 1:
                problems.append(f"{path}: use uma classe por arquivo")
            for cls in classes:
                if cls.name not in model_names:
                    problems.append(f"{path}: {cls.name} não é modelo de dados")
        else:
            for cls in classes:
                if cls.name in model_names:
                    problems.append(f"{path}: mova {cls.name} para models/ da área")
    return problems


def test_all_data_models_follow_the_layout() -> None:
    sources = {p.relative_to(APP).as_posix(): p.read_text() for p in APP.rglob("*.py")}
    assert layout_problems(sources) == []


@pytest.mark.parametrize("definition", [
    "class Claim(BaseModel): pass", "class Status(StrEnum): pass",
    "class Registry(TypedDict): pass", "@dataclass(frozen=True)\nclass Result: pass",
    "from pydantic import BaseModel as Schema\nclass Claim(Schema): pass",
])
def test_checker_rejects_data_models_outside_models(definition: str) -> None:
    assert layout_problems({"pipeline/task.py": definition})


def test_checker_follows_inheritance_across_files() -> None:
    assert layout_problems({
        "pipeline/models/base.py": "class Model(BaseModel): pass",
        "pipeline/task.py": "from .models.base import Model as Parent\nclass Claim(Parent): pass",
    }) == ["pipeline/task.py: mova Claim para models/ da área"]


def test_checker_rejects_multiple_classes_and_services_in_models() -> None:
    assert layout_problems({"media/models/timing.py": "class A(BaseModel): pass\nclass B(A): pass"})
    assert layout_problems({"media/models/worker.py": "class Worker: pass"})
    assert layout_problems({"models/claim.py": "class Claim(BaseModel): pass"})


def test_checker_allows_models_helpers_ports_services_and_errors() -> None:
    assert layout_problems({
        "pipeline/models/claim.py": "class Claim(BaseModel): pass",
        "pipeline/models/types.py": "Id = str",
        "pipeline/ports.py": "class Store(Protocol): pass",
        "providers/client.py": "class Client: pass\nclass Failure(RuntimeError): pass",
    }) == []


@pytest.mark.parametrize(("module", "name", "canonical"), [
    ("app.bootstrap_registry", "Registry", "app.bootstrap.models.registry"),
    ("app.settings", "Settings", "app.settings.models.settings"),
    ("app.pipeline.bench_data", "BenchScript", "app.pipeline.models.bench_script"),
])
def test_compatibility_imports_work_in_a_fresh_process(module: str, name: str, canonical: str) -> None:
    # O cache de imports da suíte esconderia ciclos introduzidos pela conversão para pacotes.
    code = (
        "from importlib import import_module\n"
        f"old = getattr(import_module({module!r}), {name!r})\n"
        f"assert old is getattr(import_module({canonical!r}), {name!r})\n"
    )
    subprocess.run([sys.executable, "-c", code], cwd=APP.parent, check=True, capture_output=True, text=True)
