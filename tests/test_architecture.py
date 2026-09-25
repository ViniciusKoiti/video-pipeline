"""Regras de dependência da ADR 006, verificadas no código-fonte (sem importar nada)."""

from __future__ import annotations

import ast
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"

FUNCTIONS = sorted(p.name for p in (APP / "providers").iterdir() if p.is_dir() and p.name != "__pycache__")
# app.providers.<função>.<adapter> ou app.render.<motor>, exceto os módulos base (e o que vem deles).
CONCRETE_ADAPTER = re.compile(rf"^app\.(providers\.({'|'.join(FUNCTIONS)})|render)\.(?!base(\.|$))[a-z_]")
COMPOSITION = ("app.bootstrap", "app.cli")
HEAVY = {"kokoro", "torch", "soundfile", "misaki", "spacy"}


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(APP.parent).with_suffix("").parts).removesuffix(".__init__")


def imported_modules(source: str) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module)
            # `from pacote import submódulo`: módulos são minúsculos; classes (CapWords) não entram.
            found |= {f"{node.module}.{a.name}" for a in node.names if a.name[:1].islower()}
    return found


def violations(module: str, imports: set[str]) -> list[str]:
    problems = []
    for name in sorted(imports):
        if module.startswith("app.pipeline"):
            if CONCRETE_ADAPTER.match(name) or name.startswith(COMPOSITION) or name.split(".")[0] in HEAVY:
                problems.append(f"{module} importa {name}: o pipeline só conhece portas")
        elif module.startswith(("app.providers", "app.render")):
            if name.startswith("app.pipeline.") and not name.startswith("app.pipeline.schemas"):
                problems.append(f"{module} importa {name}: adapters só usam app.pipeline.schemas")
            if name.startswith((*COMPOSITION, "app.settings")):
                problems.append(f"{module} importa {name}: adapters recebem parâmetros explícitos")
        elif module not in COMPOSITION and CONCRETE_ADAPTER.match(name):
            problems.append(f"{module} importa {name}: só app.bootstrap conhece adapters concretos")
    return problems


def test_dependency_rules_hold_for_the_whole_app() -> None:
    problems = []
    for path in sorted(APP.rglob("*.py")):
        problems += violations(module_name(path), imported_modules(path.read_text()))
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


def test_checker_catches_adapter_reaching_into_orchestration() -> None:
    source = "from app.pipeline.ports import Context\nfrom app.settings import Settings\n"
    assert violations("app.providers.text.ollama", imported_modules(source)) == [
        "app.providers.text.ollama importa app.pipeline.ports: adapters só usam app.pipeline.schemas",
        "app.providers.text.ollama importa app.settings: adapters recebem parâmetros explícitos",
    ]


def test_checker_keeps_concrete_adapters_inside_the_composition_root() -> None:
    source = "from app.providers.text.ollama import OllamaText\n"
    assert violations("app.bootstrap", imported_modules(source)) == []
    assert violations("app.media.probe", imported_modules(source)) == [
        "app.media.probe importa app.providers.text.ollama: só app.bootstrap conhece adapters concretos"
    ]
