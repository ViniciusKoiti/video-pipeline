"""Recorta personagens de anime: tira o fundo e guarda só a maior figura.

Uso (no ambiente do rembg, ver SKILL.md):
    ~/.local/share/rembg-env/bin/python -I recortar.py <quadro.jpg> <saida.png> [--apagar-escuro X0,Y0,X1,Y1]

`--apagar-escuro` apaga, dentro do retângulo, os pixels quase pretos que ficaram grudados na figura
(por exemplo, um pedaço de outro personagem). Depois da limpeza, só a maior figura fica.
"""

import argparse

import numpy as np
from PIL import Image
from rembg import new_session, remove
from scipy import ndimage


def maior_figura(rgba: np.ndarray) -> np.ndarray:
    rotulos, n = ndimage.label(rgba[..., 3] > 20)
    if n == 0:
        return rgba
    tamanhos = ndimage.sum(np.ones_like(rotulos), rotulos, range(1, n + 1))
    maior = 1 + int(np.argmax(tamanhos))
    rgba[..., 3] = np.where(rotulos == maior, rgba[..., 3], 0)
    return rgba


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("quadro")
    ap.add_argument("saida")
    ap.add_argument("--apagar-escuro", help="X0,Y0,X1,Y1 em pixels do quadro")
    ap.add_argument("--limite-escuro", type=int, default=95)
    a = ap.parse_args()

    quadro = Image.open(a.quadro).convert("RGB")
    recorte = remove(quadro, session=new_session("isnet-anime"), post_process_mask=True)
    rgba = np.array(recorte.convert("RGBA"))
    if a.apagar_escuro:
        x0, y0, x1, y1 = (int(v) for v in a.apagar_escuro.split(","))
        h, w = rgba.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        dentro = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        escuro = rgba[..., :3].max(axis=2) < a.limite_escuro
        rgba[..., 3] = np.where(dentro & escuro, 0, rgba[..., 3])
    rgba = maior_figura(rgba)
    Image.fromarray(rgba).save(a.saida)

    # Conferência: a figura sobre verde, para ver bordas e restos.
    verde = Image.new("RGBA", recorte.size, (0, 170, 0, 255))
    verde.alpha_composite(Image.fromarray(rgba))
    conferencia = a.saida.rsplit(".", 1)[0] + "-conferencia.jpg"
    verde.convert("RGB").save(conferencia, quality=85)
    ys, xs = np.nonzero(rgba[..., 3] > 20)
    print(f"{a.saida}: figura x {xs.min()}–{xs.max()}, y {ys.min()}–{ys.max()}; conferência em {conferencia}")


if __name__ == "__main__":
    main()
