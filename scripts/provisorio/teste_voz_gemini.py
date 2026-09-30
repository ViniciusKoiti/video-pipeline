"""Comparação pequena de voz: Gemini TTS × Kokoro, às cegas (CLAUDE.md §7; provisório, sem adapter ainda).

Uso: `.venv/bin/python scripts/provisorio/teste_voz_gemini.py <comando>`

  vozes                         lista as vozes da biblioteca do Gemini para pt-BR (1 chamada)
  gerar --vozes Charon,pt-br-advisor-9 [--modelo gemini-3.8-flash-lite-tts]
                                as 3 falas do vídeo-régua em cada voz (1 chamada por fala e voz)
  cegas                         mesmo volume em tudo (Gemini e Kokoro) e cópias com letras sorteadas

- Chave em `GEMINI_API_KEY` no `.env`, enviada só no cabeçalho `x-goog-api-key`; nunca é impressa.
- Camada gratuita, sem faturamento (§2.1). Erro de cota (429) para o teste; outro erro é registrado e segue.
- As falas são a narração aprovada do `votorantim-dinheiro` (história pública, §13.2). O Kokoro entra com os
  WAVs que o vídeo já usa (`pm_alex`), sem gerar de novo.
- Saída em `data/benchmarks/voz-gemini/` (fora do Git): WAVs, `chamadas.json` (modelo, voz, latência, bytes,
  duração, erro) e `cegas/`, com o gabarito em `cegas/gabarito.json` (abrir só depois de ouvir).
"""

from __future__ import annotations

import argparse
import base64
import json
import random
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media.probe import duration_ms  # noqa: E402
from app.settings import load_settings  # noqa: E402

API = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "gemini-3.8-flash-tts"
EPISODE = ROOT / "data" / "episodes" / "votorantim-dinheiro"
OUT = ROOT / "data" / "benchmarks" / "voz-gemini"
SCENES = ("S04", "S05", "S09")  # datas e valores; nomes difíceis; banco e valor por extenso
# O texto é lido ao pé da letra: a direção de fala vai só no `style` (documentação de speech-generation).
STYLE = ("narração de documentário em português do Brasil, com sotaque brasileiro; tom calmo, informativo e "
         "neutro; ritmo moderado")
LOUDNESS = "loudnorm=I=-16:TP=-1.5:LRA=11"
PAUSE_S = 21  # a camada gratuita aceita 3 chamadas por minuto (limite visto no erro 429 em 2026-09-29)


def request(key: str, method: str, path: str, body: dict | None = None, query: list | None = None) -> dict:
    url = f"{API}/{path}" + (f"?{urllib.parse.urlencode(query)}" if query else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {error.code}: {detail}") from None


def narration() -> dict[str, str]:
    scenes = json.loads((EPISODE / "scenes.json").read_text())["scenes"]
    return {s["id"]: s["narration"] for s in scenes if s["id"] in SCENES}


def voices(key: str) -> None:
    found = request(key, "GET", "voices", query=[("language_code", "pt-BR"), ("page_size", "50")])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "vozes-pt-br.json").write_text(json.dumps(found, ensure_ascii=False, indent=2))
    for voice in found.get("voices", []):
        print({k: v for k, v in voice.items() if k not in ("replicated",)})
    print(f"{len(found.get('voices', []))} vozes -> {OUT / 'vozes-pt-br.json'}")


def generate(key: str, names: list[str], model: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / "chamadas.json"
    log = json.loads(log_path.read_text()) if log_path.is_file() else []
    for scene_id, text in narration().items():
        for voice in names:
            lite = "-lite" if "lite" in model else ""
            path = OUT / f"{scene_id}-gemini{lite}-{voice.lower()}.wav"
            if path.is_file():
                continue  # já gerado: não gasta chamada
            body = {
                "model": model,
                "input": [{"type": "user_input", "content": [{
                    "type": "text", "text": text,
                    "annotations": [{"type": "speech_metadata", "style": STYLE}],
                }]}],
                "response_format": {"type": "audio"},
                "generation_config": {"speech_config": [{"voice": voice}]},
            }
            entry = {"cena": scene_id, "voz": voice, "modelo": model, "estilo": STYLE,
                     "quando": time.strftime("%Y-%m-%d %H:%M:%S")}
            started = time.monotonic()
            try:
                result = request(key, "POST", "interactions", body)
                audio = [c for step in result.get("steps", []) if step.get("type") == "model_output"
                         for c in step.get("content", []) if c.get("type") == "audio"]
                if not audio:
                    raise RuntimeError(f"resposta sem áudio: {json.dumps(result)[:300]}")
                path.write_bytes(base64.b64decode(audio[-1]["data"]))
                entry |= {"arquivo": path.name, "bytes": path.stat().st_size, "duracao_ms": duration_ms(path),
                          "uso": result.get("usage")}
            except Exception as error:  # cota, modelo ausente, resposta inesperada: registra e segue
                entry["erro"] = str(error)
            entry["latencia_s"] = round(time.monotonic() - started, 2)
            log.append(entry)
            log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2))
            print(entry.get("arquivo") or entry.get("erro"), f"({entry['latencia_s']} s)")
            if "HTTP 429" in entry.get("erro", ""):
                raise SystemExit("cota da camada gratuita atingida: teste parado (§2.1)")
            time.sleep(PAUSE_S)


def blind() -> None:
    target = OUT / "cegas"
    target.mkdir(parents=True, exist_ok=True)
    answers: dict[str, str] = {}
    for scene_id in SCENES:
        kokoro = sorted((EPISODE / "voice").glob(f"{scene_id}-*.wav"))
        samples = [("kokoro-pm_alex", kokoro[0])] if kokoro else []
        samples += [(p.stem.split("-", 1)[1], p) for p in sorted(OUT.glob(f"{scene_id}-gemini-*.wav"))]
        random.shuffle(samples)
        for letter, (origin, path) in zip("ABCDEFGH", samples, strict=False):
            out = target / f"{scene_id}-{letter}.wav"
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", LOUDNESS, "-ar", "48000", str(out)],
                check=True,
            )
            answers[out.name] = origin
    (target / "gabarito.json").write_text(json.dumps(answers, indent=2))
    print(f"{len(answers)} arquivos em {target} (gabarito em gabarito.json: abrir só depois de ouvir)")


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("vozes")
    generate_parser = commands.add_parser("gerar")
    generate_parser.add_argument("--vozes", required=True)
    generate_parser.add_argument("--modelo", default=MODEL)
    commands.add_parser("cegas")
    args = parser.parse_args()
    if args.command == "cegas":
        return blind()
    secret = load_settings(ROOT).secrets.gemini_api_key
    if secret is None or not secret.get_secret_value():
        raise SystemExit("GEMINI_API_KEY vazia no .env")
    key = secret.get_secret_value()
    if args.command == "vozes":
        return voices(key)
    return generate(key, [v.strip() for v in args.vozes.split(",") if v.strip()], args.modelo)


if __name__ == "__main__":
    main()
