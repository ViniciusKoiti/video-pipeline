"""Celular com notificações em Lottie, desenho original só com formas geométricas e texto (série Kafka).

Sem expressões, sem imagem externa: o kit recusa expressões (LOTTIE_EXPRESSIONS). O texto usa Noto Sans,
como as animações do consistent hashing. Uso: importado por `gerar.py` desta pasta.
"""

import json
import math

FPS = 30
W, H = 1000, 1000
WHITE, MUTED, GOLD, BLUE = "EDEDE8", "9AA4B2", "F2B134", "69C9F1"
GREEN, CORAL, VIOLET = "8FD694", "FF8C86", "C79BF2"
BODY, SCREEN, CARD, EDGE = "0E1218", "18202A", "232D3A", "3A4757"
EASE_OUT = ({"x": 0.25, "y": 0.1}, {"x": 0.25, "y": 1})


def rgb(color):
    return [int(color[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def fixed(value):
    return {"a": 0, "k": value}


def frame(seconds):
    return round(seconds * FPS)


def keys(steps, dims):
    """steps: [(segundo, valor)] com suavização; dims=1 para opacidade/rotação."""
    out = []
    for i, (at, value) in enumerate(steps):
        key = {"t": frame(at), "s": value if isinstance(value, list) else [value]}
        if i < len(steps) - 1:
            if dims == 1:
                key.update(o={"x": [0.25], "y": [0.1]}, i={"x": [0.25], "y": [1]})
            else:
                key.update(o=EASE_OUT[0], i=EASE_OUT[1])
        out.append(key)
    return {"a": 1, "k": out}


def transform(x=0, y=0):
    return {
        "o": fixed(100),
        "r": fixed(0),
        "p": fixed([x, y, 0]),
        "a": fixed([0, 0, 0]),
        "s": fixed([100, 100, 100]),
    }


class Scene:
    """Camadas de uma animação; a primeira acrescentada fica por baixo."""

    def __init__(self, seconds, ready, name):
        self.layers, self.seconds, self.ready, self.name = [], seconds, ready, name

    def layer(self, name, kind, start, end, x=0, y=0, **data):
        item = {
            "ddd": 0,
            "ind": len(self.layers) + 1,
            "ty": kind,
            "nm": name,
            "sr": 1,
            "ks": transform(x, y),
            "ip": frame(start),
            "op": frame(min(end, self.seconds)),
            "st": 0,
            "bm": 0,
            **data,
        }
        self.layers.append(item)
        return item

    def shape(self, name, shapes, start, end, x=0, y=0):
        return self.layer(name, 4, start, end, x, y, shapes=shapes)

    def text(self, value, x, y, size, color, start, end, justify=0):
        """justify: 0 esquerda, 1 direita, 2 centro (âncora no x)."""
        style = {
            "s": size,
            "f": "NotoSans-Regular",
            "t": value,
            "j": justify,
            "tr": 0,
            "lh": size * 1.2,
            "ls": 0,
            "fc": rgb(color),
        }
        doc = {"d": {"k": [{"s": style, "t": 0}]}, "p": {}, "m": {"g": 1, "a": fixed([0, 0])}, "a": []}
        return self.layer(value, 5, start, end, x, y + size * 0.35, t=doc)

    def finish(self):
        data = {
            "v": "5.12.2",
            "fr": FPS,
            "ip": 0,
            "op": frame(self.seconds),
            "w": W,
            "h": H,
            "nm": self.name,
            "ddd": 0,
            "assets": [],
            "fonts": {
                "list": [
                    {"fName": "NotoSans-Regular", "fFamily": "Noto Sans", "fStyle": "Regular", "ascent": 80}
                ]
            },
            "layers": list(reversed(self.layers)),
            "markers": [{"tm": frame(self.ready), "cm": "ready", "dr": 0}],
        }
        for item in data["layers"]:
            assert item["ip"] < item["op"], item["nm"]
        assert self.ready < self.seconds
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        assert '"x":"' not in text  # sem expressões
        return text


def rect(width, height, radius, fill=None, stroke=None, stroke_width=4):
    shapes = [{"ty": "rc", "d": 1, "s": fixed([width, height]), "p": fixed([0, 0]), "r": fixed(radius)}]
    if fill:
        shapes.append(
            {"ty": "fl", "c": fill if isinstance(fill, dict) else fixed(rgb(fill)), "o": fixed(100), "r": 1}
        )
    if stroke:
        shapes.append(
            {
                "ty": "st",
                "c": stroke if isinstance(stroke, dict) else fixed(rgb(stroke)),
                "o": fixed(100),
                "w": fixed(stroke_width),
                "lc": 2,
                "lj": 2,
            }
        )
    return shapes


def color_keys(steps):
    """steps: [(segundo, cor)] em degrau; a primeira vale desde o início."""
    out = [{"t": frame(at), "s": [*rgb(color), 1], "h": 1} for at, color in steps]
    return {"a": 1, "k": out} if len(out) > 1 else fixed([*rgb(steps[0][1]), 1])


def path(points, closed=False):
    zeros = [[0, 0] for _ in points]
    return {"ty": "sh", "ks": fixed({"i": zeros, "o": zeros, "v": points, "c": closed})}


def stroke(color, width=7):
    return {"ty": "st", "c": fixed(rgb(color)), "o": fixed(100), "w": fixed(width), "lc": 2, "lj": 2}


PHONE_X, PHONE_W, PHONE_H = W / 2, 880, 1500
PHONE_TOP = 120  # o aparelho passa da borda de baixo: close na tela
PHONE_Y = PHONE_TOP + PHONE_H / 2
SLOT_TOP, SLOT_GAP, CARD_W, CARD_H = 420, 160, 790, 140
ICON = 1.3  # escala dos ícones


def phone(scene, header, start=0.0):
    """O aparelho: corpo, tela, câmera, hora e um título acima (o título é a capa)."""
    end = scene.seconds
    scene.text(header, W / 2, 50, 46, MUTED, start, end, justify=2)
    scene.shape("corpo", rect(PHONE_W, PHONE_H, 110, BODY, EDGE, 8), start, end, PHONE_X, PHONE_Y)
    scene.shape("tela", rect(PHONE_W - 50, PHONE_H - 50, 86, SCREEN), start, end, PHONE_X, PHONE_Y)
    scene.shape("camera", rect(170, 42, 21, BODY), start, end, PHONE_X, PHONE_TOP + 58)
    scene.text("12:04", PHONE_X, 215, 96, WHITE, start, end, justify=2)
    scene.text("sexta-feira, almoço", PHONE_X, 300, 36, MUTED, start, end, justify=2)


def icon(scene, kind, x, y, color, start, end, spin_from=None):
    """Ícone redondo da notificação: check, bike, alerta ou um spinner girando."""
    first = len(scene.layers)
    _icon(scene, kind, x, y, color, start, end, spin_from)
    for item in scene.layers[first:]:
        item["ks"]["s"] = fixed([100 * ICON, 100 * ICON, 100])


def _icon(scene, kind, x, y, color, start, end, spin_from=None):
    scene.shape(
        "icone-fundo",
        [
            {"ty": "el", "s": fixed([64, 64]), "p": fixed([0, 0])},
            {"ty": "fl", "c": fixed(rgb(color)), "o": fixed(100), "r": 1},
        ],
        start,
        end,
        x,
        y,
    )
    if kind == "check":
        scene.shape("check", [path([[-14, 1], [-4, 11], [15, -10]]), stroke(BODY, 8)], start, end, x, y)
    elif kind == "alerta":
        scene.shape("alerta", [path([[0, -16], [0, 4]]), stroke(BODY, 8)], start, end, x, y)
        scene.shape(
            "alerta-ponto",
            [
                {"ty": "el", "s": fixed([9, 9]), "p": fixed([0, 15])},
                {"ty": "fl", "c": fixed(rgb(BODY)), "o": fixed(100), "r": 1},
            ],
            start,
            end,
            x,
            y,
        )
    elif kind == "bike":
        for cx in (-12, 12):
            scene.shape(
                "roda",
                [{"ty": "el", "s": fixed([16, 16]), "p": fixed([cx, 7])}, stroke(BODY, 5)],
                start,
                end,
                x,
                y,
            )
        scene.shape("quadro", [path([[-12, 7], [-2, -9], [12, 7]]), stroke(BODY, 5)], start, end, x, y)
    elif kind == "spinner":
        layer = scene.shape(
            "spinner",
            [
                {"ty": "el", "s": fixed([34, 34]), "p": fixed([0, 0])},
                {"ty": "tm", "s": fixed(0), "e": fixed(70), "o": fixed(0), "m": 1},
                stroke(BODY, 6),
            ],
            start,
            end,
            x,
            y,
        )
        turns = max(1, math.ceil((end - (spin_from or start)) / 0.9))
        layer["ks"]["r"] = {
            "a": 1,
            "k": [
                {"t": frame(spin_from or start), "s": [0]},
                {"t": frame((spin_from or start) + turns * 0.9), "s": [360 * turns]},
            ],
        }


def notification(scene, slot, title, body, kind, color, at, end=None, alert_at=None):
    """Cartão que desce e aparece em `at`; com `alert_at`, a borda fica coral e o ícone vira alerta."""
    end = end or scene.seconds
    y = SLOT_TOP + slot * SLOT_GAP
    border = color_keys([(0, EDGE)] + ([(alert_at, CORAL)] if alert_at else []))
    start_index = len(scene.layers)
    scene.shape("cartao", rect(CARD_W, CARD_H, 30, CARD, border, 4), at, end, PHONE_X, y)
    icon_x = PHONE_X - CARD_W / 2 + 76
    if alert_at:
        icon(scene, kind, icon_x, y, color, at, alert_at, spin_from=at)
        icon(scene, "alerta", icon_x, y, CORAL, alert_at, end)
    else:
        icon(scene, kind, icon_x, y, color, at, end, spin_from=at)
    text_x = icon_x + 70
    scene.text(title, text_x, y - 26, 44, WHITE, at, end)
    scene.text(body, text_x, y + 28, 34, MUTED, at, end)
    if at <= 0:  # já está na tela no quadro 0 (capa)
        return
    for item in scene.layers[start_index:]:  # todas as camadas do cartão descem juntas e acendem
        x0, y0 = item["ks"]["p"]["k"][:2]
        item["ks"]["p"] = keys([(at, [x0, y0 - 46, 0]), (at + 0.35, [x0, y0, 0])], 2)
        item["ks"]["o"] = keys([(at, 0), (at + 0.3, 100)], 1)
