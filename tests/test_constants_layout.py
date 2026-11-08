"""ADR 038: localização, Final e imutabilidade dos grupos de constantes de app/."""

from __future__ import annotations

import ast
import importlib
import re
import subprocess
import sys
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType

import pytest

APP = Path(__file__).resolve().parents[1] / "app"
# Registros mutáveis de composição; não são valores constantes nem exceções de migração.
RUNTIME_REGISTRIES = {("cli.py", "HANDLERS"), ("bootstrap/__init__.py", "DEFAULT_REGISTRY")}


def symbol(node: ast.expr) -> str:
    if isinstance(node, (ast.Call, ast.Subscript)):
        return symbol(node.func if isinstance(node, ast.Call) else node.value)
    if isinstance(node, ast.Attribute):
        return node.attr
    return node.id if isinstance(node, ast.Name) else ""


def constants_problems(sources: dict[str, str]) -> list[str]:
    problems = []
    for path, source in sources.items():
        tree = ast.parse(source)
        aliases = {
            a.asname or a.name: a.name
            for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom) and n.module in {"typing", "typing_extensions"}
            for a in n.names
        }
        in_constants = "constants" in Path(path).parts
        if in_constants and Path(path).parts[0] == "constants":
            problems.append(f"{path}: use constants/ da área, sem catálogo global")
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if in_constants and path.endswith("__init__.py"):
            if classes:
                problems.append(f"{path}: importe pelo módulo específico; __init__ fica mínimo")
        elif in_constants and (len(classes) != 1 or not classes[0].name.endswith("Constants")):
            problems.append(f"{path}: use uma classe *Constants por arquivo")
        pending = list(tree.body)
        while pending:
            node = pending.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                pending.extend(n for n in ast.iter_child_nodes(node) if isinstance(n, ast.stmt))
                continue
            annotation = node.annotation if isinstance(node, ast.AnnAssign) else None
            value = node.value
            if value is None:
                continue
            kind = aliases.get(symbol(value), symbol(value))
            if kind in {"TypeVar", "ParamSpec", "NewType"}:
                continue
            if annotation and aliases.get(symbol(annotation), symbol(annotation)) == "TypeAlias":
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)]
            final = annotation and aliases.get(symbol(annotation), symbol(annotation)) == "Final"
            literal = isinstance(value, (ast.Constant, ast.Tuple, ast.List, ast.Set, ast.Dict)) or (
                isinstance(value, ast.Call)
                and kind in {"compile", "Path", "frozenset", "tuple", "MappingProxyType"}
            )
            for name in names:
                if name == "__all__" or (path, name) in RUNTIME_REGISTRIES:
                    continue
                if name.lstrip("_").isupper() or final or literal:
                    problems.append(f"{path}:{node.lineno}: mova {name} para uma classe em constants/")
        for cls in classes:
            if in_constants:
                for node in cls.body:
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                        continue
                    if (
                        not isinstance(node, ast.AnnAssign)
                        or aliases.get(symbol(node.annotation), symbol(node.annotation)) != "Final"
                    ):
                        problems.append(f"{path}:{node.lineno}: constantes exigem atributo Final com valor")
                    elif node.value is None:
                        problems.append(f"{path}:{node.lineno}: constante sem valor")
            elif "models" not in Path(path).parts:
                for node in cls.body:
                    if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                        continue
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    names = [t.id for t in targets if isinstance(t, ast.Name)]
                    final = isinstance(node, ast.AnnAssign) and aliases.get(
                        symbol(node.annotation), symbol(node.annotation)
                    ) == "Final"
                    literal = isinstance(node.value, (ast.Constant, ast.Tuple, ast.List, ast.Set, ast.Dict))
                    if (any(n.lstrip("_").isupper() for n in names) or final or literal) and not isinstance(
                        node.value, ast.Attribute
                    ):
                        problems.append(f"{path}:{node.lineno}: valor fixo da classe deve vir de constants/")
    return problems


