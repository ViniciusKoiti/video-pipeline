"""Monta a miniatura em camadas: fundo, palavra atrás, sombra, personagem e contorno da palavra por cima.

Uso (no ambiente do rembg, ver SKILL.md):
    ~/.local/share/rembg-env/bin/python -I compor.py <recorte.png> <saida.jpg> [opções]

Fundo:
    --cor D80000                 vermelho chapado com vinheta (padrão)
    --foto urna.jpg              foto como fundo, preenchendo 1280×720
    --foto-largura 1280 --foto-x 0 --foto-y 80
                                 escala e corte da foto (largura depois de escalar; canto do corte)
    --foto-tom real|vermelho     cores reais ou vermelho monocromático
Personagem:
    --altura 640 --x 0           altura em px e posição horizontal; o pé fica abaixo da borda de baixo
    --cinza                      cinza de mangá com linhas finas (padrão: colorido)
Texto:
    --texto "TERIA VOTOS?" --onde topo|baixo --esticar 1.25
"""

import argparse

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
FONTE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"


def vinheta(img: Image.Image, forca: float) -> Image.Image:
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-300, -300, W + 300, H + 300), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(170))
    return Image.composite(img, ImageEnhance.Brightness(img).enhance(forca), m)


def fundo(a: argparse.Namespace) -> Image.Image:
    if not a.foto:
        return vinheta(Image.new("RGB", (W, H), "#" + a.cor), 0.45)
    f = Image.open(a.foto).convert("RGB")
    f = f.resize((a.foto_largura, round(f.height * a.foto_largura / f.width)), Image.LANCZOS)
    f = f.crop((a.foto_x, a.foto_y, a.foto_x + W, a.foto_y + H))
    if a.foto_tom == "vermelho":
        g = ImageOps.autocontrast(ImageOps.grayscale(f), cutoff=1)
        f = ImageOps.colorize(g, black=(25, 0, 0), mid=(170, 10, 10), white=(255, 70, 60))
    else:
        f = ImageEnhance.Contrast(f).enhance(1.08)
    return f


def personagem(caminho: str, altura: int, cinza: bool) -> Image.Image:
    p = Image.open(caminho).convert("RGBA")
    p = p.crop(p.getchannel("A").getbbox())
    p = p.resize((round(p.width * altura / p.height), altura), Image.LANCZOS)
    if not cinza:
        return ImageEnhance.Contrast(p).enhance(1.12)
    g = ImageOps.autocontrast(ImageOps.grayscale(p), cutoff=1)
    g = g.point(lambda v: max(0, min(255, int((v - 128) * 1.35 + 140))))
    linhas = Image.new("L", g.size, 255)
    d = ImageDraw.Draw(linhas)
    for y in range(0, g.height, 4):
        d.line((0, y, g.width, y), fill=205)
    g = ImageChops.multiply(g, linhas)
    return Image.merge("RGBA", (g, g, g, p.getchannel("A")))


def palavra(texto: str, largura: int, esticar: float) -> Image.Image:
    f = ImageFont.truetype(FONTE, 400)
    x0, y0, x1, y1 = f.getbbox(texto)
    m = Image.new("L", (x1 - x0 + 40, y1 - y0 + 40), 0)
    ImageDraw.Draw(m).text((20 - x0, 20 - y0), texto, font=f, fill=255)
    m = m.resize((round(m.width * esticar), m.height), Image.LANCZOS)
    return m.resize((largura, round(m.height * largura / m.width)), Image.LANCZOS)


def sombra(alfa: Image.Image, opacidade: float, desfoque: int) -> Image.Image:
    s = Image.new("RGBA", alfa.size, (0, 0, 0, 0))
    s.putalpha(alfa.point(lambda v: int(v * opacidade)).filter(ImageFilter.GaussianBlur(desfoque)))
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recorte")
    ap.add_argument("saida")
    ap.add_argument("--cor", default="D80000")
    ap.add_argument("--foto")
    ap.add_argument("--foto-largura", type=int, default=W)
    ap.add_argument("--foto-x", type=int, default=0)
    ap.add_argument("--foto-y", type=int, default=0)
    ap.add_argument("--foto-tom", choices=("real", "vermelho"), default="real")
    ap.add_argument("--altura", type=int, default=720)
    ap.add_argument("--x", type=int)
    ap.add_argument("--cinza", action="store_true")
    ap.add_argument("--texto", default="")
    ap.add_argument("--onde", choices=("topo", "baixo"), default="topo")
    ap.add_argument("--esticar", type=float, default=1.25)
    a = ap.parse_args()

    img = fundo(a).convert("RGBA")
    p = personagem(a.recorte, a.altura, a.cinza)
    px = (W - p.width) // 2 if a.x is None else a.x
    py = H - p.height + 50

    m = palavra(a.texto, 1220, a.esticar) if a.texto else None
    if m:
        tx = (W - m.width) // 2
        ty = 22 if a.onde == "topo" else H - m.height - 18
        if a.foto:
            # Foto clara atrás de letra branca: faixa escura e sombra na letra.
            faixa = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(faixa)
            for i in range(260):
                y = i if a.onde == "topo" else H - 1 - i
                d.line((0, y, W, y), fill=int(150 * (1 - i / 260) ** 1.6))
            img = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), img, faixa)
            img.alpha_composite(sombra(m, 0.6, 10), (tx, ty + 6))
        img.paste(Image.new("RGBA", m.size, (255, 255, 255, 255)), (tx, ty), m)

    img.alpha_composite(sombra(p.getchannel("A"), 0.65, 16), (px + 10, py + 8))
    img.alpha_composite(p, (px, py))

    if m:
        contorno = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(7)))
        img.paste(Image.new("RGBA", m.size, (255, 255, 255, 255)), (tx, ty), contorno)

    img.convert("RGB").save(a.saida, quality=92)
    previa = img.convert("RGB").resize((320, 180), Image.LANCZOS)
    previa.save(a.saida.rsplit(".", 1)[0] + "-320.jpg", quality=90)


if __name__ == "__main__":
    main()
