"""Ajusta a duração das animações traduzidas à fala inglesa, sem mudar texto ou desenho."""

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SOURCE = ROOT / "data/episodes/short-concorrencia-fluxo-pt"
EPISODE = ROOT / "data/episodes/short-concorrencia-fluxo-en"


def spoken_times(path):
    data = json.loads(path.read_text())
    return {line["scene"]: line["speech"][1] - line["speech"][0] for line in data["lines"]}


def scale_times(value, ratio):
    if isinstance(value, dict):
        return {k: round(v * ratio, 6) if k in {"t", "tm", "ip", "op", "st", "dr"}
                and isinstance(v, int | float) else scale_times(v, ratio) for k, v in value.items()}
    if isinstance(value, list):
        return [scale_times(item, ratio) for item in value]
    return value


def texts(animation):
    return [key["s"]["t"] for layer in animation["layers"] if layer["ty"] == 5
            for key in layer["t"]["d"]["k"]]


def main():
    if (EPISODE / "review.json").exists():
        raise SystemExit("A versão inglesa já tem decisões de revisão; não sobrescrever os ativos.")
    pt = spoken_times(SOURCE / "narracao.voz.json")
    en = spoken_times(EPISODE / "narracao.voz.json")
    records = []
    for scene in ("codigo", "mutex", "atomic"):
        ratio = en[scene] / pt[scene]
        assert 0 < ratio < 3
        source = json.loads((BASE / "public/lottie" / f"{scene}.json").read_text())
        result = scale_times(source, ratio)
        assert result["fr"] == source["fr"] and texts(result) == texts(source)
        assert abs(result["op"] / source["op"] - ratio) < 1e-6
        path = EPISODE / "public/lottie" / f"{scene}.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        records.append({"id": scene, "file": str(path.relative_to(ROOT)), "license": "Original",
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "time_scale": ratio,
                        "source_speech_s": pt[scene], "english_speech_s": en[scene],
                        "usage_notes": "Original C diagram with English text; "
                        "only timeline scaled to voice."})
        print(f"{scene}: {ratio:.3f} ×; {result['op'] / result['fr']:.2f} s de animação")
    (BASE / "licencas.render.en.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