def assert_immutable(value: object) -> None:
    if isinstance(value, MappingProxyType):
        for key, item in value.items():
            assert_immutable(key)
            assert_immutable(item)
    elif isinstance(value, (tuple, frozenset)):
        for item in value:
            assert_immutable(item)
    elif is_dataclass(value) and not isinstance(value, type):
        assert value.__dataclass_params__.frozen
        for field in fields(value):
            item = getattr(value, field.name)
            if not callable(item):
                assert_immutable(item)
    else:
        assert value is None or isinstance(value, (str, bytes, int, float, Enum, Path, re.Pattern)), type(
            value
        )


def test_constants_follow_the_convention_throughout_app() -> None:
    assert constants_problems({p.relative_to(APP).as_posix(): p.read_text() for p in APP.rglob("*.py")}) == []


def test_constant_collections_are_deeply_immutable() -> None:
    for path in APP.rglob("constants/*.py"):
        if path.name == "__init__.py":
            continue
        module = importlib.import_module(".".join(path.relative_to(APP.parent).with_suffix("").parts))
        classes = [n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef)]
        for cls in classes:
            namespace = getattr(module, cls.name)
            for name in namespace.__annotations__:
                assert_immutable(getattr(namespace, name))


@pytest.mark.parametrize(
    "definition",
    [
        "TIMEOUT = 30",
        "_TIMEOUT = 30",
        "timeout = 30",
        "URL: Final[str] = 'https://example.com'",
        "if True:\n    TIMEOUT = 30",
        "class Worker:\n    TIMEOUT = 30",
        "class Worker:\n    timeout: Final[int] = 30",
        "class Worker:\n    timeout = 30",
        "pattern = re.compile('word')",
    ],
)
def test_checker_rejects_constants_outside_their_namespace(definition: str) -> None:
    assert constants_problems({"providers/client.py": definition})


@pytest.mark.parametrize("body", ["VALUE = 1", "VALUE: int = 1", "VALUE: Final[int]", "def run(): pass"])
def test_checker_requires_final_values_and_no_methods(body: str) -> None:
    assert constants_problems({"media/constants/audio_constants.py": f"class AudioConstants:\n    {body}"})


def test_checker_handles_final_aliases_and_distinguishes_types_fields_and_local_values() -> None:
    assert (
        constants_problems(
            {
                "media/constants/audio_constants.py": (
                    "from typing import Final as F\nclass AudioConstants:\n    VALUE: F[int] = 1"
                ),
                "pipeline/types.py": "T = TypeVar('T')\nId = Annotated[str, Field()]\nWindow = Literal['d7']",
                "pipeline/models/result.py": "class Result(BaseModel):\n    name: str = 'ok'",
                "media/work.py": "def run():\n    timeout = 30",
                "cli.py": "HANDLERS = {}",
                "bootstrap/__init__.py": "DEFAULT_REGISTRY = {}",
            }
        )
        == []
    )
    assert constants_problems({"pipeline/work.py": "HANDLERS = {}"})
    assert constants_problems({"constants/global.py": "class GlobalConstants:\n    VALUE: Final[int] = 1"})
    assert constants_problems({"media/constants/pair.py": "class AConstants: pass\nclass BConstants: pass"})


@pytest.mark.parametrize("value", [[1], {"x": 1}, {1}, (MappingProxyType({"x": []}),)])
def test_immutability_checker_rejects_mutable_values_even_when_nested(value: object) -> None:
    with pytest.raises(AssertionError):
        assert_immutable(value)


def test_modal_client_still_loads_constants_when_executed_outside_the_package(tmp_path: Path) -> None:
    script = APP / "providers/tts/chatterbox_modal_client.py"
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    # Sem argumentos, para antes de importar Modal ou acessar a rede; o import local já ocorreu.
    assert result.returncode != 0 and "IndexError: list index out of range" in result.stderr
