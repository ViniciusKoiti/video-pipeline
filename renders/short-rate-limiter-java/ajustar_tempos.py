"""Deriva pronto/content.<idioma>.json: cada cena do tamanho da fala real, com o fluxo reescalado.

Mesma regra do circuit breaker (renders/short-circuit-breaker-java/finalizar.py, `prepare`): duração =
WAV da fala + 0,3 s (a folga do `vp short tempos`, que depois não estica nada); os eventos do fluxo
começam em 1,3 s e o último termina até 0,45 s antes do fim da fala e com 1,4 s de leitura antes do
corte. Os originais não mudam.
"""

import copy
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAD = 0.3
START = 1.3


def events_end(scene):
    tokens = [t["atSec"] + t["durationSec"] for t in scene["tokens"]]
    return max([s["atSec"] for s in scene["states"]] + tokens)


def derive(language):
    episode = ROOT / "data/episodes" / f"short-rate-limiter-java-{language}"
    record = json.loads((episode / "narracao.voz.json").read_text())
    content = copy.deepcopy(json.loads((HERE / f"content.{language}.json").read_text()))
    lines = {line["scene"]: line for line in record["lines"]}
    rows = []
    for scene in content["scenes"]:
        line = lines[scene["id"]]
        before = scene["durationSec"]
        scene["durationSec"] = math.ceil((line["seconds"] + PAD) * 10 - 1e-9) / 10
        scale = 1.0
        if scene["type"] == "flow":
            last = min(line["speech"][1] - 0.45, scene["durationSec"] - 1.4)
            assert last > START, (language, scene["id"], last)
            scale = min(1.0, (last - START) / (events_end(scene) - START))
            for state in scene["states"]:
                state["atSec"] = round(START + (state["atSec"] - START) * scale, 3)
            for token in scene["tokens"]:
                token["atSec"] = round(START + (token["atSec"] - START) * scale, 3)
                token["durationSec"] = round(token["durationSec"] * scale, 3)
        rows.append(f"{scene['id']:10s} {before:5.1f} → {scene['durationSec']:4.1f} s  escala {scale:.2f}")
    out = HERE / "pronto" / f"content.{language}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(language, *rows, f"total {sum(s['durationSec'] for s in content['scenes']):.1f} s", sep="\n  ")


def shrink(language, scene_id, seconds):
    """Depois do `vp short tempos`: encolhe uma cena com vazio acima de 1 s no `juntar` ("sem vazios")."""
    path = HERE / "pronto" / f"content.{language}.voz.json"
    content = json.loads(path.read_text())
    episode = ROOT / "data/episodes" / f"short-rate-limiter-java-{language}"
    line = {x["scene"]: x for x in json.loads((episode / "narracao.voz.json").read_text())["lines"]}[scene_id]
    scene = next(s for s in content["scenes"] if s["id"] == scene_id)
    assert line["seconds"] <= seconds, "o WAV inteiro precisa caber na cena"
    if scene["type"] == "flow":
        assert events_end(scene) + 1.4 <= seconds
    print(f"{language} {scene_id}: {scene['durationSec']} → {seconds} s (WAV {line['seconds']:.2f} s)")
    scene["durationSec"] = seconds
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:2] == ["encolher"]:
        shrink(sys.argv[2], sys.argv[3], float(sys.argv[4]))
    else:
        for language in sys.argv[1:] or ["pt", "en"]:
            derive(language)
