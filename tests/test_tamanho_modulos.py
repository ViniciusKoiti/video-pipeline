"""Gate de tamanho em `app/` (o S do SOLID): cada módulo até `MAX_CODE_LINES_PER_FILE` linhas de código e cada
função ou método até `MAX_CODE_LINES_PER_FUNCTION`. Linha de código é a que tem algum token fora de branco,
comentário e docstring: documentar não conta contra o limite.

Catraca: o que hoje passa do limite está em `tests/baseline_tamanho_app.json` com o tamanho de hoje e só pode
encolher. Arquivo ou função nova acima do limite falha; entrada da baseline que já cabe no limite, ou que não
existe mais, tem de sair dela. Regenerar a baseline, só quando um PR encolheu ou dividiu algo:
`uv run python tests/test_tamanho_modulos.py --baseline`. Sem argumento, roda o gate (também no pré-commit).
"""

from __future__ import annotations

import ast
import io
import json
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
BASELINE = Path(__file__).with_name("baseline_tamanho_app.json")

MAX_CODE_LINES_PER_FILE = 200
MAX_CODE_LINES_PER_FUNCTION = 50

_NOT_CODE = {
    tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING,
    tokenize.ENDMARKER,
}


def _docstring_lines(tree: ast.AST) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        first = node.body[0] if node.body else None
        value = first.value if isinstance(first, ast.Expr) else None
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return lines


def code_line_numbers(source: str) -> set[int]:
    """Números das linhas com código; fora ficam as em branco, os comentários e as docstrings."""
    docs = _docstring_lines(ast.parse(source))
    lines: set[int] = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in _NOT_CODE:
            continue
        lines.update(n for n in range(token.start[0], token.end[0] + 1) if n not in docs)
    return lines


def function_spans(source: str) -> dict[str, tuple[int, int]]:
    """`Classe.metodo` ou `funcao.aninhada` -> (primeira linha, última linha), decoradores fora."""
    spans: dict[str, tuple[int, int]] = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                spans[name] = (child.lineno, child.end_lineno or child.lineno)
                visit(child, f"{name}.")
            elif isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            else:
                visit(child, prefix)

    visit(ast.parse(source), "")
    return spans


@dataclass(frozen=True)
class Measure:
    files: dict[str, int] = field(default_factory=dict)  # caminho -> linhas de código
    functions: dict[str, int] = field(default_factory=dict)  # "caminho::nome" -> linhas de código


def measure(root: Path = APP) -> Measure:
    files: dict[str, int] = {}
    functions: dict[str, int] = {}
    for path in sorted(root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        code = code_line_numbers(source)
        rel = path.relative_to(ROOT).as_posix()
        files[rel] = len(code)
        for name, (start, end) in function_spans(source).items():
            functions[f"{rel}::{name}"] = sum(1 for n in code if start <= n <= end)
    return Measure(files, functions)


def violations(current: Measure, baseline: dict[str, dict[str, int]]) -> list[str]:
    """O que falha: novo acima do limite, crescimento de quem está na baseline e entrada obsoleta."""
    problems: list[str] = []
    limits = (
        ("files", MAX_CODE_LINES_PER_FILE, current.files),
        ("functions", MAX_CODE_LINES_PER_FUNCTION, current.functions),
    )
    for kind, limit, measured in limits:
        known = baseline.get(kind, {})
        for name, lines in measured.items():
            allowed = known.get(name)
            if lines <= limit:
                if allowed is not None:
                    problems.append(f"{name}: cabe no limite ({lines} <= {limit}); tire da baseline")
            elif allowed is None:
                problems.append(f"{name}: {lines} linhas de código (limite {limit}); divida")
            elif lines > allowed:
                problems.append(f"{name}: cresceu de {allowed} para {lines} (limite {limit}); só encolhe")
        problems += [f"{name}: não existe mais; tire da baseline" for name in known if name not in measured]
    return problems


def load_baseline(path: Path = BASELINE) -> dict[str, dict[str, int]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    limits = (data.get("max_code_lines_per_file"), data.get("max_code_lines_per_function"))
    if limits != (MAX_CODE_LINES_PER_FILE, MAX_CODE_LINES_PER_FUNCTION):
        raise AssertionError(f"{path.name}: limites {limits} diferentes do teste; regenere com --baseline")
    return {"files": data.get("files", {}), "functions": data.get("functions", {})}


def write_baseline(current: Measure, path: Path = BASELINE) -> int:
    data = {
        "max_code_lines_per_file": MAX_CODE_LINES_PER_FILE,
        "max_code_lines_per_function": MAX_CODE_LINES_PER_FUNCTION,
        "files": {k: v for k, v in current.files.items() if v > MAX_CODE_LINES_PER_FILE},
        "functions": {k: v for k, v in current.functions.items() if v > MAX_CODE_LINES_PER_FUNCTION},
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(data["files"]) + len(data["functions"])


def test_modulos_e_funcoes_de_app_dentro_do_limite() -> None:
    problems = violations(measure(), load_baseline())
    hint = "Baseline só quando algo encolheu: uv run python tests/test_tamanho_modulos.py --baseline"
    assert not problems, "\n".join(["gate de tamanho (tests/test_tamanho_modulos.py):", *problems, hint])


def test_linhas_de_codigo_ignoram_docstring_comentario_e_branco() -> None:
    source = (
        '"""Doc\n\nem três linhas."""\n\n# comentário\nx = 1  # inline\n\n\n'
        'def f():\n    """Doc."""\n    return (\n        x\n    )\n'
    )
    assert code_line_numbers(source) == {6, 9, 11, 12, 13}
    assert function_spans(source) == {"f": (9, 13)}


def test_catraca_recusa_novo_crescimento_e_entrada_obsoleta() -> None:
    limit = MAX_CODE_LINES_PER_FILE
    baseline = {"files": {"app/a.py": limit + 10, "app/sumiu.py": limit + 1}, "functions": {}}
    current = Measure(files={"app/a.py": limit + 11, "app/novo.py": limit + 1, "app/ok.py": limit})
    found = violations(current, baseline)
    assert [p.split(":")[0] for p in found] == ["app/a.py", "app/novo.py", "app/sumiu.py"]
    assert not violations(Measure(files={"app/a.py": limit + 10}), {"files": {"app/a.py": limit + 10}})
    assert violations(Measure(files={"app/a.py": limit}), {"files": {"app/a.py": limit + 10}})


def main(argv: list[str]) -> int:
    current = measure()
    if "--baseline" in argv:
        count = write_baseline(current)
        print(f"{BASELINE.relative_to(ROOT)}: {count} entrada(s) acima do limite, com o tamanho de hoje")
        return 0
    problems = violations(current, load_baseline())
    for problem in problems:
        print(problem)
    print(f"gate de tamanho: {len(problems)} problema(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
