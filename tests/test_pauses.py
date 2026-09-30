"""Corte da narração de várias cenas nas pausas longas (ADR 012), com áudio sintético e sem rede."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.media.pauses import LEAD_S, TAIL_S, SplitError, boundaries, silences, split_at_pauses
from app.media.probe import duration_ms


def narration(path: Path, pieces: list[tuple[str, float]]) -> Path:
    """Tom (fala) e silêncio alternados: [("tom", 1.0), ("pausa", 0.3), ...]."""
    inputs: list[str] = []
    for kind, seconds in pieces:
        source = f"sine=frequency=220:sample_rate=24000:duration={seconds}" if kind == "tom" else (
            f"anullsrc=r=24000:cl=mono:d={seconds}"
        )
        inputs += ["-f", "lavfi", "-i", source]
    joined = "".join(f"[{i}:a]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", joined, "-map", "[a]",
                    "-ac", "1", "-c:a", "pcm_s16le", str(path)], check=True)
    return path


THREE_SCENES = [
    ("tom", 1.0), ("pausa", 0.3), ("tom", 0.8),  # cena 1, com uma respiração
    ("pausa", 1.2),
    ("tom", 1.0),  # cena 2
    ("pausa", 1.1),
    ("tom", 0.5), ("pausa", 0.4), ("tom", 0.5),  # cena 3
]


def test_the_longest_pauses_split_the_scenes(tmp_path: Path) -> None:
    audio = narration(tmp_path / "lote.wav", THREE_SCENES)
    assert len(silences(audio)) == 4
    outs = split_at_pauses(audio, [tmp_path / f"S0{i}.wav" for i in (1, 2, 3)])
    seconds = [duration_ms(p) / 1000 for p in outs]
    assert seconds[0] == pytest.approx(2.1 + TAIL_S, abs=0.06)
    assert seconds[1] == pytest.approx(LEAD_S + 1.0 + TAIL_S, abs=0.06)
    assert seconds[2] == pytest.approx(LEAD_S + 1.4, abs=0.06)


def test_a_boundary_that_does_not_stand_out_is_refused() -> None:
    with pytest.raises(SplitError, match="não se destaca"):
        boundaries([(1.0, 1.7), (3.0, 3.6)], parts=2)  # 0,7 s contra 0,6 s: pouca diferença
    with pytest.raises(SplitError, match="não se destaca"):
        boundaries([(1.0, 1.4)], parts=2)  # curta demais para ser fronteira
    with pytest.raises(SplitError, match="1 pausas para separar 3 cenas"):
        boundaries([(1.0, 2.0)], parts=3)


def test_one_scene_needs_no_cut() -> None:
    assert boundaries([(1.0, 1.3)], parts=1) == []
