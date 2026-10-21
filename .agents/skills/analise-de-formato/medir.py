"""Mede os vídeos baixados por `baixar.py`: fala, ritmo de edição e folha de quadros.

Uso: python3 -I medir.py <pasta>

Para cada `<id>.info.json` da pasta, grava:
- `<id>.txt`: a transcrição com o minuto e o segundo de cada linha, sem as repetições da legenda automática;
- `<id>_folha.jpg`: 32 quadros espalhados pelo vídeo (8×4), para ver o estilo visual;
- `<id>.cortes.txt`: o segundo de cada corte (cache; refeito se o vídeo mudar);
- uma linha em `medidas.csv` (e `medidas.json`) e uma linha por janela de 30 s em `janelas.csv`.

Medidas da fala, por mil palavras: "você" (você, vocês), "a gente" (a gente, nós, nosso, nossa), "eu" (eu,
meu,
minha, pra mim, acho) e fonte citada (segundo, de acordo com, estudo, pesquisa, pesquisadores, artigo).
Corte =
mudança de cena acima de 0,3 no ffmpeg. A legenda automática não tem pontuação, então perguntas não são
contadas, e as palavras de uma linha caem na janela em que a linha começa. Precisa de ffmpeg. Mesma pasta,
mesmas
medidas.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

SCENE_THRESHOLD = 0.3
WINDOW_S = 30
PATTERNS = {
    "voce": re.compile(r"\b(você|vocês|voce|voces)\b", re.I),
    "nos": re.compile(r"\b(a gente|nós|nosso|nossa|nossos|nossas)\b", re.I),
    "eu": re.compile(r"\b(eu|meu|minha|pra mim|para mim|acho)\b", re.I),
    "fonte": re.compile(
        r"\b(segundo|de acordo com|estudo|estudos|pesquisa|pesquisas|pesquisadores|artigo)\b", re.I
    ),
}


def seconds(stamp: str) -> float:
    hours, minutes, rest = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def caption_lines(path: Path) -> list[tuple[float, str]]:
    """A legenda automática repete cada linha na entrada seguinte; fica só a primeira vez, com o tempo
    dela."""
    lines, seen, start = [], set(), 0.0
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        cue = re.match(r"(\d+:\d+:\d+\.\d+) -->", raw)
        if cue:
            start = seconds(cue.group(1))
            continue
        text = re.sub(r"<[^>]+>", "", raw).strip()
        if not text or text == "WEBVTT" or text.startswith(("Kind:", "Language:", "NOTE")) or text in seen:
            continue
        seen.add(text)
        lines.append((start, text))
    return lines


def pick_caption(folder: Path, video_id: str, meta: dict) -> Path | None:
    """Legenda do autor em pt, senão a automática original (`pt-orig`), senão `pt`. Nunca uma tradução
    automática (`pt-PT`, `pt-PT-pt-BR`), que reescreve a fala. Vídeo falado em outra língua fica sem
    legenda."""
    authored = [lang for lang in (meta.get("subtitles") or {}) if lang in ("pt", "pt-BR")]
    spoken = (meta.get("language") or "pt").lower()
    automatic = (
        ["pt-orig", "pt-BR", "pt"] if spoken.startswith("pt") else []
    )  # fora do pt, o automático é tradução
    for lang in [*authored, *automatic]:
        path = folder / f"{video_id}.{lang}.vtt"
        if path.exists():
            return path
    return None


def cut_times(video: Path) -> list[float]:
    cache = video.with_suffix(".cortes.txt")
    if cache.exists() and cache.stat().st_mtime >= video.stat().st_mtime:
        content = cache.read_text().split()
        if not content or "." in content[0]:  # formato antigo (só a contagem) é refeito
            return [float(t) for t in content]
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(video),
            "-vf",
            f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    times = [float(t) for t in re.findall(r"pts_time:([\d.]+)", result.stderr)]
    cache.write_text("\n".join(f"{t:.3f}" for t in times) + "\n")
    return times


def contact_sheet(video: Path, duration: float, out: Path) -> None:
    step = max(duration / 32, 1)
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"fps=1/{step:.3f},scale=320:-2,tile=8x4",
            "-frames:v",
            "1",
            str(out),
        ],
        check=False,
    )


def counts(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in PATTERNS.items()}


def per_thousand(value: int, words: int) -> float:
    return round(value / max(words, 1) * 1000, 1)


def main() -> None:
    folder = Path(sys.argv[1])
    videos, windows = {}, []
    for info in sorted(folder.glob("*.info.json")):
        video_id = info.name.removesuffix(".info.json")
        meta = json.loads(info.read_text(encoding="utf-8"))
        duration = float(meta.get("duration") or 0) or 1.0
        caption = pick_caption(folder, video_id, meta)
        lines = caption_lines(caption) if caption else []
        (folder / f"{video_id}.txt").write_text(
            "\n".join(f"[{int(t // 60):02d}:{int(t % 60):02d}] {text}" for t, text in lines), encoding="utf-8"
        )
        video = folder / f"{video_id}.mp4"
        cuts = None
        if video.exists():
            cuts = cut_times(video)
            sheet = folder / f"{video_id}_folha.jpg"
            if not sheet.exists():
                contact_sheet(video, duration, sheet)

        text = " ".join(t for _, t in lines)
        words = len(text.split())
        found = counts(text)
        opening = " ".join(t for start, t in lines if start < 60)
        opening_found = counts(opening)
        authored = [lang for lang in (meta.get("subtitles") or {}) if lang in ("pt", "pt-BR")]
        videos[video_id] = {
            "canal": meta.get("channel"),
            "idioma": meta.get("language"),
            "inscritos": meta.get("channel_follower_count"),
            "views": meta.get("view_count"),
            "publicado": meta.get("upload_date"),
            "duracao_s": round(duration),
            "legenda": "autor" if authored else ("automatica" if caption else "nenhuma"),
            "arquivo_legenda": caption.name if caption else None,
            "palavras": words,
            "palavras_min": round(words / duration * 60),
            "cortes_min": round(len(cuts) / duration * 60, 1) if cuts is not None else None,
            "plano_medio_s": round(duration / len(cuts), 1) if cuts else None,
            **{f"{name}_por_mil": per_thousand(n, words) for name, n in found.items()},
            "palavras_60s": len(opening.split()),
            "voce_60s": opening_found["voce"],
            "cortes_60s": sum(1 for t in cuts if t < 60) if cuts is not None else None,
            "capitulos": len(meta.get("chapters") or []),
            "titulo": meta.get("title"),
            "abertura_60s": opening,
        }
        for index in range(int(duration // WINDOW_S) + 1):
            start, end = index * WINDOW_S, min((index + 1) * WINDOW_S, duration)
            if end - start < 10:
                continue
            chunk = " ".join(t for s, t in lines if start <= s < end)
            found = counts(chunk)
            windows.append(
                {
                    "video_id": video_id,
                    "janela": index,
                    "inicio_s": start,
                    "posicao": round(start / duration, 3),
                    "palavras": len(chunk.split()),
                    "palavras_min": round(len(chunk.split()) / (end - start) * 60),
                    "cortes_min": round(sum(1 for t in cuts if start <= t < end) / (end - start) * 60, 1)
                    if cuts is not None
                    else None,
                    **{name: n for name, n in found.items()},
                }
            )

    (folder / "medidas.json").write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
    columns = [c for c in next(iter(videos.values()), {}) if c != "abertura_60s"]
    with (folder / "medidas.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["video_id", *columns])
        for video_id, row in videos.items():
            writer.writerow([video_id, *(row[c] for c in columns)])
    if windows:
        with (folder / "janelas.csv").open("w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=list(windows[0]))
            writer.writeheader()
            writer.writerows(windows)
    for video_id, row in videos.items():
        print(
            f"{video_id}\t{row['canal']}\t{row['duracao_s']} s\t{row['palavras_min']} pal/min\t"
            f"{row['cortes_min']} cortes/min\tvocê {row['voce_por_mil']}/mil\teu {row['eu_por_mil']}/mil"
        )


if __name__ == "__main__":
    main()
