"""Mistura a trilha 'Spirit of Fire' no vídeo do YouTube do Reel da Amazon
(fora do `vp short juntar`, decisão do dono, 2026-11-08).

Uso: python3 misturar_musica.py <sem-musica.mp4> <com-musica.mp4>
Plano (plano-animacao.md, seção 4): música em `pergunta` e `anel`; nenhuma em `medicao` e `pontos`;
volta em `fecho`.
Os tempos vêm do content.voz.json (soma das durações).
A trilha é ducada pela voz (DUCKING de app/render/constants).
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
EP = RAIZ / "data/episodes/reel-consistent-hashing-amazon-pt"
FAIXA = EP / "assets/ytal-spirit-of-fire.mp3"
DUCKING = "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500"
ALVO_MUSICA_LUFS = -31.0  # nível "low": cerca de 15 dB abaixo da voz (-16 LUFS)
FADE = 0.6


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def lufs(arquivo, ate):
    r = run(["ffmpeg", "-nostats", "-t", str(ate), "-i", str(arquivo), "-af", "ebur128", "-f", "null", "-"])
    linha = [ln for ln in r.stderr.splitlines() if "I:" in ln and "LUFS" in ln][-1]
    return float(linha.split("I:")[1].split("LUFS")[0])


def main(entrada, saida):
    cenas = json.loads((EP / "content.voz.json").read_text())["scenes"]
    t, inicio = 0.0, {}
    for c in cenas:
        inicio[c["id"]] = round(t, 3)
        t += c["durationSec"]
    total = round(t, 3)
    fim_anel, ini_fecho = inicio["medicao"], inicio["fecho"]
    ganho = ALVO_MUSICA_LUFS - lufs(FAIXA, total)
    seg1 = (
        f"[1:a]atrim=0:{fim_anel},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,"
        f"afade=t=out:st={fim_anel - FADE}:d={FADE}[m1]"
    )
    dur2 = round(total - ini_fecho, 3)
    seg2 = (
        f"[1:a]atrim={ini_fecho}:{total},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},"
        f"afade=t=out:st={dur2 - FADE}:d={FADE},"
        f"adelay={int(ini_fecho * 1000)}|{int(ini_fecho * 1000)}[m2]"
    )
    filtro = (
        f"{seg1};{seg2};[m1][m2]amix=inputs=2:duration=longest:normalize=0,volume={ganho:.2f}dB[mus];"
        f"[0:a]asplit=2[v][vsc];[mus][vsc]{DUCKING}[duck];[v][duck]amix=inputs=2:duration=first:normalize=0,"
        f"alimiter=limit=0.89:level=false[a]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        entrada,
        "-i",
        str(FAIXA),
        "-filter_complex",
        filtro,
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        saida,
    ]
    r = run(cmd)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    print(f"ok {saida} | cenas {inicio} | total {total} s | ganho da faixa {ganho:.1f} dB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
