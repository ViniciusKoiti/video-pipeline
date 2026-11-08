"""Lê o texto dos quadros de um vídeo renderizado com o Tesseract e compara com o roteiro (teste de OCR).

Uso: `LD_LIBRARY_PATH=... TESSDATA_PREFIX=... .venv/bin/python scripts/bench/ocr_quadros.py <episode-id>
[--video renders/final.mp4] [--tesseract tesseract] [--lang por] [--psm 11] [--frac 0.6] [--escala 1]
[--saida ARQUIVO.json]`

- Lê `data/episodes/<id>/episode.json` e pega os planos com texto na tela (keyword, number, lower_third,
  quote, compare). Para cada um, tira um quadro em `--frac` da duração do plano (depois da entrada animada) e
  lê com o Tesseract. `--escala 2` amplia o quadro antes da leitura.
- O texto esperado vem dos campos do próprio plano. Na citação só vale o texto: a atribuição não aparece no
  cartão, e a fonte do rodapé não é checada. A comparação é por palavra, sem acento e sem caixa, com
  similaridade mínima de 0,8 para contar como lida.
- Alertas: `sem_leitura` (nada lido onde há texto), `faltando` (menos de 80% das palavras esperadas),
  `numero_divergente` (número esperado não lido com exatidão, mesmo com a cobertura alta) e `perto_da_borda`
  (palavra do texto esperado a menos de 30 px da borda). Alerta não aprova nem reprova: o humano decide.
- Só lê o episódio e o vídeo; nada é alterado. Saída em `--saida` (padrão
  `data/cache/ocr-<id>/ocr-x<escala>.json`, fora do Git), com os quadros em
  `data/cache/ocr-<id>/quadros-x<escala>/`.
- Recusa rodar com a CPU limitada (sonda acima de 0,3 s): o tempo entra na medição.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import resource
import subprocess
import sys
import time
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.pipeline.bench import cpu_probe  # noqa: E402

TEXT_KINDS = ("keyword", "number", "lower_third", "quote", "compare")
CPU_LIMIT_S = 0.3
SIMILAR = 0.8
EDGE_PX = 30
WIDTH_PX = 1920
HEIGHT_PX = 1080
MIN_COVERAGE = 0.8


def expected_text(spec: dict[str, Any]) -> str:
    kind = spec["kind"]
    if kind == "keyword":
        return str(spec["text"])
    if kind == "number":
        return f"{spec['value']} {spec['label']}"
    if kind == "lower_third":
        return f"{spec['name']} {spec['role']}"
    if kind == "quote":
        return str(spec["text"])
    left, right = spec["left"], spec["right"]
    return " ".join([left["value"], left["label"], right["value"], right["label"]])


def tokens(text: str) -> list[str]:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    return re.findall(r"[a-z0-9]+", plain)


def grab(video: Path, seconds: float, out: Path, escala: int) -> None:
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{seconds:.3f}", "-i", str(video), "-frames:v", "1"]
    if escala > 1:
        cmd += ["-vf", f"scale=iw*{escala}:ih*{escala}:flags=lanczos"]
    subprocess.run([*cmd, str(out)], check=True)


def read_words(tesseract: str, image: Path, lang: str, psm: int, escala: int) -> list[dict[str, Any]]:
    proc = subprocess.run(
        [tesseract, str(image), "stdout", "-l", lang, "--psm", str(psm), "tsv"],
        capture_output=True,
        text=True,
        check=True,
    )
    words: list[dict[str, Any]] = []
    for row in csv.DictReader(proc.stdout.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE):
        text = (row.get("text") or "").strip()
        if not text or row.get("level") != "5":
            continue
        words.append(
            {
                "text": text,
                "conf": float(row["conf"]),
                "left": int(row["left"]) // escala,
                "top": int(row["top"]) // escala,
                "width": int(row["width"]) // escala,
                "height": int(row["height"]) // escala,
            }
        )
    return words


def match(expected: list[str], read: list[str]) -> tuple[list[str], list[str]]:
    """Casa cada palavra esperada com a melhor palavra lida ainda não usada. Devolve (faltando, sobrando)."""
    unused = list(read)
    missing: list[str] = []
    for tok in expected:
        best, best_at = 0.0, -1
        for at, cand in enumerate(unused):
            ratio = 1.0 if cand == tok else SequenceMatcher(None, tok, cand).ratio()
            if ratio > best:
                best, best_at = ratio, at
        if best >= SIMILAR:
            unused.pop(best_at)
        else:
            missing.append(tok)
    return missing, unused


def near_edge(words: list[dict[str, Any]]) -> bool:
    return any(
        w["left"] < EDGE_PX
        or w["top"] < EDGE_PX
        or w["left"] + w["width"] > WIDTH_PX - EDGE_PX
        or w["top"] + w["height"] > HEIGHT_PX - EDGE_PX
        for w in words
    )


def tesseract_version(tesseract: str) -> str:
    out = subprocess.run([tesseract, "--version"], capture_output=True, text=True, check=True)
    return out.stdout.splitlines()[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR dos quadros com texto de um episódio renderizado.")
    parser.add_argument("episodio")
    parser.add_argument("--video", type=Path, default=None)
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--lang", default="por")
    parser.add_argument("--psm", type=int, default=11)
    parser.add_argument("--frac", type=float, default=0.6)
    parser.add_argument("--escala", type=int, default=1)
    parser.add_argument("--saida", type=Path, default=None)
    args = parser.parse_args()

    probe = cpu_probe()
    if probe > CPU_LIMIT_S:
        print(f"CPU limitada (sonda {probe:.3f} s, acima de {CPU_LIMIT_S} s): medição inválida, nada rodou.")
        return 2

    ep_dir = ROOT / "data" / "episodes" / args.episodio
    video = args.video or ep_dir / "renders" / "final.mp4"
    out_dir = ROOT / "data" / "cache" / f"ocr-{args.episodio}"
    frames_dir = out_dir / f"quadros-x{args.escala}"
    frames_dir.mkdir(parents=True, exist_ok=True)
    saida = args.saida or out_dir / f"ocr-x{args.escala}.json"

    episode = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    planos: list[tuple[str, str, float, str]] = []
    for scene in episode["scenes"]:
        for shot in scene["shots"]:
            spec = shot["spec"]
            if spec["kind"] not in TEXT_KINDS:
                continue
            # start_ms de cada plano é relativo ao início da cena (os planos somam a duração da cena).
            moment = scene["start_ms"] + shot["start_ms"] + args.frac * shot["duration_ms"]
            planos.append((scene["id"], spec["kind"], moment / 1000, expected_text(spec)))

    inicio = time.perf_counter()
    resultados: list[dict[str, Any]] = []
    for i, (cena, tipo, seconds, texto) in enumerate(planos, 1):
        image = frames_dir / f"{i:02d}-{cena}-{tipo}.png"
        grab(video, seconds, image, args.escala)
        words = read_words(args.tesseract, image, args.lang, args.psm, args.escala)
        esperado = tokens(texto)
        lido = [tok for w in words for tok in tokens(w["text"])]
        faltando, sobrando = match(esperado, lido)
        cobertura = (len(esperado) - len(faltando)) / len(esperado) if esperado else 1.0
        numeros_faltando = [t for t in faltando if any(ch.isdigit() for ch in t)]
        # Só palavras do próprio texto esperado entram no teste de borda; o ruído do fundo não conta.
        esperadas = set(esperado)
        do_texto = [w for w in words if tokens(w["text"]) and all(t in esperadas for t in tokens(w["text"]))]
        alertas: list[str] = []
        if esperado and not words:
            alertas.append("sem_leitura")
        elif esperado and cobertura < MIN_COVERAGE:
            alertas.append("faltando")
        if numeros_faltando:
            alertas.append("numero_divergente")
        if do_texto and near_edge(do_texto):
            alertas.append("perto_da_borda")
        resultados.append(
            {
                "quadro": image.name,
                "cena": cena,
                "tipo": tipo,
                "segundo": round(seconds, 3),
                "esperado": texto,
                "lido": " ".join(w["text"] for w in words),
                "cobertura": round(cobertura, 3),
                "faltando": faltando,
                "numeros_faltando": numeros_faltando,
                "sobrando": sobrando,
                "confianca_media": round(sum(w["conf"] for w in words) / len(words), 1) if words else None,
                "alertas": alertas,
            }
        )
    decorrido = time.perf_counter() - inicio

    meta = {
        "data": date.today().isoformat(),
        "episodio": args.episodio,
        "video": str(video.relative_to(ROOT)) if video.is_relative_to(ROOT) else str(video),
        "tesseract": tesseract_version(args.tesseract),
        "idioma": args.lang,
        "psm": args.psm,
        "escala": args.escala,
        "fracao_do_plano": args.frac,
        "sonda_cpu_s": round(probe, 3),
        "quadros": len(resultados),
        "alertas": sum(1 for r in resultados if r["alertas"]),
        "decorrido_s": round(decorrido, 1),
        "pico_memoria_filhos_kb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }
    conteudo = {"meta": meta, "quadros": resultados}
    saida.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"quadros: {meta['quadros']}  alertas: {meta['alertas']}  tempo: {meta['decorrido_s']} s")
    for r in resultados:
        if r["alertas"]:
            print(
                f"  {r['quadro']}  {','.join(r['alertas'])}  cobertura={r['cobertura']}  "
                f"faltando={r['faltando']}  sobrando={len(r['sobrando'])}"
            )
    print(f"saída: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run("ocr-quadros", main))
