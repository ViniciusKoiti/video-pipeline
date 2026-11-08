"""Mede o recall do conferidor de texto (`ocr_quadros.py`) com defeitos injetados em cópias dos quadros.

Uso: `LD_LIBRARY_PATH=... TESSDATA_PREFIX=... .venv/bin/python scripts/bench/ocr_recall.py <episode-id>
[--tesseract tesseract] [--lang por] [--psm 11] [--frac 0.6] [--similar 0.8] [--cobertura 0.8]
[--saida ARQUIVO.json]`

- Parte dos quadros limpos de `ocr_quadros.py` (escala 1, `data/cache/ocr-<id>/quadros-x1/`) e faz uma
  cópia de cada quadro com um defeito por tipo:
  - `corte`: a última palavra esperada some (coberta com a cor do fundo), como texto cortado;
  - `numero`: o primeiro dígito de um número de dois ou mais dígitos muda (57% vira 27%);
  - `letra`: a primeira vogal de uma palavra longa muda (justiça vira jostiça), erro de digitação na tela.
- A edição é só de imagem PNG com o ffmpeg (`drawbox` e `drawtext`, fonte Inter, expansão de texto desligada).
  Nenhum vídeo é renderizado.
- Lê cada cópia com o mesmo Tesseract e aplica as mesmas regras de alerta de `ocr_quadros.py`, com os
  limites `--similar` (similaridade para contar uma palavra como lida) e `--cobertura` (fração mínima de
  palavras lidas). Um defeito é detectado se houver `sem_leitura`, `faltando` ou `numero_divergente`.
- Quadros que já alertavam limpos ficam de fora do recall, porque a detecção deles não prova nada.
- Saída em `--saida` (padrão `data/cache/ocr-<id>/recall.json`), com as cópias em
  `data/cache/ocr-<id>/defeitos/`.
- Recusa rodar com a CPU limitada (sonda acima de 0,3 s): o tempo entra na medição.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "bench"))

import ocr_quadros as ocr  # noqa: E402

from app.commands.errors import run  # noqa: E402
from app.pipeline.bench import cpu_probe  # noqa: E402

FONT = Path("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf")
CPU_LIMIT_S = 0.3
SELECAO_SIMILAR = 0.8  # só escolhe o alvo da cópia; não muda o critério de detecção
DETECTA = frozenset({"sem_leitura", "faltando", "numero_divergente"})
TIPOS = ("corte", "numero", "letra")
VOGAIS = {"a": "e", "e": "i", "i": "o", "o": "a", "u": "o"}


def bate(token: str, alvo: str) -> bool:
    return token == alvo or SequenceMatcher(None, token, alvo).ratio() >= SELECAO_SIMILAR


def avaliar(texto: str, words: list[dict[str, Any]]) -> dict[str, Any]:
    esperado = ocr.tokens(texto)
    lido = [tok for w in words for tok in ocr.tokens(w["text"])]
    faltando, sobrando = ocr.match(esperado, lido)
    cobertura = (len(esperado) - len(faltando)) / len(esperado) if esperado else 1.0
    numeros = [t for t in faltando if any(ch.isdigit() for ch in t)]
    alertas: list[str] = []
    if esperado and not words:
        alertas.append("sem_leitura")
    elif esperado and cobertura < ocr.MIN_COVERAGE:
        alertas.append("faltando")
    if numeros:
        alertas.append("numero_divergente")
    return {
        "alertas": alertas,
        "faltando": faltando,
        "sobrando": len(sobrando),
        "cobertura": round(cobertura, 3),
        "lido": " ".join(w["text"] for w in words),
    }


def escolher(
    tipo: str, words: list[dict[str, Any]], esperado: list[str]
) -> tuple[dict[str, Any] | None, str | None, str]:
    """Escolhe a palavra a estragar e o texto novo (None = só cobrir). Devolve (alvo, novo, descrição)."""
    if tipo == "corte":
        ultimo = esperado[-1] if esperado else ""
        hits = [w for w in words if any(bate(t, ultimo) for t in ocr.tokens(w["text"]))]
        if not hits:
            return None, None, ""
        alvo = max(hits, key=lambda w: (w["top"], w["left"]))
        return alvo, None, f"cobre '{alvo['text']}'"
    if tipo == "numero":
        numeros = [t for t in esperado if len(t) >= 2 and any(ch.isdigit() for ch in t)]
        hits = [
            w
            for w in words
            if len(w["text"]) >= 2
            and any(ch.isdigit() for ch in w["text"])
            and any(bate(t, n) for t in ocr.tokens(w["text"]) for n in numeros)
        ]
        if not hits:
            return None, None, ""
        alvo = min(hits, key=lambda w: (w["top"], w["left"]))
        texto = alvo["text"]
        posicao = next(i for i, ch in enumerate(texto) if ch.isdigit())
        novo = texto[:posicao] + str((int(texto[posicao]) + 3) % 10) + texto[posicao + 1 :]
        return alvo, novo, f"'{texto}' vira '{novo}'"
    # letra
    hits = [
        w
        for w in words
        if any(len(t) >= 6 and t.isalpha() and t in esperado for t in ocr.tokens(w["text"]))
    ]
    if not hits:
        return None, None, ""
    alvo = min(hits, key=lambda w: (w["top"], w["left"]))
    texto = alvo["text"]
    posicao = next((i for i, ch in enumerate(texto) if ch.lower() in VOGAIS), None)
    if posicao is None:
        return None, None, ""
    trocada = VOGAIS[texto[posicao].lower()]
    trocada = trocada.upper() if texto[posicao].isupper() else trocada
    novo = texto[:posicao] + trocada + texto[posicao + 1 :]
    return alvo, novo, f"'{texto}' vira '{novo}'"


def media_cor(img: Path, x: int, y: int, w: int, h: int) -> tuple[int, int, int]:
    x = max(0, min(x, ocr.WIDTH_PX - 1))
    y = max(0, min(y, ocr.HEIGHT_PX - 1))
    w = max(1, min(w, ocr.WIDTH_PX - x))
    h = max(1, min(h, ocr.HEIGHT_PX - y))
    out = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(img),
            "-vf",
            f"crop={w}:{h}:{x}:{y},scale=1:1:flags=area",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    return out[0], out[1], out[2]


def pintar(origem: Path, destino: Path, alvo: dict[str, Any], novo: str | None) -> None:
    esq, topo, larg, alt = alvo["left"], alvo["top"], alvo["width"], alvo["height"]
    faixa_y = topo - 8 if topo >= 8 else min(topo + alt + 2, ocr.HEIGHT_PX - 6)
    bg = media_cor(origem, esq, faixa_y, larg, 6)
    luminancia = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    fg = (250, 250, 250) if luminancia < 128 else (20, 20, 20)
    x, y = max(0, esq - 3), max(0, topo - 3)
    cor_fundo = f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
    filtros = [f"drawbox=x={x}:y={y}:w={larg + 6}:h={alt + 6}:color={cor_fundo}:t=fill"]
    if novo is not None:
        arquivo_texto = destino.with_suffix(".txt")
        arquivo_texto.write_text(novo, encoding="utf-8")
        tamanho = max(8, round(alt * 0.85))
        cor = f"#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"
        filtros.append(
            f"drawtext=fontfile={FONT}:textfile={arquivo_texto}:expansion=none"
            f":x={esq}:y={topo}:fontsize={tamanho}:fontcolor={cor}"
        )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(origem), "-vf", ",".join(filtros), str(destino)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Recall do conferidor de texto com defeitos injetados.")
    parser.add_argument("episodio")
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--lang", default="por")
    parser.add_argument("--psm", type=int, default=11)
    parser.add_argument("--frac", type=float, default=0.6)
    parser.add_argument("--similar", type=float, default=ocr.SIMILAR)
    parser.add_argument("--cobertura", type=float, default=ocr.MIN_COVERAGE)
    parser.add_argument("--saida", type=Path, default=None)
    args = parser.parse_args()

    probe = cpu_probe()
    if probe > CPU_LIMIT_S:
        print(f"CPU limitada (sonda {probe:.3f} s, acima de {CPU_LIMIT_S} s): medição inválida, nada rodou.")
        return 2

    # Os limites da detecção valem para `avaliar` e para `ocr.match`, que leem estas constantes do módulo.
    ocr.SIMILAR = args.similar
    ocr.MIN_COVERAGE = args.cobertura

    ep_dir = ROOT / "data" / "episodes" / args.episodio
    out_dir = ROOT / "data" / "cache" / f"ocr-{args.episodio}"
    quadros_dir = out_dir / "quadros-x1"
    defeitos_dir = out_dir / "defeitos"
    saida = args.saida or out_dir / "recall.json"
    if not quadros_dir.is_dir():
        print(f"faltam os quadros limpos em {quadros_dir}; rode antes scripts/bench/ocr_quadros.py")
        return 2

    # Mesma ordem e mesmos nomes de ocr_quadros.py, para usar os quadros que ele já extraiu.
    episode = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    planos: list[tuple[str, str, str]] = []
    for scene in episode["scenes"]:
        for shot in scene["shots"]:
            spec = shot["spec"]
            if spec["kind"] in ocr.TEXT_KINDS:
                planos.append((scene["id"], spec["kind"], ocr.expected_text(spec)))

    inicio = time.perf_counter()
    limpos: list[dict[str, Any]] = []
    casos: list[dict[str, Any]] = []
    for i, (cena, tipo_plano, texto) in enumerate(planos, 1):
        quadro = quadros_dir / f"{i:02d}-{cena}-{tipo_plano}.png"
        words = ocr.read_words(args.tesseract, quadro, args.lang, args.psm, 1)
        base = avaliar(texto, words)
        ja_alertava = bool(DETECTA & set(base["alertas"]))
        limpos.append({"quadro": quadro.name, "alertas": base["alertas"], "ja_alertava": ja_alertava})
        esperado = ocr.tokens(texto)
        for tipo in TIPOS:
            alvo, novo, descricao = escolher(tipo, words, esperado)
            caso: dict[str, Any] = {"tipo": tipo, "quadro": quadro.name, "ja_alertava": ja_alertava}
            if alvo is None:
                caso["injetavel"] = False
                casos.append(caso)
                continue
            destino = defeitos_dir / tipo / quadro.name
            destino.parent.mkdir(parents=True, exist_ok=True)
            pintar(quadro, destino, alvo, novo)
            lidos = ocr.read_words(args.tesseract, destino, args.lang, args.psm, 1)
            res = avaliar(texto, lidos)
            caso.update(
                {
                    "injetavel": True,
                    "descricao": descricao,
                    "lido": res["lido"],
                    "alertas": res["alertas"],
                    "faltando": res["faltando"],
                    "detectado": bool(DETECTA & set(res["alertas"])),
                }
            )
            casos.append(caso)
    decorrido = time.perf_counter() - inicio

    resumo: dict[str, Any] = {}
    for tipo in TIPOS:
        do_tipo = [c for c in casos if c["tipo"] == tipo]
        injetados = [c for c in do_tipo if c["injetavel"]]
        avaliados = [c for c in injetados if not c["ja_alertava"]]
        detectados = [c for c in avaliados if c["detectado"]]
        resumo[tipo] = {
            "quadros_sem_alvo": len(do_tipo) - len(injetados),
            "injetados": len(injetados),
            "excluidos_ja_alertavam": len(injetados) - len(avaliados),
            "avaliados": len(avaliados),
            "detectados": len(detectados),
            "recall": round(len(detectados) / len(avaliados), 3) if avaliados else None,
        }

    meta = {
        "data": date.today().isoformat(),
        "episodio": args.episodio,
        "tesseract": ocr.tesseract_version(args.tesseract),
        "idioma": args.lang,
        "psm": args.psm,
        "similar": args.similar,
        "cobertura": args.cobertura,
        "sonda_cpu_s": round(probe, 3),
        "quadros_limpos": len(limpos),
        "falsos_alarmes_limpos": sum(1 for q in limpos if q["ja_alertava"]),
        "copias_geradas": sum(1 for c in casos if c["injetavel"]),
        "decorrido_s": round(decorrido, 1),
    }
    conteudo = {"meta": meta, "resumo": resumo, "limpos": limpos, "casos": casos}
    saida.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"similar={args.similar} cobertura={args.cobertura}  "
        f"alarmes em limpos: {meta['falsos_alarmes_limpos']}/{meta['quadros_limpos']}"
    )
    for tipo, r in resumo.items():
        print(
            f"{tipo:<7} injetados={r['injetados']} avaliados={r['avaliados']} "
            f"detectados={r['detectados']} recall={r['recall']}"
        )
    for c in casos:
        if c["injetavel"] and not c["detectado"] and not c["ja_alertava"]:
            print(f"  perdido: {c['tipo']} {c['quadro']} {c['descricao']} | lido: {c['lido'][:90]}")
    print(f"tempo: {meta['decorrido_s']} s  saída: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run("ocr-recall", main))
