"""Medição própria como prova (ADR 034): cada número do Short aponta para o arquivo de resultado do dono."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.pipeline.gates import GateError, record_decision
from app.pipeline.medicao import (
    Numero,
    coverage_problems,
    entry_problems,
    medicao_problems,
    narration_numbers,
    screen_numbers,
)
from app.pipeline.schemas import Decision, Step
from app.pipeline.translation import Narration
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME

EPISODE = "short-teste"
RESULTADO = (
    "# 2026-10-30 | gcc 15.2.0 -O2 | mediana de 15\n"
    "n=1000  sequencial=0.003 ms  embaralhada=0.003 ms  razao=1.0x\n"
    "n=10000000  sequencial=26.877 ms  embaralhada=2420.782 ms  razao=90.1x\n"
    "n=10000000  sequencial=29.856 ms  embaralhada=2434.294 ms  razao=81.5x\n"
)
NARRATION = {
    "language": "pt-BR",
    "lines": [
        {"scene": "codigo", "text": "São dez milhões de nós."},
        {
            "scene": "resultado",
            "text": "Uns trinta milissegundos contra mais de dois segundos. Oitenta a noventa vezes.",
        },
    ],
}
CONTENT = {
    "fps": 30,
    "footer": "gcc 15.2 -O2 · 2026-10-30",
    "scenes": [
        {
            "id": "codigo",
            "type": "grid",
            "durationSec": 9,
            "cells": [
                {"kind": "number", "value": 10000000, "label": "nós"},
                {"kind": "text", "text": "Lista 2: embaralhada"},
            ],
        },
        {
            "id": "resultado",
            "type": "comparison",
            "durationSec": 9,
            "left": {"value": 26.9},
            "right": {"value": 2420.8},
        },
        {
            "id": "tamanho",
            "type": "categories",
            "durationSec": 7,
            "decimals": 1,
            "items": [{"label": "1 mil nós", "value": 1.0}],
        },
    ],
}
MEDICAO = {
    "arquivo": "demo/resultado.txt",
    "numeros": [
        {"valor": 10000000, "trechos": ["n=10000000"], "medidos": [10000000]},
        {"valor": 1000, "trechos": ["n=1000  "], "medidos": [1000]},
        {
            "valor": 30,
            "trechos": ["sequencial=26.877 ms", "sequencial=29.856 ms"],
            "medidos": [26.877, 29.856],
            "tolerancia": 0.12,
            "cenas": ["resultado"],
            "nota": "resume as duas rodadas",
        },
        {
            "valor": 2,
            "trechos": ["embaralhada=2420.782 ms"],
            "medidos": [2420.782],
            "fator": 0.001,
            "tolerancia": 0.22,
            "cenas": ["resultado"],
            "nota": "mais de dois segundos",
        },
        {
            "valor": 80,
            "trechos": ["razao=81.5x"],
            "medidos": [81.5],
            "tolerancia": 0.02,
            "cenas": ["resultado"],
        },
        {"valor": 90, "trechos": ["razao=90.1x"], "medidos": [90.1], "cenas": ["resultado"]},
        {"valor": 26.9, "trechos": ["sequencial=26.877 ms"], "medidos": [26.877], "tolerancia": 0.002},
        {
            "valor": 2420.8,
            "trechos": ["embaralhada=2420.782 ms"],
            "medidos": [2420.782],
            "tolerancia": 0.0001,
        },
        {"valor": 1.0, "trechos": ["razao=1.0x"], "cenas": ["tamanho"]},
        {"valor": 2, "cenas": ["codigo"], "nota": "'Lista 2' é nome, não medida"},
    ],
}


def write(root: Path, name: str, data: dict | str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def make_store(tmp_path: Path, medicao: dict | None = MEDICAO) -> JsonFileStore:
    root = tmp_path / "data" / "episodes" / EPISODE
    write(root, "narracao.json", NARRATION)
    write(root, "demo/resultado.txt", RESULTADO)
    write(root, "content.json", CONTENT)
    if medicao is not None:
        write(root, "medicao.json", medicao)
    return JsonFileStore(tmp_path / "data" / "episodes")


def approve_preview(store: JsonFileStore, review: JsonReviewGate):
    return record_decision(
        store, review, EPISODE, Step.PREVIEW, Decision.APPROVED, reviewer="Dono", now=lambda: FIXED_TIME
    )


def test_numbers_spoken_and_shown_are_collected_by_scene() -> None:
    spoken = narration_numbers(Narration.model_validate(NARRATION))
    assert spoken == [("codigo", 10000000.0)] + [("resultado", v) for v in (30.0, 2.0, 80.0, 90.0)]
    shown = screen_numbers(CONTENT, "pt-BR")
    assert ("codigo", 10000000.0) in shown and ("codigo", 2.0) in shown  # value e o "Lista 2" do texto
    assert ("resultado", 26.9) in shown and ("tamanho", 1000.0) in shown and ("tamanho", 1.0) in shown
    assert not any(v in (30.0, 9.0, 7.0, 15.2) for _, v in shown)  # fps, durationSec, decimals, footer


def test_a_declared_number_needs_its_quote_measured_values_and_tolerance() -> None:
    ok = Numero(valor=30, trechos=["sequencial=29.856 ms"], medidos=[29.856])
    assert entry_problems(1, ok, RESULTADO) == []
    missing_quote = Numero(valor=30, trechos=["sequencial=31.000 ms"])
    assert "não está no arquivo de resultado" in entry_problems(1, missing_quote, RESULTADO)[0]
    wrong_measured = Numero(valor=30, trechos=["sequencial=29.856 ms"], medidos=[29.0])
    assert "o medido 29 não aparece nos trechos" in entry_problems(1, wrong_measured, RESULTADO)[0]
    too_far = Numero(valor=40, trechos=["sequencial=29.856 ms"], medidos=[29.856])
    assert "não cabe na tolerância de 1%" in entry_problems(1, too_far, RESULTADO)[0]
    unit = Numero(valor=2.4, trechos=["embaralhada=2420.782 ms"], fator=0.001, tolerancia=0.01)
    assert entry_problems(1, unit, RESULTADO) == []
    assert "sem trecho do resultado e sem nota" in entry_problems(1, Numero(valor=2), RESULTADO)[0]
    assert entry_problems(1, Numero(valor=2, nota="nome da lista"), RESULTADO) == []


def test_every_number_must_have_an_entry_in_its_scene() -> None:
    entries = [Numero(valor=2, cenas=["codigo"], nota="nome"), Numero(valor=90, trechos=["razao=90.1x"])]
    numbers = [("codigo", 2.0), ("resultado", 2.0), ("fecho", 90.0)]
    problems, used = coverage_problems(numbers, entries, "fala")
    assert problems == ["fala de resultado: 2 não está no medicao.json"]
    assert used == {0, 1}


def test_the_pilot_shaped_short_is_clean_and_unused_entries_are_warnings(tmp_path: Path) -> None:
    extra = {**MEDICAO, "numeros": [*MEDICAO["numeros"], {"valor": 7, "nota": "sobra"}]}
    problems, warnings = medicao_problems(make_store(tmp_path, medicao=extra), EPISODE)
    assert problems == []
    assert warnings == ["medicao.json, número 11 (7): declarado e não usado na fala nem na tela"]


def test_missing_file_wrong_path_or_uncovered_number_are_problems(tmp_path: Path) -> None:
    assert "falta arquivo" in medicao_problems(make_store(tmp_path, medicao=None), EPISODE)[0][0]
    wrong_path = {**MEDICAO, "arquivo": "demo/outro.txt"}
    assert "não existe" in medicao_problems(make_store(tmp_path, medicao=wrong_path), EPISODE)[0][0]
    thin = {**MEDICAO, "numeros": MEDICAO["numeros"][:-1]}  # sem a entrada do "Lista 2"
    problems, _ = medicao_problems(make_store(tmp_path, medicao=thin), EPISODE)
    assert problems == ["tela de codigo: 2 não está no medicao.json"]


def test_gate_4_refuses_a_short_whose_measurement_check_fails(tmp_path: Path) -> None:
    thin = {**MEDICAO, "numeros": MEDICAO["numeros"][:-1]}
    store = make_store(tmp_path, medicao=thin)
    renders = tmp_path / "data" / "episodes" / EPISODE / "renders"
    renders.mkdir()
    (renders / "final.mp4").write_bytes(b"mp4")
    review = JsonReviewGate(store)
    with pytest.raises(GateError, match="conferência da medição achou 1 problema"):
        approve_preview(store, review)
    store = make_store(tmp_path)  # medicao.json completo: o gate abre
    assert approve_preview(store, review).decision is Decision.APPROVED
