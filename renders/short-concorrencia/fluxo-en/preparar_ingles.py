"""Tradução da versão publicada em C, preservando os dados e os desenhos originais."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "data/episodes/short-concorrencia-fluxo-pt"
EPISODE = ROOT / "data/episodes/short-concorrencia-fluxo-en"

LABELS = {
    "C · sem proteção": "C · no protection",
    "Exemplo didático": "Illustrative example",
    "contador compartilhado": "shared counter",
    "LER": "READ", "SOMAR": "ADD", "GRAVAR": "WRITE",
    "lê 10": "reads 10", "grava 11": "writes 11",
    "11, e não 12: uma soma perdida": "11, not 12: one update lost",
    "Em C: comportamento indefinido": "In C: undefined behavior",
    "C · com mutex": "C · with a mutex",
    "lock → trecho protegido → unlock": "lock → protected section → unlock",
    "TRECHO PROTEGIDO": "PROTECTED SECTION",
    "A entra": "A enters", "B entra": "B enters",
    "B espera a mesma trava": "B waits for the same lock",
    "destrava": "unlock",
    "Um thread por vez nesse trecho": "One thread at a time in this section",
    "UMA OPERAÇÃO INDIVISÍVEL": "ONE INDIVISIBLE OPERATION",
    "contador em C": "counter in C",
    "10 → 11 → 12: cada soma conta": "10 → 11 → 12: every update counts",
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    if (EPISODE / "review.json").exists():
        raise SystemExit("A pasta inglesa já tem decisões de revisão; não sobrescrever suas entradas.")
    content = json.loads((SOURCE / "content.json").read_text())
    source_narration = json.loads((SOURCE / "narracao.json").read_text())
    texts = {
        "gancho": "In C, two threads each add a million times. The total should be two million.",
        "resultado": "Without protection, the total fell short.",
        "codigo": "An increment reads the value, adds, and writes it back. "
                  "Imagine the two threads reading ten and writing eleven: an update is lost. "
                  "In C, this data race has undefined behavior.",
        "mutex": "The mutex lets one thread at a time enter this section.",
        "atomic": "The atomic increment makes the read, add, and write one indivisible operation, "
                  "so this counter does not lose increments.",
        "tempo": "Without protection, eleven milliseconds, and wrong. With a mutex, ninety-two, and correct. "
                 "With atomic, 21, and correct.",
        "fecho": "How does this work in other languages? Comment which language you would like to see "
                 "in the next video.",
    }
    narration = {"language": "en", "lines": []}
    for original in source_narration["lines"]:
        line = deepcopy(original)
        line["text"] = texts[line["scene"]]
        narration["lines"].append(line)
    content["footer"] = (
        "Measured 2026-11-01 · gcc 15.2 -O2 · Ryzen 7 5700U · "
        "2 threads · expected: 2,000,000 · 15 runs"
    )
    for scene in content["scenes"]:
        if scene["id"] == "gancho":
            scene.update(kicker="C · concurrency",
                         text="In C: 2 threads. 1 counter. It should total 2,000,000.",
                         highlight="should total 2,000,000")
        elif scene["id"] == "resultado":
            scene["left"]["label"] = "no protection (median)"
            scene["right"]["label"] = "mutex and atomic"
        elif scene["id"] == "tempo":
            scene["title"] = "Time per run"
            scene["items"][0]["label"] = "no protection · wrong"
        elif scene["id"] == "fecho":
            scene.update(text="What about other languages?", sub="Comment which one you want next")

    licenses = []
    for asset_id, asset in content["assets"].items():
        source = json.loads((SOURCE / "public" / asset["path"]).read_text())
        animation = deepcopy(source)
        for layer in animation["layers"]:
            if layer.get("ty") != 5:
                continue
            for key in layer["t"]["d"]["k"]:
                old = key["s"]["t"]
                key["s"]["t"] = LABELS.get(old, old)
                layer["nm"] = key["s"]["t"]
                assert old in LABELS or old in {"10", "11", "12", "10 + 1 = 11", "THREAD A", "THREAD B",
                                              "C · atomic_fetch_add"}, old
        assert [x["ks"] for x in source["layers"]] == [x["ks"] for x in animation["layers"]]
        for folder in (BASE, EPISODE):
            save(folder / "public" / asset["path"], animation)
        digest = hashlib.sha256((BASE / "public" / asset["path"]).read_bytes()).hexdigest()
        licenses.append({"id": asset_id, "file": "public/" + asset["path"], "license": "Original",
                         "sha256": digest, "usage_notes": "English labels on the original C diagrams; "
                         "same illustrative states, no new measurements."})
    for name, value in (("content", content), ("narracao", narration)):
        save(BASE / f"{name}.en.json", value)
        save(EPISODE / f"{name}.json", value)
    for name in ("medicao", "sfx"):
        value = json.loads((SOURCE / f"{name}.json").read_text())
        save(BASE / f"{name}.en.json", value)
        save(EPISODE / f"{name}.json", value)
    save(EPISODE / "traducao.json", {
        "derived_from": "short-concorrencia-fluxo-pt", "language": "en", "source_language": "pt-BR"
    })
    save(BASE / "licencas.json", licenses)
    assert [x["scene"] for x in narration["lines"]] == [x["id"] for x in content["scenes"]]
    print("7 scenes translated; 3 original diagrams localized; published Portuguese inputs untouched.")


if __name__ == "__main__":
    main()
