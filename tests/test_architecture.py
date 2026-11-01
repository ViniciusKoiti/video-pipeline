"""Regras de dependência da ADR 006, verificadas no código-fonte (sem importar nada)."""

from __future__ import annotations

import ast
import re
from importlib.util import resolve_name
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"

FUNCTIONS = sorted(
    p.name
    for p in (APP / "providers").iterdir()
    if p.is_dir() and p.name not in {"__pycache__", "models", "constants"}
)
# app.providers.<função>.<adapter> ou app.render.<motor>, exceto os módulos base (e o que vem deles).
CONCRETE_ADAPTER = re.compile(
    f"^app\\.(providers\\.({'|'.join(FUNCTIONS)})|render|storage)\\.(?!base(\\.|$))[a-z_]"
)
COMPOSITION = ("app.bootstrap", "app.cli")
HEAVY = {"kokoro", "torch", "soundfile", "misaki", "spacy"}


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(APP.parent).with_suffix("").parts).removesuffix(".__init__")


def imported_modules(source: str, *, package: str = "") -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            name = node.module or ""
            if node.level:
                name = resolve_name("." * node.level + name, package)
            found.add(name)
            # `from pacote import submódulo`: módulos são minúsculos; classes (CapWords) não entram.
            found |= {f"{name}.{a.name}" for a in node.names if a.name[:1].islower()}
    return found


def in_package(module: str, roots: tuple[str, ...]) -> bool:
    return any(module == root or module.startswith(root + ".") for root in roots)


def violations(module: str, imports: set[str]) -> list[str]:
    problems = []
    for name in sorted(imports):
        concrete = CONCRETE_ADAPTER.match(name) and not {"models", "constants"} & set(name.split("."))
        if in_package(module, ("app.pipeline",)):
            if concrete or in_package(name, COMPOSITION) or name.split(".")[0] in HEAVY:
                problems.append(f"{module} importa {name}: o pipeline só conhece portas")
        elif in_package(module, ("app.providers", "app.render")):
            if in_package(name, ("app.pipeline",)) and not in_package(
                name, ("app.pipeline.schemas", "app.pipeline.models", "app.pipeline.constants")
            ):
                problems.append(f"{module} importa {name}: adapters só usam models ou schemas")
            if in_package(name, (*COMPOSITION, "app.settings")):
                problems.append(f"{module} importa {name}: adapters recebem parâmetros explícitos")
        elif not in_package(module, COMPOSITION) and concrete:
            problems.append(f"{module} importa {name}: só app.bootstrap conhece adapters concretos")
        if (
            in_package(module, ("app.media",))
            and in_package(name, ("app.pipeline",))
            and not in_package(
                name, ("app.pipeline.schemas", "app.pipeline.models", "app.pipeline.constants")
            )
        ):
            problems.append(f"{module} importa {name}: mídia só usa models ou schemas")
    return problems


def test_dependency_rules_hold_for_the_whole_app() -> None:
    problems = []
    for path in sorted(APP.rglob("*.py")):
        module = module_name(path)
        package = module if path.name == "__init__.py" else module.rpartition(".")[0]
        problems += violations(module, imported_modules(path.read_text(), package=package))
    assert problems == []


def test_checker_catches_pipeline_importing_a_concrete_adapter() -> None:
    source = (
        "from app.providers.tts import kokoro\n"
        "from app.render.ffmpeg import FfmpegEngine\n"
        "import torch\n"
    )
    assert violations("app.pipeline.voice", imported_modules(source)) == [
        "app.pipeline.voice importa app.providers.tts.kokoro: o pipeline só conhece portas",
        "app.pipeline.voice importa app.render.ffmpeg: o pipeline só conhece portas",
        "app.pipeline.voice importa torch: o pipeline só conhece portas",
    ]


def test_checker_allows_ports_and_schemas() -> None:
    source = (
        "from app.providers.tts.base import TTSProvider\nfrom app.providers.errors import QuotaExhausted\n"
        "from app.render.base import RenderEngine\nfrom app.pipeline.schemas import Scene\n"
    )
    assert violations("app.pipeline.voice", imported_modules(source)) == []
    assert violations("app.providers.tts.kokoro", imported_modules(source)) == []


@pytest.mark.parametrize("module", ["app.pipeline.voice", "app.media.host", "app.providers.tts.kokoro"])
def test_checker_allows_models_and_constants_from_other_areas(module: str) -> None:
    assert violations(module, {
        "app.pipeline.models.scene", "app.providers.tts.models.speech",
        "app.render.models.target_spec",
        "app.pipeline.constants.schemas_constants", "app.providers.tts.constants.kokoro_constants",
        "app.render.constants.ffmpeg_constants",
    }) == []


def test_checker_catches_adapter_reaching_into_orchestration() -> None:
    source = "from app.pipeline.ports import Context\nfrom app.settings import Settings\n"
    assert violations("app.providers.text.ollama", imported_modules(source)) == [
        "app.providers.text.ollama importa app.pipeline.ports: adapters só usam models ou schemas",
        "app.providers.text.ollama importa app.settings: adapters recebem parâmetros explícitos",
    ]


def test_checker_keeps_concrete_adapters_inside_the_composition_root() -> None:
    source = "from app.providers.text.ollama import OllamaText\n"
    assert violations("app.bootstrap", imported_modules(source)) == []
    assert violations("app.media.probe", imported_modules(source)) == [
        "app.media.probe importa app.providers.text.ollama: só app.bootstrap conhece adapters concretos"
    ]


@pytest.mark.parametrize("module", ["app.bootstrap", "app.bootstrap.factories", "app.bootstrap.tts.factory"])
def test_composition_root_can_be_split_into_a_package(module: str) -> None:
    assert violations(module, {"app.providers.tts.kokoro"}) == []


@pytest.mark.parametrize("module", ["app.bootstrap_extra", "app.cli_helpers", "app.commands.voice"])
def test_similar_names_do_not_gain_composition_privileges(module: str) -> None:
    assert violations(module, {"app.providers.tts.kokoro"})


@pytest.mark.parametrize("dependency", ["app.pipeline.short", "app.pipeline.production", "app.pipeline.sfx"])
def test_media_cannot_import_pipeline_orchestration(dependency: str) -> None:
    assert violations("app.media.earshot", {dependency}) == [
        f"app.media.earshot importa {dependency}: mídia só usa models ou schemas"
    ]


def test_media_can_import_schema_packages_but_not_similar_names() -> None:
    assert violations("app.media.host", {"app.pipeline.schemas", "app.pipeline.schemas.episode"}) == []
    assert violations("app.media.host", {"app.pipeline.schemas_helpers"})


@pytest.mark.parametrize(
    ("source", "package", "expected"),
    [
        ("from ..providers.tts import kokoro", "app.pipeline", "app.providers.tts.kokoro"),
        ("from ..pipeline import short", "app.media", "app.pipeline.short"),
        ("from . import production", "app.pipeline", "app.pipeline.production"),
    ],
)
def test_relative_imports_are_checked(source: str, package: str, expected: str) -> None:
    imports = imported_modules(source, package=package)
    assert expected in imports
    assert violations("app.media.earshot", imports)
