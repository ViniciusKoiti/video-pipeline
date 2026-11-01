"""Conferência de áudio com o earshot (ADR 035, emenda de 2026-10-31): o que o ouvido do dono não mede.

O earshot (MIT, só CPU, offline depois do cache; termos em `data/benchmarks/termos-earshot.md`) vive num
ambiente próprio, apontado por `EARSHOT_PYTHON` no `.env`, como o Chatterbox. Aqui só se chama o `timeline`
dele por subprocesso e se lê o JSON: a loudness **como o YouTube mede** (mono contado nos dois alto-falantes,
BS.1770; o `ebur128` do ffmpeg mede um canal só e dá 3 dB a menos num Short mono), o pico real, a grade de
batidas da trilha e, para cada corte que passamos, se há um ataque de som perto dele. Não decide nada: devolve
medidas e a lista do que fugiu do alvo, para o `juntar` e para a prévia do dono.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Set
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.media.loudness import loudness_problem
from app.media.models._earshot_types import SYNC_TOLERANCE_MS as SYNC_TOLERANCE_MS
from app.media.models.audio_review import AudioReview as AudioReview
from app.media.models.cue_sync import CueSync as CueSync

MAX_TRUE_PEAK_DBTP = -1.0  # acima disso o encoder já passou do teto; o loudnorm pede −1,5


class EarshotError(RuntimeError):
    pass


def parse_review(data: dict[str, Any]) -> AudioReview:
    """O que usamos do JSON do `earshot timeline`."""
    loud = data.get("loudness") or {}
    music = data.get("music") or {}
    cues = ((data.get("sync") or {}).get("cues") or {})
    stats = cues.get("stats") or {}
    items = [
        CueSync(
            at_s=float(item["t"]),
            status=str(item.get("status", "")),
            offset_ms=None if item.get("offset_ms") is None else float(item["offset_ms"]),
            event=item.get("event"),
        )
        for item in cues.get("items") or []
    ]
    return AudioReview(
        duration_s=float(data.get("duration") or 0.0),
        integrated_lufs=float(loud["integrated_lufs"]),
        true_peak_dbtp=float(loud["true_peak_dbtp"]),
        tempo_bpm=None if music.get("tempo") is None else float(music["tempo"]),
        pulse_clarity=None if music.get("pulse_clarity") is None else float(music["pulse_clarity"]),
        cues=items,
        median_abs_offset_ms=stats.get("median_abs_offset_ms"),
        chance_within_tolerance=stats.get("chance_within_40ms"),
    )


def run_timeline(python: Path, media: Path, cuts: list[float], out: Path, threads: int = 4) -> dict[str, Any]:
    """Roda `earshot timeline` sobre `media` (áudio e vídeo do mesmo arquivo), com os nossos cortes como cues,
    offline, e devolve o JSON gravado em `out`. Carrega os modelos a cada chamada (~30 s)."""
    command = [str(python), "-m", "earshot", "timeline", str(media), "--video", str(media)]
    command += ["--json", "--out", str(out)]
    if cuts:
        command += ["--cues", ",".join(f"{cut:.3f}" for cut in cuts)]
    env = {**os.environ, "EARSHOT_OFFLINE": "1", "EARSHOT_THREADS": str(threads)}
    result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    if result.returncode != 0 or not out.is_file():
        raise EarshotError(f"earshot timeline falhou em {media.name}: {result.stderr.strip()[-300:]}")
    return TypeAdapter(dict[str, Any]).validate_json(out.read_text(encoding="utf-8"))


def review_problems(review: AudioReview, expected_hits: Set[float] = frozenset()) -> list[str]:
    """O que fugiu do alvo: loudness efetiva fora do alvo, pico real acima do teto e, nos cortes em que o
    plano pôs um som (`expected_hits`, em segundos), um corte sem ataque a 40 ms."""
    problems = []
    loud = loudness_problem(review.integrated_lufs)
    if loud:
        problems.append(f"volume efetivo (mono nos dois alto-falantes, como o YouTube mede): {loud}")
    if review.true_peak_dbtp > MAX_TRUE_PEAK_DBTP:
        problems.append(f"pico real {review.true_peak_dbtp:.1f} dBTP acima de {MAX_TRUE_PEAK_DBTP:.0f}")
    for cue in review.cues:
        if any(abs(cue.at_s - at) < 0.02 for at in expected_hits) and not cue.hit:
            where = "sem som" if cue.offset_ms is None else f"ataque a {cue.offset_ms:+.0f} ms"
            problems.append(f"corte em {cue.at_s:.2f} s tinha efeito no plano e ficou {where}")
    return problems
