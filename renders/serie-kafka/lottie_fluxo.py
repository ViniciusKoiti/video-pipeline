"""Fila e log em Lottie, grandes no vertical (série Kafka): desenho original, formas geométricas e texto.

`fila()`: mensagens num tubo; o consumidor pega a da frente e ela some (ler é apagar).
`log()`: fita vertical de mensagens numeradas pelo offset; ponteiros nomeados descem, voltam e releem.
Tempos em segundos desde o início da cena, alinhados à fala gravada. Sem expressões.
"""

import lottie_celular as cel
from lottie_celular import CARD, CORAL, EDGE, GOLD, GREEN, MUTED, SCREEN, WHITE, fixed, frame, rect

ITEM, MOVE = 150, 0.35
TITLE = 60  # tamanho do título dentro da animação


def track(steps):
    """steps: [(segundo, [x, y])] em ordem; descarta quadros repetidos e devolve a propriedade animada."""
    clean = []
    for at, (x, y) in steps:
        if clean and frame(at) <= frame(clean[-1][0]):
            continue
        clean.append((at, [x, y, 0]))
    return cel.keys(clean, 2) if len(clean) > 1 else fixed(clean[0][1])


def fade(steps):
    clean = []
    for at, value in steps:
        if clean and frame(at) <= frame(clean[-1][0]):
            continue
        clean.append((at, value))
    return cel.keys(clean, 1) if len(clean) > 1 else fixed(clean[0][1])


def group(scene, start_index, path, opacity=None):
    """Move juntas as camadas criadas desde start_index, mantendo o deslocamento de cada uma."""
    x0, y0 = path[0][1]
    for item in scene.layers[start_index:]:
        lx, ly = item["ks"]["p"]["k"][:2]
        dx, dy = lx - x0, ly - y0
        item["ks"]["p"] = track([(t, [x + dx, y + dy]) for t, (x, y) in path])
        if opacity is not None:
            item["ks"]["o"] = fade(opacity)


def text_steps(scene, steps, x, y, size, color, start, end, justify=2):
    """Texto que troca no tempo: steps [(segundo, texto)]."""

    def style(value):
        return {
            "s": size,
            "f": "NotoSans-Regular",
            "t": value,
            "j": justify,
            "tr": 0,
            "lh": size * 1.2,
            "ls": 0,
            "fc": cel.rgb(color),
        }

    doc = {
        "d": {"k": [{"s": style(v), "t": frame(t)} for t, v in steps]},
        "p": {},
        "m": {"g": 1, "a": fixed([0, 0])},
        "a": [],
    }
    return scene.layer(steps[0][1], 5, start, end, x, y + size * 0.35, t=doc)


def fila(
    name,
    seconds,
    ready,
    title,
    queue_label,
    queue_sub,
    consumers,
    item_label,
    caption,
    caption_at,
    t0=0.6,
    period=1.1,
    header=None,
):
    """Tubo com 3 lugares; a cada `period` o da frente vai a um consumidor, é processado e some.

    Um consumidor: o nome fica no alto da caixa e a mensagem pousa embaixo. Vários: `header` acima da coluna,
    um rótulo curto (número) à esquerda de cada caixa e a mensagem pousa à direita, sem cobrir o texto.
    """
    s = cel.Scene(seconds, ready, name)
    end = s.seconds
    s.text(title, cel.W / 2, 70, TITLE, WHITE, 0, end, justify=2)
    tube_y, slots, hidden_x = 500, [520, 345, 170], -10
    cx = 835
    s.text(queue_label, 40, 300, 54, WHITE, 0, end)
    s.text(queue_sub, 40, 362, 38, MUTED, 0, end)
    s.shape("tubo", rect(610, 220, 44, SCREEN, EDGE, 6), 0, end, 330, tube_y)
    ys = [tube_y] if len(consumers) == 1 else [tube_y - 190 + 190 * i for i in range(len(consumers))]
    height = 250 if len(consumers) == 1 else 160
    cycles = max(1, int((seconds - t0 - 1.0) / period) + 1)
    busy = {i: [] for i in range(len(consumers))}
    for k in range(cycles):
        busy[k % len(consumers)].append(t0 + k * period + MOVE)
    for i, (label, y) in enumerate(zip(consumers, ys, strict=True)):
        steps = [(0, EDGE)]
        for at in busy[i]:
            steps += [(at, GOLD), (at + 0.32, EDGE)]
        s.shape("consumidor", rect(290, height, 34, CARD, cel.color_keys(steps), 7), 0, end, cx, y)
        if len(consumers) == 1:
            s.text(label, cx, y - 88, 40, WHITE, 0, end, justify=2)
        else:
            s.text(label, cx - 100, y, 50, MUTED, 0, end, justify=2)
    if header:
        s.text(header, cx, ys[0] - 128, 44, WHITE, 0, end, justify=2)
    land_x, land_dy = (cx, 38) if len(consumers) == 1 else (cx + 50, 0)
    n = len(slots)
    for i in range(cycles + n):
        q0 = min(i, n)
        start_x = slots[q0] if q0 < n else hidden_x
        first = len(s.layers)
        s.shape("mensagem", rect(ITEM, ITEM, 30, CARD, GOLD, 6), 0, end, start_x, tube_y)
        s.text(item_label(i), start_x, tube_y, 46, WHITE, 0, end, justify=2)
        path, opacity = [(0, [start_x, tube_y])], [(0, 100 if i < n else 0)]
        for k in range(min(i, cycles)):  # cada mensagem que sai empurra esta um lugar para a frente
            at = t0 + k * period + 0.2
            q = i - k
            if q > n:
                continue
            src = slots[q] if q < n else hidden_x
            path += [(at, [src, tube_y]), (at + MOVE, [slots[q - 1], tube_y])]
            if q == n:
                opacity += [(at, 0), (at + MOVE, 100)]
        if i < cycles:
            at = t0 + i * period
            target_y = ys[i % len(consumers)] + land_dy
            path += [
                (at, [slots[0], tube_y]),
                (at + MOVE, [land_x, target_y]),
                (at + 0.65, [land_x, target_y]),
                (at + 1.0, [land_x, target_y + 140]),
            ]
            opacity += [(at + 0.65, 100), (at + 1.0, 0)]
        group(s, first, path, opacity)
    s.text(caption, cel.W / 2, 880, 58, CORAL, caption_at, end, justify=2)
    return s


