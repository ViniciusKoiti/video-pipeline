"""Evolução do template: versões do vídeo-régua, registro e comparação, com vídeos minúsculos e sem rede."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.media import evolution
from app.media.probe import dimensions
from app.pipeline.schemas import EpisodeFormat, EpisodeManifest, EpisodeScene, EpisodeShot, KeywordShot

NARRATION = "um dois três quatro"


def video(path: Path, color: str, seconds: float = 2.0, then: str | None = None) -> Path:
    """Vídeo de uma cor; com `then`, a segunda metade tem outra cor."""
    half = seconds / 2
    colors = [(color, seconds)] if then is None else [(color, half), (then, half)]
    inputs = [arg for c, d in colors for arg in ("-f", "lavfi", "-i", f"color=c={c}:s=320x180:r=10:d={d}")]
    joined = "".join(f"[{i}:v]" for i in range(len(colors))) + f"concat=n={len(colors)}:v=1:a=0[v]"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", joined, "-map", "[v]", "-map", f"{len(colors)}:a", "-t", str(seconds),
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", str(path)],
        check=True,
    )
    return path


def keyword(text: str) -> KeywordShot:
    return KeywordShot(anchor=text, text=text)


def episode(shots_per_scene: tuple[int, ...] = (2, 1), scene_ms: int = 1000) -> EpisodeManifest:
    scenes, cursor = [], 0
    for number, count in enumerate(shots_per_scene, start=1):
        step = scene_ms // count
        shots = [
            EpisodeShot(start_ms=i * step, duration_ms=step if i < count - 1 else scene_ms - i * step,
                        spec=keyword(NARRATION.split()[i]))
            for i in range(count)
        ]
        scenes.append(EpisodeScene(id=f"S{number:02d}", start_ms=cursor, duration_ms=scene_ms,
                                   narration=NARRATION, audio=f"voice/S{number:02d}.wav", shots=shots))
        cursor += scene_ms
    return EpisodeManifest(schema_version=2, episode_id="regua", title="régua", language="pt-BR",
                           format=EpisodeFormat.EXPLAINER, scenes=scenes)


def store(render: Path, folder: Path, note: str = "mudança", **extra: object) -> evolution.Version:
    return evolution.store(render, episode(), folder, commit="abc1234", template_hash="f" * 64,
                           motion_kit="2af5a7e", note=note, **extra)  # type: ignore[arg-type]


def test_one_sample_per_shot_at_seventy_percent() -> None:
    found = evolution.samples(episode())
    assert [(s.key, s.kind, s.at_ms) for s in found] == [
        ("S01#1", "keyword", 350), ("S01#2", "keyword", 850), ("S02#1", "keyword", 1700),
    ]


def test_motion_kit_sha_comes_from_package_json() -> None:
    package = '{"dependencies": {"@viniciusk/motion-kit": "https://x/archive.tar.gz?sha=2af5a7eaacc5349b2b70"}}'
    assert evolution.motion_kit_sha(package) == "2af5a7e"
    with pytest.raises(evolution.EvolutionError):
        evolution.motion_kit_sha('{"dependencies": {}}')


def test_versions_are_numbered_and_sorted_numerically(tmp_path: Path) -> None:
    for name in ("v1", "v10", "v2", "folha", "v3-v4"):
        (tmp_path / f"{name}.json").write_text("{}")
    assert evolution.versions(tmp_path) == ["v1", "v2", "v10"]


def test_store_copies_render_and_refuses_the_same_render_twice(tmp_path: Path) -> None:
    folder = tmp_path / "evolucao"
    first = store(video(tmp_path / "a.mp4", "navy"), folder, render_s=180, cpu_probe_s=0.05)
    assert first.name == "v1" and (folder / "v1.mp4").is_file()
    assert evolution.load(folder, "v1") == first
    with pytest.raises(evolution.EvolutionError, match="igual à v1"):
        store(tmp_path / "a.mp4", folder)
    second = store(video(tmp_path / "b.mp4", "darkred"), folder)
    assert second.name == "v2" and evolution.versions(folder) == ["v1", "v2"]


def test_store_refuses_a_render_that_does_not_match_the_episode(tmp_path: Path) -> None:
    with pytest.raises(evolution.EvolutionError, match="não é o deste render"):
        store(video(tmp_path / "long.mp4", "navy", seconds=4), tmp_path / "evolucao")


def test_registry_starts_with_the_header_and_escapes_pipes(tmp_path: Path) -> None:
    folder, registry = tmp_path / "evolucao", tmp_path / "evolucao-template.md"
    evolution.append_registry(registry, store(video(tmp_path / "a.mp4", "navy"), folder, render_s=180.4,
                                              cpu_probe_s=0.05))
    evolution.append_registry(registry, store(video(tmp_path / "b.mp4", "darkred"), folder, note="a | b"))
    lines = registry.read_text().splitlines()
    assert registry.read_text().startswith(evolution.REGISTRY_HEADER)
    assert lines[-2] == ("| v1 | `regua` | " + evolution.load(folder, "v1").rendered_at
                         + " | `abc1234` | `2af5a7e` | `ffffffffffff` | 180 s | 0,05 s | — | mudança |")
    assert lines[-1].endswith("| — | — | S01 plano 1, S01 plano 2, S02 plano 1 | a \\| b |")


def test_only_the_shots_whose_frame_changed_are_marked(tmp_path: Path) -> None:
    folder = tmp_path / "evolucao"
    first = store(video(tmp_path / "a.mp4", "navy", then="darkred"), folder)
    second = store(video(tmp_path / "b.mp4", "navy", then="darkgreen"), folder)
    assert first.changed is None  # a primeira versão não tem com o que comparar
    assert second.changed == ["S02#1"]  # S01 fica no primeiro segundo, igual nas duas
    assert evolution.load(folder, "v2").changed == ["S02#1"]


def test_contact_sheet_has_one_row_per_shot_and_one_column_per_version(tmp_path: Path) -> None:
    folder = tmp_path / "evolucao"
    store(video(tmp_path / "a.mp4", "navy", then="darkred"), folder)
    store(video(tmp_path / "b.mp4", "navy", then="darkgreen"), folder)
    out = folder / "folha.jpg"
    assert evolution.contact_sheet(folder, ["v1", "v2"], out) == {"v2": ["S02#1"]}
    assert dimensions(out) == (evolution.LABEL_W + 2 * evolution.CELL_W,
                               evolution.HEADER_H + 3 * evolution.CELL_H)


def test_side_by_side_puts_both_versions_in_one_video(tmp_path: Path) -> None:
    folder = tmp_path / "evolucao"
    store(video(tmp_path / "a.mp4", "navy"), folder)
    store(video(tmp_path / "b.mp4", "darkred"), folder)
    out = evolution.side_by_side(folder, "v1", "v2", folder / "v1-v2.mp4")
    assert dimensions(out) == (2 * evolution.SIDE_W, evolution.SIDE_H)


def test_unknown_version_is_a_clear_error(tmp_path: Path) -> None:
    with pytest.raises(evolution.EvolutionError, match="v7 não existe"):
        evolution.load(tmp_path, "v7")
