"""Gera imagens com o FLUX.2 [klein] 4B do Cloudflare Workers AI a partir de uma lista de pedidos.

Uso (raiz do auto-play):
  PYTHONPATH=. .venv/bin/python scripts/provisorio/gerar_imagens_klein.py pedidos.json --saida PASTA \
      [--teto-dia 9500]

pedidos.json: lista de objetos {"arquivo": "47-voce-capela", "prompt": "...", "refs": ["caminho.png", ...],
"seed": 1, "guidance": 4.0, "width": 1792, "height": 1008}. `refs` (até 4) viram input_image_0..3, reduzidas a
no máximo 511 px pelo ffmpeg (a API exige menos de 512x512). `guidance` e `seed` são opcionais.

Custo (página de preços do Workers AI, 2026-10-20): 26,05 neurons por bloco de 512x512 da saída e 5,37 por
bloco de cada referência; a cota grátis é de 10.000 neurons por dia UTC. O script soma os `registro.jsonl` da
pasta do teste (data/cache/teste-flux2-klein-2026-11-06) e da pasta de saída e para antes de passar de
--teto-dia. Credenciais: CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_API_TOKEN do .env (nunca impressas). Provedor
externo: rodar só
com pedido do dono na sessão (CLAUDE.md §14). Campos da API: changelog de 2026-01-15 do Workers AI.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

from app.settings import read_dotenv

MODELO = "@cf/black-forest-labs/flux-2-klein-4b"
TESTE = Path("data/cache/teste-flux2-klein-2026-11-06")
NEURONS_SAIDA = 26.05
NEURONS_ENTRADA = 5.37
REF_MAX = 511


def blocos(w: int, h: int) -> int:
    return math.ceil(w / 512) * math.ceil(h / 512)


def dimensoes(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True,
    ).stdout.strip().split(",")
    return int(out[0]), int(out[1])


def reduzir(ref: Path, destino: Path) -> tuple[int, int]:
    """Cópia PNG da referência com no máximo 511 px em cada lado."""
    escala = f"scale='min({REF_MAX},iw)':'min({REF_MAX},ih)':force_original_aspect_ratio=decrease"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ref), "-vf", escala, str(destino)], check=True)
    return dimensoes(destino)


def usados_hoje(saida: Path) -> float:
    hoje = datetime.now(UTC).date().isoformat()
    total = 0.0
    for reg in {*TESTE.glob("**/registro.jsonl"), saida / "registro.jsonl"}:
        if not reg.exists():
            continue
        for linha in reg.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                if str(d.get("data", "")).startswith(hoje):
                    total += float(d.get("neurons_estimados", 0))
    return total


def formato(b: bytes) -> str:
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if b[:2] == b"\xff\xd8":
        return "jpg"
    return "bin"


def gerar(pedido: dict, saida: Path, conta: str, token: str, tmp: Path) -> dict:
    w, h = int(pedido.get("width", 1792)), int(pedido.get("height", 1008))
    refs = [Path(r) for r in pedido.get("refs", [])][:4]
    campos = {"prompt": pedido["prompt"], "width": str(w), "height": str(h)}
    for chave in ("seed", "guidance"):
        if pedido.get(chave) is not None:
            campos[chave] = str(pedido[chave])
    arquivos = []
    refs_px = []
    for i, ref in enumerate(refs):
        red = tmp / f"ref{i}.png"
        refs_px.append(reduzir(ref, red))
        arquivos.append((f"input_image_{i}", (red.name, red.read_bytes(), "image/png")))
    estimado = blocos(w, h) * NEURONS_SAIDA + sum(blocos(*px) * NEURONS_ENTRADA for px in refs_px)
    inicio = time.monotonic()
    resp = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{conta}/ai/run/{MODELO}",
        headers={"Authorization": f"Bearer {token}"},
        data=campos, files=arquivos or None, timeout=300,
    )
    latencia = time.monotonic() - inicio
    try:
        corpo = resp.json()
    except ValueError:
        raise SystemExit(f"{pedido['arquivo']}: resposta não JSON ({resp.status_code})") from None
    if not corpo.get("success") or not corpo.get("result", {}).get("image"):
        raise SystemExit(f"{pedido['arquivo']}: erro da API {resp.status_code}: {corpo.get('errors')}")
    dados = base64.b64decode(corpo["result"]["image"])
    ext = formato(dados)
    nome = f"{pedido['arquivo']}-s{pedido.get('seed', 'x')}-g{pedido.get('guidance', 'def')}.{ext}"
    destino = saida / nome
    destino.write_bytes(dados)
    registro = {
        "arquivo": nome, "modelo": MODELO, "data": datetime.now(UTC).isoformat(timespec="seconds"),
        "pedido": {"width": w, "height": h, "seed": pedido.get("seed"), "guidance": pedido.get("guidance"),
                   "refs": [str(r) for r in refs]},
        "refs_enviadas_px": refs_px, "prompt": pedido["prompt"],
        "recebido": {"formato": ext, "dimensoes": list(dimensoes(destino)), "bytes": len(dados)},
        "sha256": hashlib.sha256(dados).hexdigest(), "latencia_s": round(latencia, 1),
        "neurons_estimados": round(estimado, 1),
    }
    with (saida / "registro.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pedidos")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--teto-dia", type=float, default=9500.0)
    args = ap.parse_args()
    env = read_dotenv(Path(".env"))
    conta, token = env.get("CLOUDFLARE_ACCOUNT_ID"), env.get("CLOUDFLARE_API_TOKEN")
    if not conta or not token:
        raise SystemExit("CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_API_TOKEN precisam estar no .env")
    pedidos = json.loads(Path(args.pedidos).read_text(encoding="utf-8"))
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        for pedido in pedidos:
            gasto = usados_hoje(saida)
            w, h = int(pedido.get("width", 1792)), int(pedido.get("height", 1008))
            previsto = blocos(w, h) * NEURONS_SAIDA + len(pedido.get("refs", [])) * NEURONS_ENTRADA
            if gasto + previsto > args.teto_dia:
                print(f"PARADO: {gasto:.0f} usados hoje + {previsto:.0f} > teto {args.teto_dia:.0f}")
                return 2
            r = gerar(pedido, saida, conta, token, Path(tmpdir))
            dia = gasto + r["neurons_estimados"]
            print(f"{r['arquivo']}: {r['recebido']['dimensoes']} {r['recebido']['formato']} "
                  f"{r['latencia_s']} s ~{r['neurons_estimados']} neurons (dia: {dia:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