ROW_Y0, ROW_GAP, CELL_W, CELL_H = 205, 118, 430, 98
CELL_L, CELL_R = cel.W / 2 - CELL_W / 2, cel.W / 2 + CELL_W / 2


def row_y(row):
    return ROW_Y0 + row * ROW_GAP


def log(name, seconds, ready, title, times, pointers, caption, caption_at, marks=()):
    """Fita de mensagens (offset e horário) que não some; ponteiros com nome e o offset da próxima leitura.

    pointers: [{"label", "color", "side": "right"|"left", "steps": [(segundo, linha)]}]
    marks: [(segundo, primeira_linha, última_linha, cor)] mudam a borda das células (afetadas, relidas).
    """
    s = cel.Scene(seconds, ready, name)
    end = s.seconds
    s.text(title, cel.W / 2, 70, TITLE, WHITE, 0, end, justify=2)
    for row, hora in enumerate(times):
        steps = [(0, EDGE)]
        for at, first, last, color in sorted(marks):
            if first <= row <= last:
                steps.append((at, color))
        s.shape(
            "celula", rect(CELL_W, CELL_H, 22, CARD, cel.color_keys(steps), 6), 0, end, cel.W / 2, row_y(row)
        )
        s.text(str(row), CELL_L + 62, row_y(row), 54, WHITE, 0, end, justify=2)
        s.text(hora, CELL_R - 34, row_y(row), 38, MUTED, 0, end, justify=1)
    for pointer in pointers:
        right = pointer["side"] == "right"
        tip = CELL_R + 14 if right else CELL_L - 14
        box_x = tip + 135 if right else tip - 135
        rows = pointer["steps"]
        first_row = rows[0][1]
        first = len(s.layers)
        head = [
            [tip, row_y(first_row)],
            [tip + (32 if right else -32), row_y(first_row) - 22],
            [tip + (32 if right else -32), row_y(first_row) + 22],
        ]
        s.shape(
            "seta",
            [
                cel.path(head, True),
                {"ty": "fl", "c": fixed(cel.rgb(pointer["color"])), "o": fixed(100), "r": 1},
            ],
            0,
            end,
        )
        s.shape("rotulo", rect(212, 92, 22, SCREEN, pointer["color"], 5), 0, end, box_x, row_y(first_row))
        s.text(pointer["label"], box_x, row_y(first_row) - 19, 32, pointer["color"], 0, end, justify=2)
        text_steps(
            s,
            [(0, f"offset {first_row}")] + [(t, f"offset {r}") for t, r in rows[1:]],
            box_x,
            row_y(first_row) + 23,
            28,
            MUTED,
            0,
            end,
        )
        path, previous = [(0, [box_x, row_y(first_row)])], first_row
        for at, r in rows[1:]:
            path += [(at, [box_x, row_y(previous)]), (at + MOVE, [box_x, row_y(r)])]
            previous = r
        for item in s.layers[first:]:  # a seta é um caminho absoluto: move pelo deslocamento
            if item["nm"] == "seta":
                item["ks"]["p"] = track([(t, [x - box_x, y - row_y(first_row)]) for t, (x, y) in path])
        group_offsets(s, first, path)
    s.text(caption, cel.W / 2, 930, 54, GOLD, caption_at, end, justify=2)
    return s


def group_offsets(scene, start_index, path):
    """Como `group`, mas sem tocar na seta (já animada) e sem opacidade."""
    x0, y0 = path[0][1]
    for item in scene.layers[start_index:]:
        if item["nm"] == "seta":
            continue
        lx, ly = item["ks"]["p"]["k"][:2]
        dx, dy = lx - x0, ly - y0
        item["ks"]["p"] = track([(t, [x + dx, y + dy]) for t, (x, y) in path])


__all__ = ["fila", "log", "GREEN", "CORAL", "GOLD"]
