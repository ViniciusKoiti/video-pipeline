"""Tempo por palavra de um clipe de letra: casa a letra (tag `lyrics` do MP3) com as palavras reconhecidas.

Provisório. Entrada: o MP3 e um ou mais JSON de palavras reconhecidas com tempo, em ordem de prioridade:
`{"palavras": [{w, ini, fim}]}`, com `janela: [a, b]` opcional, ou uma lista de janelas
`[{"janela": [a, b], "palavras": [...]}]`. Saída: o JSON que a composição `Clipe` do `video/` lê. Palavra que
o reconhecedor não casou recebe tempo interpolado (`ok: false`); o relatório lista os versos cujo início é
interpolado, para ajuste de ouvido em `AJUSTES`.

Uso: python scripts/provisorio/clipe_tempos.py musica.mp3 saida.json reconhecido.json [outro.json ...]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SECOES = {
    "Intro": "intro", "Verse 1": "verso", "Verse 2": "verso", "Pre-Chorus": "pre", "Chorus": "refrao",
    "Final Chorus": "refrao", "Bridge": "ponte", "Outro": "outro",
}
LONGA = 1.5  # s; nenhuma palavra cantada dura isso
# Início (s) de versos ajustado de ouvido, por índice do verso na letra. Vazio até a escuta do dono.
AJUSTES: dict[int, float] = {}


def norm(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in decomposed if unicodedata.category(c) != "Mn"))


def read_lyrics(mp3: Path) -> tuple[list[dict], float]:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:format_tags", "-of", "json", str(mp3)],
        check=True, capture_output=True, text=True,
    )
    fmt = json.loads(probe.stdout)["format"]
    text = next(v for k, v in fmt["tags"].items() if k.lower().startswith("lyrics"))
    lines, section, counts = [], "", {}
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith("["):
            section = SECOES[raw.strip("[]").split(":")[0]]
            counts[section] = counts.get(section, 0) + 1
            continue
        lines.append({"secao": section, "vez": counts[section], "texto": raw})
    return lines, float(fmt["duration"])


def read_recognized(paths: list[Path]) -> list[dict]:
    """Junta as fontes: cada janela é dona do trecho até o meio da sobreposição com a vizinha."""
    words: list[dict] = []
    covered: list[tuple[float, float]] = []
    for path in paths:
        data = json.loads(path.read_text())
        windows = data
        if isinstance(data, dict):
            windows = [{"janela": data.get("janela", [0.0, 1e9]), "palavras": data["palavras"]}]
        own = []
        for i, win in enumerate(windows):
            start, end = win["janela"]
            if i > 0:
                start = (start + windows[i - 1]["janela"][1]) / 2
            if i + 1 < len(windows):
                end = (end + windows[i + 1]["janela"][0]) / 2
            own.append((start, end))
            words += [
                w for w in win["palavras"]
                if start <= w["ini"] < end and norm(w["w"]) and not any(a <= w["ini"] < b for a, b in covered)
            ]
        covered += own
    # O reconhecedor estica a primeira palavra depois de um trecho sem voz: ela começa perto do próprio fim.
    for w in words:
        if w["fim"] - w["ini"] > LONGA:
            w["ini"] = round(w["fim"] - 0.4, 2)
    return sorted(words, key=lambda w: w["ini"])


def main() -> None:
    mp3, out, sources = Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]]
    lines, duration = read_lyrics(mp3)
    recognized = read_recognized(sources)
    tokens = [(i, w) for i, line in enumerate(lines) for w in line["texto"].split() if norm(w)]
    heard = [norm(w["w"]) for w in recognized]
    matcher = SequenceMatcher(None, [norm(w) for _, w in tokens], heard, autojunk=False)
    pairs: dict[int, int] = {}
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            pairs[a + k] = b + k
    times = {k: recognized[r] for k, r in pairs.items()}

    # Palavra não casada: se o reconhecedor ouviu algo no mesmo intervalo (ex.: "mata se" por "Mataste"), ela
    # herda o tempo da palavra ouvida na posição proporcional; sem nada ouvido, interpola entre as vizinhas.
    matched = sorted(pairs)
    starts: list[float] = []
    for k in range(len(tokens)):
        if k in pairs:
            starts.append(times[k]["ini"])
            continue
        before = max((m for m in matched if m < k), default=None)
        after = min((m for m in matched if m > k), default=None)
        lo = pairs[before] + 1 if before is not None else 0
        hi = pairs[after] if after is not None else len(recognized)
        first = before + 1 if before is not None else 0
        span = (after if after is not None else len(tokens)) - first
        if hi > lo:
            starts.append(recognized[lo + (k - first) * (hi - lo) // span]["ini"])
        elif before is None or after is None:
            starts.append(times[after]["ini"] if before is None else times[before]["fim"])
        else:
            t0, t1 = times[before]["fim"], times[after]["ini"]
            starts.append(round(t0 + (t1 - t0) * (k - before) / (after - before), 2))

    result = []
    for i, line in enumerate(lines):
        idx = [k for k, (li, _) in enumerate(tokens) if li == i]
        words = [{"t": tokens[k][1], "ini": starts[k], "ok": k in times} for k in idx]
        if i in AJUSTES:
            shift = AJUSTES[i] - words[0]["ini"]
            words = [{**w, "ini": round(w["ini"] + shift, 2), "ok": True} for w in words]
        last = idx[-1]
        end = times[last]["fim"] if last in times and i not in AJUSTES else words[-1]["ini"] + 0.4
        result.append({**line, "ini": words[0]["ini"], "fim": round(end, 2), "palavras": words})
        if not words[0]["ok"]:
            print(f"início interpolado: verso {i} em {words[0]['ini']:.2f} s: {line['texto']}")

    out.write_text(json.dumps({"duracao": duration, "linhas": result}, ensure_ascii=False, indent=1) + "\n")
    hits = sum(1 for k in range(len(tokens)) if k in times)
    print(f"{len(lines)} versos, {hits}/{len(tokens)} palavras casadas -> {out}")


if __name__ == "__main__":
    main()
