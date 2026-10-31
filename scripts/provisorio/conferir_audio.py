"""Conferência de áudio de um vídeo pronto com o earshot (ADR 035, emenda; provisório até virar `vp`).

Uso: `.venv/bin/python scripts/provisorio/conferir_audio.py <video.mp4>
      (--episodio=<id> | --content=<content.voz.json>) [--sfx=<sfx.json>] [--saida=<json>]`

- `--episodio=<id>`: vídeo longo; os cortes vêm do `episode.json` da pasta do episódio (`start_ms` de cada
  cena).
- `--content=<content.voz.json>`: Short por JSON do motion-video; os cortes vêm do começo de cada cena, com a
  mesma conta do `shorts_tec.py`. Com `--sfx`, os cortes em que o plano pôs um som no começo da cena precisam
  ter um ataque a 40 ms, senão é problema.
- Mede a loudness como o YouTube mede (mono contado nos dois alto-falantes), o pico real e a batida da trilha,
  e grava o JSON do earshot em `--saida` (padrão: `<video>.earshot.json`, ao lado do vídeo).

Roda só com pedido do dono e com a máquina livre (`cpu_probe()` antes: acima de 0,3 s a medida é inválida).
Precisa de `EARSHOT_PYTHON` no `.env` (termos e instalação em `data/benchmarks/termos-earshot.md`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media.earshot import EarshotError, parse_review, review_problems, run_timeline  # noqa: E402
from app.pipeline.bench import cpu_probe  # noqa: E402

CPU_LIMIT_S = 0.3


def cuts_from_episode(data_dir: Path, episode_id: str) -> list[float]:
    episode = json.loads((data_dir / "episodes" / episode_id / "episode.json").read_text(encoding="utf-8"))
    return [round(s["start_ms"] / 1000, 3) for s in episode["scenes"]][1:]


def cuts_from_content(content_file: Path) -> tuple[list[float], dict[str, float]]:
    from scripts.provisorio.shorts_tec import scene_starts

    starts = scene_starts(json.loads(content_file.read_text(encoding="utf-8")))
    return [round(t, 3) for t in list(starts.values())[1:]], starts


def expected_from_sfx(plan_file: Path, starts: dict[str, float]) -> set[float]:
    """Os cortes em que o plano de efeitos pôs um som no começo da cena (sem âncora de texto, até 0,3 s)."""
    from app.pipeline.sfx import SfxPlan

    plan = SfxPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    return {
        round(starts[cue.scene], 3)
        for cue in plan.cues
        if cue.text is None and cue.offset_s <= 0.3 and cue.scene in starts and starts[cue.scene] > 0
    }


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
    if len(args) != 1 or not ({"--episodio", "--content"} & set(flags)):
        raise SystemExit(__doc__)
    from app.bootstrap import build_context

    settings = build_context(ROOT).settings
    python = settings.earshot.python
    if python is None:
        raise SystemExit(
            "conferir_audio: configure EARSHOT_PYTHON no .env (data/benchmarks/termos-earshot.md)"
        )
    media = Path(args[0])
    expected: set[float] = set()
    if "--episodio" in flags:
        cuts = cuts_from_episode(settings.data_dir, flags["--episodio"])
    else:
        cuts, starts = cuts_from_content(Path(flags["--content"]))
        if "--sfx" in flags:
            expected = expected_from_sfx(Path(flags["--sfx"]), starts)
    probe = cpu_probe()
    if probe > CPU_LIMIT_S:
        raise SystemExit(
            f"conferir_audio: máquina limitada (sonda {probe:.2f} s > {CPU_LIMIT_S}); medida inválida"
        )
    out = Path(flags.get("--saida") or f"{media}.earshot.json")
    try:
        review = parse_review(run_timeline(python, media, cuts, out, settings.earshot.threads))
    except EarshotError as error:
        raise SystemExit(f"conferir_audio: {error}") from error
    beat = "sem batida"
    if review.has_beat:
        beat = f"{review.tempo_bpm:.0f} bpm, pulso {review.pulse_clarity:.2f}"
    chance = review.chance_within_tolerance
    hits = sum(c.hit for c in review.cues)
    print(
        f"conferir_audio: {media.name} ({review.duration_s:.1f} s) volume efetivo "
        f"{review.integrated_lufs:.1f} LUFS, pico {review.true_peak_dbtp:.1f} dBTP, trilha {beat}; "
        f"{len(cuts)} corte(s), {hits} com ataque a 40 ms"
        + (f" (acaso ~{chance:.0%})" if chance is not None else "")
    )
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


if __name__ == "__main__":
    raise SystemExit(main())
