"""Medição própria como prova (ADR 034, adapter "medição própria"): cada número do Short aponta para o
arquivo de resultado de uma execução do dono.

O Short técnico não tem fontes nem fichas: a prova é o `resultado.txt` que o programa do dono imprimiu. O
`medicao.json` da pasta do vídeo declara cada número que a fala diz ou a tela mostra, com o trecho **literal**
do arquivo de resultado que o sustenta (como a `quote` de uma ficha) e, quando a fala arredonda ("uns trinta",
"oitenta a noventa"), os valores medidos e a tolerância. O código confere: o trecho existe no arquivo, os
valores medidos estão no trecho, o número dito cabe na tolerância, e nenhum número da fala ou da tela ficou
sem entrada. Quem decide continua sendo o dono, no gate 4, que só abre com esta conferência limpa.

Fora da conferência: o `footer` (a legenda do ambiente, conferida de olho) e o `kicker`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import Field

from app.pipeline.ports import ManifestNotFound, ManifestStore
from app.pipeline.schemas import Model
from app.pipeline.translation import CONTENT_FILE, NARRATION_FILE, Narration, spoken_numbers

MEDICAO_FILE = "medicao.json"
TEXT_KEYS = frozenset({"text", "title", "sub", "label", "highlight"})  # strings da tela que contam
DEFAULT_TOLERANCE = 0.01
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


class Numero(Model):
    """Um número dito ou mostrado, e de onde ele vem."""

    valor: float
    trechos: list[str] = []  # trechos literais do arquivo de resultado
    medidos: list[float] = []  # os valores medidos que o número resume; vazio = os números dos trechos
    tolerancia: float = Field(default=DEFAULT_TOLERANCE, ge=0)  # relativa ao medido
    fator: float = 1.0  # unidade: medido × fator = a unidade dita (ms → s é 0.001)
    cenas: list[str] | None = None  # só vale nessas cenas; None = em qualquer cena
    nota: str | None = None  # obrigatória sem trechos: por que não é uma medida (nome, contagem)


class Medicao(Model):
    arquivo: str  # relativo à pasta do vídeo ou à raiz do repositório
    ambiente: str | None = None
    numeros: list[Numero]


def _numbers_in(text: str) -> list[float]:
    return [float(t.replace(",", ".")) for t in _NUMBER.findall(text)]


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def screen_numbers(content: dict[str, Any], language: str) -> list[tuple[str, float]]:
    """(cena, número) para cada `value` numérico e cada número dito nos textos da tela."""
    found: list[tuple[str, float]] = []

    def walk(node: Any, scene: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "value" and isinstance(value, int | float) and not isinstance(value, bool):
                    found.append((scene, float(value)))
                elif key in TEXT_KEYS and isinstance(value, str):
                    found.extend((scene, float(n)) for n in spoken_numbers(value, language))
                elif isinstance(value, dict | list):
                    walk(value, scene)
        elif isinstance(node, list):
            for item in node:
                walk(item, scene)

    for scene in content.get("scenes", []):
        walk(scene, str(scene.get("id", "?")))
    return found


def narration_numbers(narration: Narration) -> list[tuple[str, float]]:
    return [
        (line.scene or "?", float(n))
        for line in narration.lines
        for n in spoken_numbers(line.text, narration.language)
    ]


def entry_problems(n: int, entry: Numero, evidence: str) -> list[str]:
    """O que a entrada afirma e o arquivo de resultado não sustenta."""
    label = f"medicao.json, número {n} ({entry.valor:g})"
    if not entry.trechos:
        return [] if entry.nota else [f"{label}: sem trecho do resultado e sem nota dizendo por quê"]
    problems = []
    in_quotes: list[float] = []
    for quote in entry.trechos:
        if quote not in evidence:
            problems.append(f"{label}: o trecho {quote!r} não está no arquivo de resultado")
        in_quotes += _numbers_in(quote)
    for measured in entry.medidos:
        if not any(_same(measured, q) for q in in_quotes):
            problems.append(f"{label}: o medido {measured:g} não aparece nos trechos")
    candidates = [m * entry.fator for m in (entry.medidos or in_quotes)]
    fits = any(abs(entry.valor - c) <= entry.tolerancia * abs(c) + 1e-9 for c in candidates)
    if candidates and not fits:
        shown = ", ".join(f"{c:g}" for c in candidates)
        problems.append(
            f"{label}: não cabe na tolerância de {entry.tolerancia:.0%} sobre o medido ({shown})"
        )
    return problems


def coverage_problems(
    numbers: list[tuple[str, float]], entries: list[Numero], where: str
) -> tuple[list[str], set[int]]:
    """Números ditos ou mostrados sem entrada; devolve também os índices das entradas usadas."""
    problems, used = [], set()
    for scene, value in numbers:
        matches = [
            i
            for i, entry in enumerate(entries)
            if _same(entry.valor, value) and (entry.cenas is None or scene in entry.cenas)
        ]
        if matches:
            used.update(matches)
        else:
            problems.append(f"{where} de {scene}: {value:g} não está no medicao.json")
    return problems, used


def _evidence_path(store: ManifestStore, episode_id: str, relative: str) -> Path | None:
    for candidate in (store.path(episode_id, relative), Path(relative)):
        if candidate.is_file():
            return candidate
    return None


def medicao_problems(store: ManifestStore, episode_id: str) -> tuple[list[str], list[str]]:
    """(problemas, avisos) da conferência; sem problemas, o gate 4 pode abrir."""
    try:
        plan = store.read(episode_id, MEDICAO_FILE, Medicao)
        narration = store.read(episode_id, NARRATION_FILE, Narration)
    except ManifestNotFound as error:
        return [f"falta arquivo para conferir a medição ({error})"], []
    except ValueError as error:
        return [f"arquivo inválido ({error})"], []
    evidence_path = _evidence_path(store, episode_id, plan.arquivo)
    if evidence_path is None:
        return [f"medicao.json: o arquivo de resultado {plan.arquivo!r} não existe"], []
    evidence = evidence_path.read_text(encoding="utf-8")
    problems: list[str] = []
    for n, entry in enumerate(plan.numeros, start=1):
        problems += entry_problems(n, entry, evidence)
    spoken = narration_numbers(narration)
    missing, used = coverage_problems(spoken, plan.numeros, "fala")
    problems += missing
    content_path = store.path(episode_id, CONTENT_FILE)
    if content_path.is_file():
        import json

        shown = screen_numbers(json.loads(content_path.read_text(encoding="utf-8")), narration.language)
        missing, used_screen = coverage_problems(shown, plan.numeros, "tela")
        problems += missing
        used |= used_screen
    warnings = [
        f"medicao.json, número {i + 1} ({entry.valor:g}): declarado e não usado na fala nem na tela"
        for i, entry in enumerate(plan.numeros)
        if i not in used
    ]
    return problems, warnings
