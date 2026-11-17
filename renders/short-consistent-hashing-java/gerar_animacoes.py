"""Consistent hashing em Java: três animações Lottie originais, content e narração (pt e en).

Uso: uv run --no-sync python renders/short-consistent-hashing-java/gerar_animacoes.py
Os tempos (segundos) de cada cena ficam em TEMPOS e são ajustados à voz depois de gerada (plano-animacao.md).
Exemplos didáticos: chaves 0 a 19 (resto por 4 e por 5) e 12 chaves no anel (ângulos fixos).
Nada aqui é medição.
"""

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
EPISODES = [ROOT / f"data/episodes/short-consistent-hashing-java-{x}" for x in ("pt", "en")]
FPS = 30
WHITE, MUTED, GOLD, BLUE = "EDEDE8", "9AA4B2", "F2B134", "69C9F1"
GREEN, VIOLET, CORAL = "8FD694", "C79BF2", "FF8C86"
PANEL, EDGE, DARK = "1A222D", "536171", "11161D"
SERVERS = [GOLD, BLUE, GREEN, VIOLET, CORAL]  # S1..S5 (S5 é o servidor novo)

# Durações (s) de cada cena do vídeo e momento "ready" de cada animação; refeitas depois da voz.
TEMPOS = {
    "situacao": {"scene": 3.2, "anim": 3.2, "ready": 2.0},
    "pergunta": {"scene": 2.6},
    "modulo": {"scene": 8.6, "anim": 8.6, "ready": 6.9},
    "medicao-modulo": {"scene": 4.6},
    "anel": {"scene": 8.4, "anim": 8.4, "ready": 6.6},
    "comparacao": {"scene": 7.4},
    "pontos": {"scene": 7.0},
    "fecho": {"scene": 3.6},
}
# Quando cada coisa acontece dentro da animação (segundos); ajustados aos trechos falados.
EVENTOS = {
    "abertura": {"novo": 0.7, "troca": 1.3, "texto": 1.8},
    "modulo": {"n5": 4.6, "troca": 5.2, "texto": 6.3},
    "anel": {"pulso": 1.0, "novo": 3.4, "arco": 4.4, "troca": 5.0, "texto": 6.0},
}


