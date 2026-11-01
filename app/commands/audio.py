"""`vp audio <video.mp4> (--episodio ID | --content content.voz.json) [--sfx sfx.json] [--saida JSON]`.

Conferência de áudio de um vídeo pronto com o earshot (ADR 035, emenda; RF7). Mede a loudness como o YouTube
mede (mono contado nos dois alto-falantes), o pico real e a batida da trilha, e grava o JSON do earshot em
`--saida` (padrão: `<video>.earshot.json`, ao lado do vídeo). Sai com 1 se algo fugiu do alvo.

- `--episodio ID`: vídeo longo; os cortes vêm do `episode.json` do episódio (`start_ms` de cada cena).
- `--content content.voz.json`: Short por JSON do motion-video; os cortes vêm do começo de cada cena, com a
  mesma conta do `vp short juntar`. Com `--sfx`, cada som colocado por deslocamento (começo da cena +
  `offset_s`) precisa ter um ataque a 40 ms de onde o kit diz que o ataque dele cai (momento − `sync.at` +
  `onset`), senão é problema; os cortes de cena entram na medida como informação.

Roda só com pedido do dono e com a máquina livre (`cpu_probe()` antes: acima de 0,3 s a medida é inválida).
Precisa de `EARSHOT_PYTHON` no `.env` (termos e instalação em `data/benchmarks/termos-earshot.md`).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.media.earshot import AudioReview, parse_review, review_problems, run_timeline
from app.pipeline.audio_review import (
    AudioReviewError,
    cuts_from_content,
    cuts_from_episode,
    expected_onsets,
)
from app.pipeline.bench import cpu_probe
from app.pipeline.constants.audio_review_constants import AudioReviewConstants
from app.pipeline.motion_inputs import load_content
from app.pipeline.ports import Context
from app.pipeline.sfx import load_kit, load_plan


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("video", type=Path, metavar="video.mp4")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--episodio", metavar="ID", help="vídeo longo: os cortes vêm do episode.json")
    source.add_argument("--content", type=Path, metavar="content.voz.json", help="Short por JSON do kit")
    parser.add_argument("--sfx", type=Path, metavar="sfx.json", help="plano de efeitos (só com --content)")
    parser.add_argument("--saida", type=Path, metavar="JSON", help="padrão: <video>.earshot.json")


def _cuts(args: argparse.Namespace, context: Context) -> tuple[list[float], set[float]]:
    if args.episodio:
        return cuts_from_episode(context.store.path(args.episodio, "episode.json")), set()
    cuts, starts = cuts_from_content(load_content(args.content))
    if not args.sfx:
        return cuts, set()
    expected = expected_onsets(load_plan(args.sfx), load_kit(context.settings.data_dir), starts)
    return sorted(set(cuts) | expected), expected  # sincronia nos cortes e nos momentos do plano


def _summary(media: Path, review: AudioReview, cuts: list[float]) -> str:
    beat = "sem batida"
    if review.has_beat:
        beat = f"{review.tempo_bpm:.0f} bpm, pulso {review.pulse_clarity:.2f}"
    chance = review.chance_within_tolerance
    hits = sum(c.hit for c in review.cues)
    return (
        f"audio: {media.name} ({review.duration_s:.1f} s) volume efetivo "
        f"{review.integrated_lufs:.1f} LUFS, pico {review.true_peak_dbtp:.1f} dBTP, trilha {beat}; "
        f"{len(cuts)} corte(s), {hits} com ataque a 40 ms"
        + (f" (acaso ~{chance:.0%})" if chance is not None else "")
    )


def run(args: argparse.Namespace, context: Context) -> int:
    settings = context.settings
    python = settings.earshot.python
    if python is None:
        raise AudioReviewError("configure EARSHOT_PYTHON no .env (data/benchmarks/termos-earshot.md)")
    cuts, expected = _cuts(args, context)
    probe = cpu_probe()
    if probe > AudioReviewConstants.CPU_LIMIT_S:
        limit = AudioReviewConstants.CPU_LIMIT_S
        raise AudioReviewError(f"máquina limitada (sonda {probe:.2f} s > {limit}); medida inválida")
    media = args.video
    out = args.saida or Path(f"{media}.earshot.json")
    review = parse_review(run_timeline(python, media, cuts, out, settings.earshot.threads))
    print(_summary(media, review, cuts))
    for cue in review.cues:
        mark = "ok " if cue.hit else "-- "
        offset = "sem som" if cue.offset_ms is None else f"{cue.offset_ms:+.0f} ms"
        planned = " (efeito no plano)" if any(abs(cue.at_s - at) < 0.02 for at in expected) else ""
        print(f"  {mark}{cue.at_s:7.2f} s  {offset:>9}  {cue.event or ''}{planned}")
    problems = review_problems(review, expected)
    for problem in problems:
        print(f"  problema: {problem}")
    print(f"json: {out}")
    return 1 if problems else 0
