"""ADR 045: o layout dos erros é verificado no código-fonte, como os de modelos e constantes.

1. Toda classe de exceção de `app/` herda de `PipelineError`, direta ou indiretamente.
2. Comandos e scripts não capturam erro do projeto por tipo: levantam, e o handler central decide a saída.
   `except PipelineError` sozinho (recuperação por item) e exceções que não são do projeto seguem livres.
   As exceções à regra estão na lista abaixo, com o motivo, e ela só encolhe.
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILTIN_ERRORS = {
    n for n, v in vars(builtins).items() if isinstance(v, type) and issubclass(v, BaseException)
}
SCRIPT_DIRS = ("scripts/provisorio", "scripts/bench", "scripts/ferramentas")
GUARDED = ("app/cli.py", "app/commands", *SCRIPT_DIRS)

# Arquivo -> motivo. Sair da lista quando o `except` sair; entrar nela, só com motivo e decisão do dono.
ALLOWED = {
    "app/commands/postiz.py": "contrato de erro em JSON, com mensagens fixas que não vazam segredo",
    "app/commands/usage.py": "contrato de erro em JSON, com mensagens fixas",
    "app/commands/postiz_cadeia.py": "registra a falha do agendamento na trilha e relança (auditoria)",
}


def class_bases(sources: dict[str, str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ClassDef):
                found[node.name] = [
                    b.id if isinstance(b, ast.Name) else getattr(b, "attr", "?") for b in node.bases
                ]
    return found


def exception_classes(bases: dict[str, list[str]]) -> set[str]:
    errors = {name for name, parents in bases.items() if any(p in BUILTIN_ERRORS for p in parents)}
    grew = True
    while grew:
        grew = False
        for name, parents in bases.items():
            if name not in errors and any(p in errors for p in parents):
                errors.add(name)
                grew = True
    return errors


def outside_the_pipeline_error_tree(bases: dict[str, list[str]]) -> list[str]:
    def rooted(name: str, seen: frozenset[str] = frozenset()) -> bool:
        if name == "PipelineError":
            return True
        return any(rooted(p, seen | {name}) for p in bases.get(name, []) if p in bases and p not in seen)

    return sorted(n for n in exception_classes(bases) if n != "PipelineError" and not rooted(n))


def caught_project_errors(source: str, project: set[str]) -> list[tuple[int, str]]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ExceptHandler) and node.type is not None:
            types = node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
            names = [t.id if isinstance(t, ast.Name) else getattr(t, "attr", "?") for t in types]
            found += [(node.lineno, name) for name in names if name in project and name != "PipelineError"]
    return found


def app_sources() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): p.read_text() for p in sorted((ROOT / "app").rglob("*.py"))}


def guarded_sources() -> dict[str, str]:
    files = [
        ROOT / "app/cli.py",
        *(ROOT / "app/commands").glob("*.py"),
        *(path for folder in SCRIPT_DIRS for path in (ROOT / folder).glob("*.py")),
    ]
    return {str(p.relative_to(ROOT)): p.read_text() for p in sorted(files)}


def test_every_exception_class_in_app_derives_from_pipeline_error() -> None:
    bases = class_bases(app_sources())
    assert len(exception_classes(bases)) > 25  # o scanner enxerga as classes de hoje
    assert outside_the_pipeline_error_tree(bases) == []


def test_commands_and_scripts_do_not_catch_project_errors_by_type() -> None:
    project = exception_classes(class_bases(app_sources()))
    offenders = {
        path: caught_project_errors(source, project)
        for path, source in guarded_sources().items()
        if caught_project_errors(source, project)
    }
    unexpected = {path: hits for path, hits in offenders.items() if path not in ALLOWED}
    assert unexpected == {}, "use o handler central (app.commands.errors.run) em vez de try/except"
    stale = sorted(path for path in ALLOWED if path not in offenders)
    assert stale == [], f"saiu o except: tire da lista ALLOWED {stale}"


def test_checker_catches_a_class_outside_the_tree_and_a_listed_except() -> None:
    sources = {
        "a.py": "class Raiz(Exception): pass\nclass Filha(Raiz): pass\n"
        "class PipelineError(Exception): pass\nclass Boa(PipelineError, ValueError): pass\n"
    }
    bases = class_bases(sources)
    assert outside_the_pipeline_error_tree(bases) == ["Filha", "Raiz"]
    project = exception_classes(bases)
    code = (
        "try:\n    pass\nexcept (Boa, OSError):\n    pass\n"
        "except PipelineError:\n    pass\nexcept KeyError:\n    pass\n"
    )
    assert caught_project_errors(code, project) == [
        (3, "Boa")
    ]  # só o do projeto, e não `PipelineError` sozinho


def test_the_guard_reads_every_script_folder() -> None:
    paths = set(guarded_sources())
    assert {
        "scripts/provisorio/evolucao.py",
        "scripts/bench/checagem_local.py",
        "scripts/ferramentas/clipe_tempos.py",
    } <= paths
