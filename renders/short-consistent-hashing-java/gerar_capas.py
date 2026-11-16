"""Capas 1080x1920 dos Reels e do Short de consistent hashing (marca da empresa numa placa branca).

Uso: python3 gerar_capas.py (Pillow do sistema; o -I não enxerga o pacote)
O logo entra sem alteração (proporção, cor e fonte originais), sozinho numa placa branca com respiro, como
pedem os termos da Amazon e do Discord (data/benchmarks/termos-logos-empresas.md). Sem o arquivo do logo
(Akamai), a placa leva o nome em texto e a capa fica marcada como provisória.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
LOGOS = AQUI / "miniaturas" / "logos"
SAIDA = AQUI / "miniaturas"
FONTE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
W, H = 1080, 1920
FUNDO = (14, 17, 22)
AMARELO = (255, 210, 63)
BRANCO = (255, 255, 255)

CAPAS = [
    {
        "id": "reel-1-amazon",
        "logo": "amazon-logo-squid-ink-smile-orange.png",
        "nome": "AMAZON",
        "linhas": ["COMO A", "AMAZON", "ADICIONA UM", "SERVIDOR SEM", "ESVAZIAR O", "CACHE?"],
        "destaque": {"AMAZON"},
    },
    {
        "id": "reel-2-discord",
        "logo": "Discord-Logo-Blurple.png",
        "nome": "DISCORD",
        "linhas": ["COMO O", "DISCORD", "DESCOBRE EM", "QUAL NÓ ESTÁ", "CADA", "COMUNIDADE?"],
        "destaque": {"DISCORD"},
    },
    {
        "id": "reel-3-akamai",
        "logo": "akamai.png",
        "nome": "AKAMAI",
        "linhas": ["COMO A", "AKAMAI", "DECIDE QUAL", "SERVIDOR", "ENTREGA CADA", "ARQUIVO?"],
        "destaque": {"AKAMAI"},
    },
    {
        "id": "short-java-amazon",
        "logo": "amazon-logo-squid-ink-smile-orange.png",
        "nome": "AMAZON",
        "linhas": ["ADICIONEI 1", "SERVIDOR E O", "CACHE INTEIRO", "MUDOU DE", "LUGAR"],
        "destaque": {"LUGAR"},
        "selo": "JAVA",
        "texto_y": 800,
    },
]


def anel(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(60, 68, 82), width=6)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        forte = i in (2, 3, 4)
        rr = 22 if forte else 14
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=AMARELO if forte else (96, 106, 124))


def placa(img: Image.Image, capa: dict) -> None:
    pw, ph = 920, 360
    x0, y0 = (W - pw) // 2, 130
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=44, fill=BRANCO)
    arquivo = LOGOS / capa["logo"]
    if arquivo.exists():
        logo = Image.open(arquivo).convert("RGBA")
        esc = min((pw - 160) / logo.width, (ph - 130) / logo.height)  # só escala, sem recorte nem recolorir
        logo = logo.resize((round(logo.width * esc), round(logo.height * esc)), Image.LANCZOS)
        img.paste(logo, (x0 + (pw - logo.width) // 2, y0 + (ph - logo.height) // 2), logo)
    else:
        f = ImageFont.truetype(FONTE, 150)
        esq, t, r, b = d.textbbox((0, 0), capa["nome"], font=f)
        d.text(
            (x0 + (pw - (r - esq)) // 2 - esq, y0 + (ph - (b - t)) // 2 - t),
            capa["nome"],
            font=f,
            fill=(30, 30, 30),
        )
        capa["provisoria"] = True


def texto(img: Image.Image, capa: dict) -> None:
    d = ImageDraw.Draw(img)
    tam = 138
    while (
        tam > 60 and max(d.textlength(ln, font=ImageFont.truetype(FONTE, tam)) for ln in capa["linhas"]) > 900
    ):
        tam -= (
            2  # o mesmo tamanho em todas as linhas, com a mais larga em 900 px (margem de 90 px de cada lado)
        )
    f = ImageFont.truetype(FONTE, tam)
    y = capa.get("texto_y", 700)  # linha de base da primeira linha
    for ln in capa["linhas"]:
        cor = AMARELO if ln in capa["destaque"] else BRANCO
        d.text((W // 2, y), ln, font=f, fill=cor, anchor="ms", stroke_width=3, stroke_fill=(0, 0, 0))
        y += round(tam * 1.1)


def gerar(capa: dict) -> Path:
    img = Image.new("RGB", (W, H), FUNDO)
    placa(img, capa)
    texto(img, capa)
    d = ImageDraw.Draw(img)
    anel(d, W // 2, 1660, 150)
    if capa.get("selo"):
        f = ImageFont.truetype(FONTE, 84)
        esq, t, r, b = d.textbbox((0, 0), capa["selo"], font=f)
        larg, alt = (r - esq) + 80, (b - t) + 44
        bx, by = (W - larg) // 2, 530
        d.rounded_rectangle((bx, by, bx + larg, by + alt), radius=24, fill=AMARELO)
        d.text((bx + 40 - esq, by + 22 - t), capa["selo"], font=f, fill=(14, 17, 22))
    f = ImageFont.truetype(FONTE, 40)
    rod = "CONSISTENT HASHING · JAVA"
    esq, t, r, b = d.textbbox((0, 0), rod, font=f)
    d.text(((W - (r - esq)) // 2 - esq, 1850), rod, font=f, fill=(150, 160, 176))
    out = SAIDA / f"capa-{capa['id']}{'-provisoria' if capa.get('provisoria') else ''}.jpg"
    img.save(out, quality=92)
    img.resize((320, round(320 * H / W)), Image.LANCZOS).save(
        out.with_name(out.stem + "-320.jpg"), quality=90
    )
    return out


if __name__ == "__main__":
    for c in CAPAS:
        print(gerar(c))
