"""Animações originais do contador em C; JSON Lottie, sem expressões ou dependências."""

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
EPISODE = ROOT / "data/episodes/short-concorrencia-fluxo-pt"
FPS = 30
WHITE = "EDEDE8"
MUTED = "9AA4B2"
GOLD = "F2B134"
BLUE = "69C9F1"
RED = "FF8C86"
PANEL = "1A222D"
EDGE = "536171"


def rgb(color):
    return [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def fixed(value):
    return {"a": 0, "k": value}


def transform(x=0, y=0):
    return {"o": fixed(100), "r": fixed(0), "p": fixed([x, y, 0]),
            "a": fixed([0, 0, 0]), "s": fixed([100, 100, 100])}


def layer(layers, name, kind, start=0, end=12, x=0, y=0, **data):
    item = {"ddd": 0, "ind": len(layers) + 1, "ty": kind, "nm": name,
            "sr": 1, "ks": transform(x, y), "ip": round(start * FPS),
            "op": round(end * FPS), "st": 0, "bm": 0, **data}
    layers.append(item)
    return item


def text(layers, value, x, y, size=44, color=WHITE, start=0, end=12):
    style = {"s": size, "f": "NotoSans-Regular", "t": value, "j": 2,
             "tr": 0, "lh": size * 1.2, "ls": 0, "fc": rgb(color)}
    return layer(layers, value, 5, start, end, x, y + size * 0.35,
                 t={"d": {"k": [{"s": style, "t": 0}]}, "p": {},
                    "m": {"g": 1, "a": fixed([0, 0])}, "a": []})


def box(layers, x, y, width, height, color=EDGE, start=0, end=12, fill=True):
    shapes = [{"ty": "rc", "d": 1, "s": fixed([width, height]),
               "p": fixed([0, 0]), "r": fixed(20)}]
    if fill:
        shapes.append({"ty": "fl", "c": fixed(rgb(PANEL)), "o": fixed(100), "r": 1})
    shapes.append({"ty": "st", "c": fixed(rgb(color)), "o": fixed(100),
                   "w": fixed(5), "lc": 2, "lj": 2})
    return layer(layers, "caixa", 4, start, end, x, y, shapes=shapes)


def path_shape(points, closed=False):
    return {"ty": "sh", "ks": fixed({"i": [[0, 0] for _ in points],
            "o": [[0, 0] for _ in points], "v": points, "c": closed})}


def arrow(layers, points, color=EDGE, start=0, end=12):
    stroke = {"ty": "st", "c": fixed(rgb(color)), "o": fixed(100),
              "w": fixed(5), "lc": 2, "lj": 2}
    layer(layers, "conexão", 4, start, end, shapes=[path_shape(points), stroke])
    a, b = points[-2:]
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    head = [b, *[[b[0] - 17 * math.cos(angle + delta),
                  b[1] - 17 * math.sin(angle + delta)] for delta in (-0.5, 0.5)]]
    layer(layers, "seta", 4, start, end,
          shapes=[path_shape(head, True), {"ty": "fl", "c": fixed(rgb(color)),
                                         "o": fixed(100), "r": 1}])


def pulse(layers, points, start, end, color):
    distances = [math.dist(a, b) for a, b in zip(points, points[1:], strict=False)]
    total = sum(distances)
    assert start < end and total > 0
    elapsed = 0.0
    keys = []
    for i, point in enumerate(points):
        at = start + (end - start) * elapsed / total
        key = {"t": round(at * FPS, 3), "s": [*point, 0]}
        if i < len(points) - 1:
            key.update(e=[*points[i + 1], 0], o={"x": 0.333, "y": 0.333},
                       i={"x": 0.667, "y": 0.667})
            elapsed += distances[i]
        keys.append(key)
    assert keys[0]["t"] == round(start * FPS, 3)
    assert keys[-1]["t"] == round(end * FPS, 3)
    assert all(a["t"] < b["t"] for a, b in zip(keys, keys[1:], strict=False))
    dot = layer(layers, "valor em trânsito", 4, start, end,
                shapes=[{"ty": "el", "s": fixed([24, 24]), "p": fixed([0, 0])},
                        {"ty": "fl", "c": fixed(rgb(color)), "o": fixed(100), "r": 1}])
    dot["ks"]["p"] = {"a": 1, "k": keys}


def states(layers, x, y, entries, size=46, color=WHITE, end=12):
    for i, (at, value) in enumerate(entries):
        until = entries[i + 1][0] if i + 1 < len(entries) else end
        text(layers, value, x, y, size, color, at, until)


def race():
    layers = []
    for x, color in ((250, GOLD), (750, BLUE)):
        arrow(layers, [[500, 290], [500, 340], [x, 340], [x, 415]])
        arrow(layers, [[x, 505], [x, 575]])
        arrow(layers, [[x, 665], [x, 735]])
        side, target = (40, 300) if x == 250 else (960, 700)
        arrow(layers, [[x, 825], [x, 865], [side, 865], [side, 220], [target, 220]])
        for y in (460, 620, 780):
            box(layers, x, y, 320, 90)
        text(layers, "THREAD A" if x == 250 else "THREAD B", x, 380, 38, color)
    box(layers, 500, 220, 400, 140)
    text(layers, "C · sem proteção", 500, 48, 48, GOLD)
    text(layers, "Exemplo didático", 500, 102, 30, MUTED)
    text(layers, "contador compartilhado", 500, 185, 30, MUTED)
    states(layers, 500, 244, [(0, "10"), (5.8, "11")], 76)
    for x, read_at, sum_at, write_at, color in ((250, 3.3, 4.4, 5.0, GOLD),
                                               (750, 3.9, 4.9, 6.1, BLUE)):
        states(layers, x, 460, [(0, "LER"), (read_at + 0.45, "lê 10")])
        states(layers, x, 620, [(0, "SOMAR"), (sum_at, "10 + 1 = 11")], 42)
        states(layers, x, 780, [(0, "GRAVAR"), (write_at, "grava 11")])
        pulse(layers, [[500, 290], [500, 340], [x, 340], [x, 415]], read_at, read_at + 0.45, color)
        pulse(layers, [[x, 505], [x, 575]], sum_at - 0.3, sum_at, color)
        pulse(layers, [[x, 665], [x, 735]], write_at - 0.3, write_at, color)
        side, target = (40, 300) if x == 250 else (960, 700)
        pulse(layers, [[x, 825], [x, 865], [side, 865], [side, 220], [target, 220]],
              write_at, write_at + 0.8, color)
        box(layers, 500, 220, 400, 140, color if x == 250 else RED,
            write_at + 0.7, write_at + 1.0, False)
    text(layers, "11, e não 12: uma soma perdida", 500, 925, 40, RED, 6.9)
    text(layers, "Em C: comportamento indefinido", 500, 980, 28, MUTED, 9.2)
    return layers, 12, 9.2


def mutex():
    layers = []
    for x in (250, 750):
        arrow(layers, [[x, 280], [x, 355], [500, 355], [500, 420]], end=4)
    arrow(layers, [[500, 630], [500, 745]], end=4)
    for x, label, color in ((250, "THREAD A", GOLD), (750, "THREAD B", BLUE)):
        box(layers, x, 220, 350, 120, color, end=4)
        text(layers, label, x, 220, 40, color, end=4)
    box(layers, 500, 525, 650, 210, end=4)
    box(layers, 500, 800, 500, 110, end=4)
    text(layers, "C · com mutex", 500, 55, 48, GOLD, end=4)
    text(layers, "lock → trecho protegido → unlock", 500, 112, 32, MUTED, end=4)
    text(layers, "TRECHO PROTEGIDO", 500, 473, 32, MUTED, end=4)
    states(layers, 500, 550, [(0, "A entra"), (2.3, "B entra")], 58, end=4)
    text(layers, "B espera a mesma trava", 500, 685, 36, BLUE, 0.65, 2.0)
    text(layers, "destrava", 500, 800, 44, end=4)
    box(layers, 500, 525, 650, 210, GOLD, 0.4, 2.0, False)
    box(layers, 500, 525, 650, 210, BLUE, 2.3, 4, False)
    pulse(layers, [[250, 280], [250, 355], [500, 355], [500, 420]], 0.1, 0.4, GOLD)
    pulse(layers, [[750, 280], [750, 355]], 0.5, 0.8, BLUE)
    pulse(layers, [[500, 630], [500, 745]], 1.5, 2.0, GOLD)
    pulse(layers, [[750, 355], [500, 355], [500, 420]], 2.0, 2.3, BLUE)
    text(layers, "Um thread por vez nesse trecho", 500, 935, 40, GOLD, 2.8, 4)
    return layers, 3.8, 2.8


def atomic():
    layers = []
    for x in (250, 750):
        arrow(layers, [[x, 280], [x, 340], [500, 340], [500, 410]], end=8)
    arrow(layers, [[500, 650], [500, 745]], end=8)
    for x, label, color in ((250, "THREAD A", GOLD), (750, "THREAD B", BLUE)):
        box(layers, x, 220, 350, 120, color, end=8)
        text(layers, label, x, 220, 40, color, end=8)
    box(layers, 500, 530, 920, 240, end=8)
    text(layers, "C · atomic_fetch_add", 500, 55, 48, GOLD, end=8)
    text(layers, "UMA OPERAÇÃO INDIVISÍVEL", 500, 454, 34, GOLD, end=8)
    for x, label in ((220, "LER"), (500, "SOMAR"), (780, "GRAVAR")):
        box(layers, x, 550, 250, 105, end=8)
        text(layers, label, x, 550, 36, end=8)
    arrow(layers, [[348, 550], [372, 550]], end=8)
    arrow(layers, [[628, 550], [652, 550]], end=8)
    box(layers, 500, 825, 440, 160, end=8)
    text(layers, "contador em C", 500, 784, 30, MUTED, end=8)
    states(layers, 500, 850, [(0, "10"), (2.4, "11"), (4.9, "12")], 76, end=8)
    for x, start, finish, color in ((250, 1.2, 2.4, GOLD), (750, 3.7, 4.9, BLUE)):
        pulse(layers, [[x, 280], [x, 340], [500, 340], [500, 410]], start, start + 0.4, color)
        box(layers, 500, 530, 920, 240, color, start + 0.4, finish, False)
        pulse(layers, [[500, 650], [500, 745]], finish - 0.4, finish, color)
    text(layers, "10 → 11 → 12: cada soma conta", 500, 964, 40, GOLD, 5.2, 8)
    return layers, 7.1, 5.5


def main():
    source = ROOT / "renders/short-concorrencia/explicacao"
    content = json.loads((source / "content.pt.json").read_text())
    narration = json.loads((source / "narracao.pt.json").read_text())
    narration["lines"][0]["text"] = (
        "Em C, dois threads somam um milhão cada. O total deveria dar dois milhões."
    )
    narration["lines"][-1]["text"] = (
        "E em outras linguagens, como isso funciona? Comenta qual linguagem você quer ver no próximo vídeo."
    )
    licenses = []
    for scene_id, make in (("codigo", race), ("mutex", mutex), ("atomic", atomic)):
        layers, seconds, ready = make()
        animation = {"v": "5.12.2", "fr": FPS, "ip": 0, "op": round(seconds * FPS),
                     "w": 1000, "h": 1000, "nm": f"C · {scene_id}", "ddd": 0,
                     "assets": [], "fonts": {"list": [{"fName": "NotoSans-Regular",
                     "fFamily": "Noto Sans", "fStyle": "Regular", "ascent": 80}]},
                     "layers": list(reversed(layers)),
                     "markers": [{"tm": round(ready * FPS), "cm": "ready", "dr": 0}]}
        for item in animation["layers"]:
            item["op"] = min(item["op"], animation["op"])
            assert item["ip"] < item["op"]
        assert ready < seconds and animation["assets"] == []
        data = json.dumps(animation, ensure_ascii=False, separators=(",", ":")) + "\n"
        assert '"x":"' not in data  # sem expressões JavaScript
        relative = f"lottie/{scene_id}.json"
        for directory in (BASE, EPISODE):
            file = directory / "public" / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(data, encoding="utf-8")
        content["assets"][scene_id] = {"kind": "lottie", "path": relative}
        scene = next(s for s in content["scenes"] if s["id"] == scene_id)
        scene.clear()
        duration = {"codigo": 12.4, "mutex": 4, "atomic": 7.9}[scene_id]
        scene.update(id=scene_id, type="animation", durationSec=duration,
                     assetId=scene_id, colors="original")
        licenses.append({"id": scene_id, "file": f"public/{relative}", "license": "Original",
                         "sha256": hashlib.sha256(data.encode()).hexdigest(),
                         "usage_notes": "Gráfico vetorial original gerado a pedido do dono; "
                         "exemplo didático de C, sem mídia externa."})
    for scene in content["scenes"]:
        if scene["id"] == "gancho":
            scene["kicker"] = "C · concorrência"
            scene["text"] = "Em C: 2 threads. 1 contador. Deveria dar 2.000.000."
        elif scene["id"] == "fecho":
            scene["text"] = "E em outras linguagens?"
            scene["sub"] = "Comenta qual você quer ver"
    for name, data in (("content", content), ("narracao", narration)):
        for directory, filename in ((BASE, f"{name}.pt.json"), (EPISODE, f"{name}.json")):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    (BASE / "licencas.json").write_text(json.dumps(licenses, ensure_ascii=False, indent=2) + "\n")
    assert 10 + 1 == 11 and 10 + 1 + 1 == 12
    assert [s["id"] for s in content["scenes"]] == [s["scene"] for s in narration["lines"]]
    print("3 animações Lottie originais; fonte Noto Sans local; sem expressões ou arquivos externos.")


if __name__ == "__main__":
    main()
