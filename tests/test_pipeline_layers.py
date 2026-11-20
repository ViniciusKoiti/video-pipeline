"""Camadas do `app/pipeline` (ADR 064): cada módulo pertence a uma etapa, e as etapas se empilham.

    base (contratos e utilitários sem etapa)  →  governance (estado, proteção, hashes do gate)
    →  etapas (research, script, visuals, sound, voice, publishing, bench)
    →  fluxos (production, short, gates, status)

Duas regras: um módulo não importa uma etapa de camada acima da sua, e não há ciclo entre etapas.
Dentro da mesma etapa, e entre etapas da mesma camada sem ciclo, vale tudo. Os imports de fora do
pipeline (`commands`, `media`, `providers`, `render`…) e a orquestração de `production` e `short`
(ADR 042) ficam com `test_architecture.py`.

A etapa de um módulo vem do subpacote (`app/pipeline/voice/...` é `voice`; `models/` e `constants/`
são `base`). Enquanto um módulo continua solto em `app/pipeline/`, a etapa dele vem de `ROOT_MODULES`:
módulo novo solto ali entra nessa tabela, e módulo que mudou de pasta sai dela.

Catraca: `KNOWN` lista as violações conhecidas e só encolhe. Import novo que viola falha; entrada
que já não viola tem de sair. Está vazia desde o PR 1 da ADR 064.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from tests.test_architecture import APP, imported_modules, module_name

PIPELINE = APP / "pipeline"

LAYERS: Mapping[str, int] = {
    "base": 0,
    "governance": 1,
    **dict.fromkeys(("research", "script", "visuals", "sound", "voice", "publishing", "bench"), 2),
    **dict.fromkeys(("production", "short", "gates", "status"), 3),
}
BASE_PACKAGES = frozenset({"models", "constants"})

# Etapa de cada módulo ainda solto em app/pipeline/ (distribuição decidida com o dono em 2026-11-19).
ROOT_MODULES: Mapping[str, str] = {
    **dict.fromkeys(
        ("schemas", "ports", "atomic_files", "file_hash", "shots", "attribution", "motion_inputs"), "base"
    ),
    **dict.fromkeys(
        ("state", "protection", "review_hashes", "reopen", "failures", "scene_step", "gate_stamps"),
        "governance",
    ),
    **dict.fromkeys(("sources", "extract", "excerpts", "format_decision"), "research"),
    **dict.fromkeys(
        (
            "check", "check_report", "script_form", "funnel_check", "objective_check",
            "opinion_labels", "narration_gaps", "emotion_marks", "glossary_check", "retention_clock",
            "text_fit", "checagem_local", "numbers", "numbers_citations", "molde", "radar", "briefs",
        ),
        "script",
    ),
    **dict.fromkeys(("assets", "candidates"), "visuals"),
    **dict.fromkeys(("music", "music_library", "sfx", "sfx_inputs"), "sound"),
    **dict.fromkeys(("voice", "voice_state", "voice_timeline", "voice_retake", "speech_review"), "voice"),
    **dict.fromkeys(("package", "metrics", "translation", "medicao", "affiliate", "usage"), "publishing"),
    **dict.fromkeys(("bench", "bench_data"), "bench"),
    **dict.fromkeys(
        ("voice_production", "caption_production", "episode_build", "assembly", "audio_review"),
        "production",
    ),
    **dict.fromkeys(("short_voice", "short_timing", "short_join", "short_mouth", "short_speech"), "short"),
    "gates": "gates",
    "pending": "status",
}

# Violações conhecidas: só encolhe. O PR 1 da ADR 064 (2026-11-19) esvaziou a lista.
KNOWN: frozenset[str] = frozenset()


def stage_of(module: str) -> str | None:
    """Etapa de `app.pipeline...`; `None` para módulo solto que ainda não declarou a sua."""
    parts = module.split(".")[2:]
    if not parts or parts[0] in BASE_PACKAGES:
        return "base"
    if parts[0] in LAYERS:
        return parts[0]
    return ROOT_MODULES.get(parts[0])


def _existing_module(name: str) -> str:
    """`app.pipeline.excerpts.excerpts_of` -> `app.pipeline.excerpts` (o import de função parece módulo)."""
    parts = name.split(".")
    while len(parts) > 2:
        path = APP.parent.joinpath(*parts)
        if path.with_suffix(".py").is_file() or (path / "__init__.py").is_file():
            return ".".join(parts)
        parts.pop()
    return "app.pipeline"


def pipeline_graph() -> dict[str, set[str]]:
    """Módulo do pipeline -> módulos do pipeline que ele importa."""
    graph: dict[str, set[str]] = {}
    for path in sorted(PIPELINE.rglob("*.py")):
        module = module_name(path)
        package = module if path.name == "__init__.py" else module.rpartition(".")[0]
        imports = imported_modules(path.read_text(), package=package)
        graph[module] = {_existing_module(name) for name in imports if name.startswith("app.pipeline")}
    return graph


def _reaches(edges: Mapping[str, set[str]], start: str, goal: str) -> bool:
    seen, todo = {start}, [start]
    while todo:
        for nxt in edges.get(todo.pop(), set()) - seen:
            if nxt == goal:
                return True
            seen.add(nxt)
            todo.append(nxt)
    return False


def layer_violations(graph: Mapping[str, set[str]]) -> dict[str, str]:
    """`"origem -> destino"` -> motivo, para cada import que sobe de camada ou fecha ciclo entre etapas.

    Import que sobe já é violação; sem ele, ciclo só existe entre etapas da mesma camada, e só ali se
    procura. Assim o motivo aponta o import culpado, e não os que só fecham o ciclo por tabela."""
    found: dict[str, str] = {}
    lateral: dict[str, set[str]] = defaultdict(set)
    same_layer: list[tuple[str, str, str, str]] = []
    for module, imports in graph.items():
        src = stage_of(module)
        for name in imports:
            dst = stage_of(name)
            if src is None or dst is None or src == dst:
                continue
            if LAYERS[dst] > LAYERS[src]:
                reason = f"{src} (camada {LAYERS[src]}) importa {dst} (camada {LAYERS[dst]})"
                found[f"{module} -> {name}"] = reason
            elif LAYERS[dst] == LAYERS[src]:
                lateral[src].add(dst)
                same_layer.append((module, name, src, dst))
    for module, name, src, dst in same_layer:
        if _reaches(lateral, dst, src):
            found[f"{module} -> {name}"] = f"ciclo entre {src} e {dst}"
    return found


def test_every_loose_pipeline_module_declares_its_stage() -> None:
    loose = sorted(module_name(p) for p in PIPELINE.glob("*.py") if p.name != "__init__.py")
    undeclared = [m for m in loose if stage_of(m) is None]
    assert undeclared == [], f"declare a etapa em ROOT_MODULES (ADR 064): {undeclared}"
    stale = sorted(set(ROOT_MODULES) - {m.rpartition(".")[2] for m in loose})
    assert stale == [], f"não estão mais soltos em app/pipeline/; tire de ROOT_MODULES: {stale}"


def test_pipeline_layers_only_shrink() -> None:
    found = layer_violations(pipeline_graph())
    new = sorted(set(found) - KNOWN)
    detail = "\n".join(f"{edge}: {found[edge]}" for edge in new)
    assert new == [], f"imports que quebram as camadas (ADR 064):\n{detail}"
    solved = sorted(KNOWN - set(found))
    assert solved == [], f"já resolvidas; tire de KNOWN: {solved}"


def test_checker_catches_a_lower_layer_importing_a_higher_one() -> None:
    graph = {"app.pipeline.state": {"app.pipeline.check"}}
    assert layer_violations(graph) == {
        "app.pipeline.state -> app.pipeline.check": "governance (camada 1) importa script (camada 2)"
    }


def test_checker_catches_a_cycle_between_stages_of_the_same_layer() -> None:
    graph = {
        "app.pipeline.voice.narrator": {"app.pipeline.sound.music"},
        "app.pipeline.sound.music": {"app.pipeline.voice.narrator"},
    }
    assert layer_violations(graph) == {
        "app.pipeline.voice.narrator -> app.pipeline.sound.music": "ciclo entre voice e sound",
        "app.pipeline.sound.music -> app.pipeline.voice.narrator": "ciclo entre sound e voice",
    }


def test_checker_blames_the_upward_import_not_the_ones_closing_the_loop() -> None:
    graph = {
        "app.pipeline.state": {"app.pipeline.numbers"},  # governance sobe para script
        "app.pipeline.check": {"app.pipeline.state"},  # script desce para governance: legítimo
    }
    assert set(layer_violations(graph)) == {"app.pipeline.state -> app.pipeline.numbers"}


def test_checker_allows_going_down_and_crossing_without_a_cycle() -> None:
    graph = {
        "app.pipeline.short.timing": {
            "app.pipeline.sound.sfx", "app.pipeline.voice", "app.pipeline.schemas",
        },
        "app.pipeline.script.check": {"app.pipeline.research.excerpts", "app.pipeline.models.scene"},
        "app.pipeline.voice.state": {"app.pipeline.governance.state", "app.pipeline.constants.x"},
    }
    assert layer_violations(graph) == {}


def test_stage_comes_from_the_subpackage_once_the_module_moves() -> None:
    assert stage_of("app.pipeline.voice.models.voice_key") == "voice"
    assert stage_of("app.pipeline.models.scene") == "base"
    assert stage_of("app.pipeline") == "base"
    assert stage_of("app.pipeline.pending") == "status"
    assert stage_of("app.pipeline.nao_declarado") is None


def test_existing_module_drops_the_imported_function() -> None:
    assert _existing_module("app.pipeline.excerpts.excerpts_of") == "app.pipeline.excerpts"
    assert _existing_module("app.pipeline.models.scene") == "app.pipeline.models.scene"