def rgb(color):
    return [int(color[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def fixed(value):
    return {"a": 0, "k": value}


def transform(x=0, y=0):
    return {
        "o": fixed(100),
        "r": fixed(0),
        "p": fixed([x, y, 0]),
        "a": fixed([0, 0, 0]),
        "s": fixed([100, 100, 100]),
    }


def layer(layers, name, kind, start, end, x=0, y=0, **data):
    item = {
        "ddd": 0,
        "ind": len(layers) + 1,
        "ty": kind,
        "nm": name,
        "sr": 1,
        "ks": transform(x, y),
        "ip": round(start * FPS),
        "op": round(end * FPS),
        "st": 0,
        "bm": 0,
        **data,
    }
    layers.append(item)
    return item


def text(layers, value, x, y, size, color, start, end):
    style = {
        "s": size,
        "f": "NotoSans-Regular",
        "t": value,
        "j": 2,
        "tr": 0,
        "lh": size * 1.2,
        "ls": 0,
        "fc": rgb(color),
    }
    return layer(
        layers,
        value,
        5,
        start,
        end,
        x,
        y + size * 0.35,
        t={"d": {"k": [{"s": style, "t": 0}]}, "p": {}, "m": {"g": 1, "a": fixed([0, 0])}, "a": []},
    )


def color_keys(steps):
    """steps: [(segundo, cor)] em hold; a primeira entrada vale desde o início."""
    keys = [{"t": round(at * FPS), "s": [*rgb(color), 1], "h": 1} for at, color in steps]
    return {"a": 1, "k": keys} if len(keys) > 1 else fixed([*rgb(steps[0][1]), 1])


def disc(layers, x, y, size, steps, start, end):
    shapes = [
        {"ty": "el", "s": fixed([size, size]), "p": fixed([0, 0])},
        {"ty": "fl", "c": color_keys(steps), "o": fixed(100), "r": 1},
    ]
    return layer(layers, "disco", 4, start, end, x, y, shapes=shapes)


def box(layers, x, y, width, height, start, end, color=EDGE, fill=True):
    shapes = [{"ty": "rc", "d": 1, "s": fixed([width, height]), "p": fixed([0, 0]), "r": fixed(20)}]
    if fill:
        shapes.append({"ty": "fl", "c": fixed(rgb(PANEL)), "o": fixed(100), "r": 1})
    shapes.append({"ty": "st", "c": fixed(rgb(color)), "o": fixed(100), "w": fixed(5), "lc": 2, "lj": 2})
    return layer(layers, "caixa", 4, start, end, x, y, shapes=shapes)


def path_shape(points, closed=False):
    return {
        "ty": "sh",
        "ks": fixed({"i": [[0, 0] for _ in points], "o": [[0, 0] for _ in points], "v": points, "c": closed}),
    }


def line(layers, points, color, start, end, width=6):
    stroke = {"ty": "st", "c": fixed(rgb(color)), "o": fixed(100), "w": fixed(width), "lc": 2, "lj": 2}
    return layer(layers, "linha", 4, start, end, shapes=[path_shape(points), stroke])


def arrow(layers, points, start, end, color=EDGE):
    line(layers, points, color, start, end, 5)
    a, b = points[-2:]
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    head = [b, *[[b[0] - 17 * math.cos(angle + d), b[1] - 17 * math.sin(angle + d)] for d in (-0.5, 0.5)]]
    layer(
        layers,
        "seta",
        4,
        start,
        end,
        shapes=[path_shape(head, True), {"ty": "fl", "c": fixed(rgb(color)), "o": fixed(100), "r": 1}],
    )


def pulse(layers, points, start, end, color):
    distances = [math.dist(a, b) for a, b in zip(points, points[1:], strict=False)]
    total = sum(distances)
    assert start < end and total > 0
    elapsed, keys = 0.0, []
    for i, point in enumerate(points):
        key = {"t": round((start + (end - start) * elapsed / total) * FPS, 3), "s": [*point, 0]}
        if i < len(points) - 1:
            key.update(e=[*points[i + 1], 0], o={"x": 0.333, "y": 0.333}, i={"x": 0.667, "y": 0.667})
            elapsed += distances[i]
        keys.append(key)
    assert all(a["t"] < b["t"] for a, b in zip(keys, keys[1:], strict=False))
    dot = layer(
        layers,
        "chave em trânsito",
        4,
        start,
        end,
        shapes=[
            {"ty": "el", "s": fixed([26, 26]), "p": fixed([0, 0])},
            {"ty": "fl", "c": fixed(rgb(color)), "o": fixed(100), "r": 1},
        ],
    )
    dot["ks"]["p"] = {"a": 1, "k": keys}


def finish(layers, seconds, ready, name):
    animation = {
        "v": "5.12.2",
        "fr": FPS,
        "ip": 0,
        "op": round(seconds * FPS),
        "w": 1000,
        "h": 1000,
        "nm": name,
        "ddd": 0,
        "assets": [],
        "fonts": {
            "list": [{"fName": "NotoSans-Regular", "fFamily": "Noto Sans", "fStyle": "Regular", "ascent": 80}]
        },
        "layers": list(reversed(layers)),
        "markers": [{"tm": round(ready * FPS), "cm": "ready", "dr": 0}],
    }
    for item in animation["layers"]:
        item["op"] = min(item["op"], animation["op"])
        assert item["ip"] < item["op"], item["nm"]
    assert ready < seconds
    data = json.dumps(animation, ensure_ascii=False, separators=(",", ":")) + "\n"
    assert '"x":"' not in data  # sem expressões JavaScript
    return data


# ---------------------------------------------------------------- abertura e módulo (chaves 0 a 19)
KEYS = 20


def owner4(k):
    return k % 4


def owner5(k):
    return k % 5


CHANGED = [k for k in range(KEYS) if owner4(k) != owner5(k)]
assert len(CHANGED) == 16  # 16 de 20 trocam: é o que o texto da tela diz


def key_grid(layers, ev_switch, end, with_remainder, ev_n5=None):
    """20 chaves em 2 fileiras de 10; a cor é a do servidor dono (resto por 4, depois por 5)."""
    for k in range(KEYS):
        x = 107 + 86 * (k % 10)
        y = (420 if with_remainder else 470) + 190 * (k // 10)
        steps = [(0, SERVERS[owner4(k)])]
        if owner4(k) != owner5(k):
            steps.append((ev_switch, SERVERS[owner5(k)]))
        disc(layers, x, y, 52, steps, 0, end)
        if with_remainder:
            text(layers, str(owner4(k)), x, y + 52, 34, MUTED, 0, ev_n5)
            text(layers, str(owner5(k)), x, y + 52, 34, WHITE, ev_n5, end)
            text(layers, f"{k}", x, y - 44, 24, MUTED, 0, end)


def abertura():
    t, ev = TEMPOS["situacao"], EVENTOS["abertura"]
    end, layers = t["anim"], []
    text(layers, "Cache de sessões · Java", 500, 55, 44, GOLD, 0, end)
    box(layers, 500, 170, 340, 92, 0, end)
    text(layers, "Aplicação", 500, 170, 40, WHITE, 0, end)
    for i in range(5):
        x = 100 + 200 * i
        start = 0 if i < 4 else ev["novo"]
        arrow(layers, [[500, 216], [500, 250], [x, 250], [x, 300]], start, end)
        box(layers, x, 360, 170, 100, start, end, SERVERS[i])
        text(layers, f"S{i + 1}", x, 360, 44, SERVERS[i], start, end)
    text(layers, "4 servidores", 500, 460, 38, MUTED, 0, ev["novo"])
    text(layers, "+ 1 servidor novo", 500, 460, 38, CORAL, ev["novo"], end)
    key_grid(layers, ev["troca"], end, False)
    text(layers, "cada ponto é uma sessão; a cor é o servidor", 500, 785, 30, MUTED, 0, end)
    text(layers, "16 de 20 sessões trocaram de servidor", 500, 880, 40, CORAL, ev["texto"], end)
    text(layers, "exemplo didático", 500, 940, 28, MUTED, ev["texto"], end)
    return finish(layers, end, t["ready"], "Cache · abertura")


def modulo():
    t, ev = TEMPOS["modulo"], EVENTOS["modulo"]
    end, layers = t["anim"], []
    text(layers, "servidor = hash(chave) % N", 500, 60, 54, GOLD, 0, end)
    text(layers, "N = 4", 500, 150, 60, WHITE, 0, ev["n5"])
    text(layers, "N = 5", 500, 150, 60, CORAL, ev["n5"], end)
    text(layers, "o número embaixo é o resto, ou seja, o servidor", 500, 235, 28, MUTED, 0, end)
    key_grid(layers, ev["troca"], end, True, ev["n5"])
    for i in range(5):
        x = 100 + 200 * i
        start = 0 if i < 4 else ev["n5"]
        box(layers, x, 790, 150, 80, start, end, SERVERS[i])
        text(layers, f"S{i + 1} = {i}", x, 790, 32, SERVERS[i], start, end)
    text(layers, "16 de 20 chaves trocaram de servidor", 500, 905, 42, CORAL, ev["texto"], end)
    text(layers, "exemplo didático: chaves 0 a 19", 500, 960, 28, MUTED, ev["texto"], end)
    return finish(layers, end, t["ready"], "Cache · módulo")


# ---------------------------------------------------------------- anel (12 chaves, ângulos fixos)
CX, CY, R = 500, 500, 330
SERVER_ANGLES = {0: 25, 1: 95, 2: 180, 3: 285}  # S1..S4 (graus, sentido horário a partir do topo)
NEW_ANGLE = 140  # S5, entre S2 (95) e S3 (180)
KEY_ANGLES = [10, 40, 70, 100, 120, 135, 150, 170, 210, 250, 300, 340]


def pos(angle, radius=R):
    rad = math.radians(angle)
    return [round(CX + radius * math.sin(rad), 2), round(CY - radius * math.cos(rad), 2)]


def ring_owner(angle, servers):
    ahead = [(a, s) for s, a in servers.items() if a >= angle]
    return min(ahead)[1] if ahead else min((a, s) for s, a in servers.items())[1]


def arc_points(a0, a1, radius=R, step=3):
    n = max(2, int((a1 - a0) / step) + 1)
    return [pos(a0 + (a1 - a0) * i / (n - 1), radius) for i in range(n)]


OWN_BEFORE = [ring_owner(a, SERVER_ANGLES) for a in KEY_ANGLES]
OWN_AFTER = [ring_owner(a, {**SERVER_ANGLES, 4: NEW_ANGLE}) for a in KEY_ANGLES]
RING_CHANGED = [i for i in range(len(KEY_ANGLES)) if OWN_BEFORE[i] != OWN_AFTER[i]]
assert len(RING_CHANGED) == 3 and all(OWN_AFTER[i] == 4 for i in RING_CHANGED)  # 3 de 12, todas para S5


def anel():
    t, ev = TEMPOS["anel"], EVENTOS["anel"]
    end, layers = t["anim"], []
    text(layers, "o anel de consistent hashing", 500, 45, 44, GOLD, 0, end)
    circle = {"ty": "el", "s": fixed([2 * R, 2 * R]), "p": fixed([0, 0])}
    stroke = {"ty": "st", "c": fixed(rgb(EDGE)), "o": fixed(100), "w": fixed(6), "lc": 2, "lj": 2}
    layer(layers, "anel", 4, 0, end, CX, CY, shapes=[circle, stroke])
    # arco que o servidor novo passa a cobrir: do vizinho anterior (S2) até o novo
    line(layers, arc_points(SERVER_ANGLES[1], NEW_ANGLE), CORAL, ev["arco"], end, 14)
    for i, angle in enumerate(KEY_ANGLES):
        steps = [(0, SERVERS[OWN_BEFORE[i]])]
        if i in RING_CHANGED:
            steps.append((ev["troca"], SERVERS[4]))
        x, y = pos(angle)
        disc(layers, x, y, 30, steps, 0, end)
    for s, angle in SERVER_ANGLES.items():
        x, y = pos(angle)
        disc(layers, x, y, 78, [(0, SERVERS[s])], 0, end)
        text(layers, f"S{s + 1}", x, y, 34, DARK, 0, end)
    x, y = pos(NEW_ANGLE)
    disc(layers, x, y, 78, [(0, SERVERS[4])], ev["novo"], end)
    text(layers, "S5", x, y, 34, DARK, ev["novo"], end)
    # uma chave anda no sentido horário até o primeiro servidor (chave a 70° → S2 a 95°)
    pulse(layers, arc_points(70, SERVER_ANGLES[1], R - 52, 2), ev["pulso"], ev["pulso"] + 1.5, WHITE)
    text(layers, "TreeMap", 500, 455, 46, WHITE, 0, end)
    text(layers, "primeiro servidor no", 500, 515, 32, MUTED, 0, end)
    text(layers, "sentido horário", 500, 560, 32, MUTED, 0, end)
    text(layers, "3 de 12 chaves trocaram, todas para S5", 500, 925, 40, CORAL, ev["texto"], end)
    text(layers, "exemplo didático", 500, 972, 26, MUTED, ev["texto"], end)
    return finish(layers, end, t["ready"], "Cache · anel")


# ---------------------------------------------------------------- narração, conteúdo e saída
NARRACAO = {
    "pt-BR": [
        ("situacao", "Entrou o quinto servidor do cache.", "hook"),
        ("pergunta", "Por que quase toda sessão mudou de lugar?", None),
        ("modulo", "O servidor é o resto do hash por N, e mudando o N, quase toda chave muda.", None),
        ("medicao-modulo", "Em cem mil sessões, oitenta por cento trocaram de servidor.", None),
        (
            "anel",
            "No anel, um TreeMap acha o servidor no sentido horário, e o novo toma só o seu arco.",
            "turn",
        ),
        ("comparacao", "Com cem pontos por servidor, só vinte por cento mudaram, e todas para o novo.", None),
        (
            "pontos",
            "Com um ponto por servidor a carga fica torta, e cem pontos virtuais deixam parelha.",
            None,
        ),
        ("fecho", "Quantos pontos virtuais você usaria por servidor?", "invite"),
    ],
    "en": [
        ("situacao", "A fifth server joined the cache.", "hook"),
        ("pergunta", "Why did almost every session move?", None),
        (
            "modulo",
            "The server is the hash remainder by N, and when N changes, almost every key moves.",
            None,
        ),
        ("medicao-modulo", "Out of a hundred thousand sessions, eighty percent changed servers.", None),
        (
            "anel",
            "On the ring, a TreeMap finds the server clockwise, and the new one takes only its arc.",
            "turn",
        ),
        (
            "comparacao",
            "With a hundred points per server, only about twenty percent moved, all to the new one.",
            None,
        ),
        (
            "pontos",
            "With one point per server the load is lopsided, and a hundred virtual points even it out.",
            None,
        ),
        ("fecho", "How many virtual points per server would you use?", "invite"),
    ],
}

TEXTOS = {
    "pt-BR": {
        "footer": "08/11/2026 · Java 25 · Ryzen 7 5700U · 100 mil sessões · 4 → 5 servidores · 15 rodadas · "
            "só em memória",
        "kicker": "Java · cache de sessões",
        "pergunta": "Por que quase toda sessão mudou de lugar?",
        "destaque": "quase toda sessão",
        "medicao": "% das sessões trocaram de servidor",
        "nota": "simulado · módulo · 100 mil sessões · 4 → 5 servidores",
        "cmp_titulo": "Quem trocou de servidor? (4 → 5)",
        "esq": "Módulo (hash % N)",
        "esq_l": "das sessões trocaram",
        "dir": "Anel, 100 pontos",
        "dir_l": "trocaram, todas para o novo",
        "carga": "Carga do servidor mais cheio, em % da ideal",
        "pontos": ["Anel, 1 ponto", "Anel, 10 pontos", "Anel, 100 pontos"],
        "pontos_d": "Anel, 100 pontos",
        "fecho": "Quantos pontos virtuais por servidor?",
        "sub": "Comenta o seu número",
    },
    "en": {
        "footer": "2026-11-08 · Java 25 · Ryzen 7 5700U · 100k sessions · 4 → 5 servers · 15 runs · in "
            "memory only",
        "kicker": "Java · session cache",
        "pergunta": "Why did almost every session move?",
        "destaque": "almost every session",
        "medicao": "% of sessions changed servers",
        "nota": "simulated · modulo · 100k sessions · 4 → 5 servers",
        "cmp_titulo": "Who changed servers? (4 → 5)",
        "esq": "Modulo (hash % N)",
        "esq_l": "of sessions moved",
        "dir": "Ring, 100 points",
        "dir_l": "moved, all to the new one",
        "carga": "Load of the fullest server, % of ideal",
        "pontos": ["Ring, 1 point", "Ring, 10 points", "Ring, 100 points"],
        "pontos_d": "Ring, 100 points",
        "fecho": "How many virtual points per server?",
        "sub": "Comment your number",
    },
}


def content(locale):
    x, t = TEXTOS[locale], TEMPOS
    seg = {k: v["scene"] for k, v in t.items()}
    return {
        "version": 2,
        "locale": locale,
        "format": "vertical",
        "fps": 30,
        "style": "editorial",
        "safeArea": "shorts",
        "cover": True,
        "footer": x["footer"],
        "assets": {n: {"kind": "lottie", "path": f"lottie/{n}.json"} for n in ("abertura", "modulo", "anel")},
        "scenes": [
            {
                "id": "situacao",
                "type": "animation",
                "durationSec": seg["situacao"],
                "assetId": "abertura",
                "colors": "original",
            },
            {
                "id": "pergunta",
                "type": "hook",
                "durationSec": seg["pergunta"],
                "kicker": x["kicker"],
                "text": x["pergunta"],
                "highlight": x["destaque"],
            },
            {
                "id": "modulo",
                "type": "animation",
                "durationSec": seg["modulo"],
                "assetId": "modulo",
                "colors": "original",
            },
            {
                "id": "medicao-modulo",
                "type": "number",
                "durationSec": seg["medicao-modulo"],
                "value": 80.18,
                "decimals": 2,
                "suffix": "%",
                "label": x["medicao"],
                "note": x["nota"],
            },
            {
                "id": "anel",
                "type": "animation",
                "durationSec": seg["anel"],
                "assetId": "anel",
                "colors": "original",
            },
            {
                "id": "comparacao",
                "type": "versus",
                "durationSec": seg["comparacao"],
                "title": x["cmp_titulo"],
                "left": {
                    "title": x["esq"],
                    "value": "80,18%" if locale == "pt-BR" else "80.18%",
                    "lines": [x["esq_l"]],
                },
                "right": {
                    "title": x["dir"],
                    "value": "20,13%" if locale == "pt-BR" else "20.13%",
                    "lines": [x["dir_l"]],
                },
                "winner": "right",
                "winnerAtSec": 3.0,
            },
            {
                "id": "pontos",
                "type": "categories",
                "durationSec": seg["pontos"],
                "title": x["carga"],
                "unit": "%",
                "decimals": 1,
                "highlight": x["pontos_d"],
                "items": [
                    {"label": label, "value": value}
                    for label, value in zip(x["pontos"], (251.5, 140.2, 111.2), strict=False)
                ],
            },
            {
                "id": "fecho",
                "type": "end_card",
                "durationSec": seg["fecho"],
                "variant": "follow",
                "text": x["fecho"],
                "sub": x["sub"],
            },
        ],
    }


def narracao(locale):
    lines = []
    for scene, text_, delivery in NARRACAO[locale]:
        item = {"scene": scene, "text": text_}
        if delivery:
            item["delivery"] = delivery
        lines.append(item)
    return {"language": locale, "lines": lines}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    licenses = []
    for name, make in (("abertura", abertura), ("modulo", modulo), ("anel", anel)):
        data = make()
        relative = f"lottie/{name}.json"
        for directory in (BASE, *EPISODES):
            file = directory / "public" / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(data, encoding="utf-8")
        licenses.append(
            {
                "id": name,
                "file": f"public/{relative}",
                "license": "Original",
                "sha256": hashlib.sha256(data.encode()).hexdigest(),
                "usage_notes": "Gráfico vetorial original gerado por renders/short-consistent-hashing-java/"
                "gerar_animacoes.py; exemplo didático, sem mídia externa.",
            }
        )
    for locale, episode, suffix in (("pt-BR", EPISODES[0], "pt"), ("en", EPISODES[1], "en")):
        for directory, filename in ((BASE, f"content.{suffix}.json"), (episode, "content.json")):
            write_json(directory / filename, content(locale))
        for directory, filename in ((BASE, f"narracao.{suffix}.json"), (episode, "narracao.json")):
            write_json(directory / filename, narracao(locale))
    write_json(BASE / "licencas.json", licenses)
    ids = [s["scene"] for s in narracao("pt-BR")["lines"]]
    assert ids == [s["id"] for s in content("pt-BR")["scenes"]] == [s[0] for s in NARRACAO["en"]]
    print("3 animações Lottie originais; fonte Noto Sans; sem expressões nem arquivos externos.")


if __name__ == "__main__":
    main()
