"""RF7: `vp briefs` e `vp music` usam os serviços de resumo e de catálogo; sem rede e sem ffmpeg."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands import music
from app.commands.errors import run as handled
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.test_briefs import EP, format_text, radar_text
from tests.test_music_library import PROBE


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "episodes" / EP).mkdir(parents=True)
    monkeypatch.setattr(music, "duration_ms", PROBE.duration_ms)
    monkeypatch.setattr(music, "integrated_lufs", PROBE.lufs)
    monkeypatch.setattr(music, "intensity", PROBE.intensity)
    return tmp_path


def run(root: Path, *argv: str) -> int:
    """O caminho real do comando: parser do `vp`, `HANDLERS` e o handler central de erros (ADR 045)."""
    args = build_parser().parse_args(list(argv))
    store = JsonFileStore(root / "episodes")
    settings = SimpleNamespace(data_dir=root)
    context = SimpleNamespace(store=store, review=JsonReviewGate(store), settings=settings)
    return handled(f"vp {argv[0]}", lambda: HANDLERS[argv[0]](args, context))  # type: ignore[arg-type]


def test_briefs_radar_installs_is_idempotent_refuses_a_swap_and_keeps_the_old_one(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    radar = root / "radar"
    (radar / "briefs").mkdir(parents=True)
    brief = radar / "briefs" / "n.json"
    args = ("briefs", "radar", EP, "n", "--radar", str(radar))
    brief.write_text(radar_text("n", "2026-10-01T12:00:00+00:00"))
    assert run(root, *args) == 0
    assert "radar-brief.json: nicho n" in capsys.readouterr().out
    assert run(root, *args) == 0
    assert "já está atualizado" in capsys.readouterr().out
    brief.write_text(radar_text("n", "2026-10-12T03:21:19+00:00"))
    assert run(root, *args) == 1
    assert "use --atualizar para trocar" in capsys.readouterr().err
    assert run(root, *args, "--atualizar") == 0
    assert "resumo anterior guardado em radar-brief.20261001-120000.json" in capsys.readouterr().out
    assert (root / "episodes" / EP / "radar-brief.20261001-120000.json").is_file()


def test_briefs_radar_reports_a_missing_episode_and_a_brief_outside_the_contract(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    radar = root / "radar"
    (radar / "briefs").mkdir(parents=True)
    (radar / "briefs" / "n.json").write_text(radar_text("n"))
    assert run(root, "briefs", "radar", "ep-fantasma", "n", "--radar", str(radar)) == 1
    assert "episódio ep-fantasma não existe" in capsys.readouterr().err
    assert not (root / "episodes" / "ep-fantasma").exists()


def test_briefs_formato_uses_the_data_dir_and_keeps_two_same_day_profiles(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, nicho in (("a", "a"), ("b", "b"), ("c", "c")):
        (root / f"{name}.json").write_text(format_text(nicho, "2026-10-18" if name != "c" else "2026-10-19"))
    assert run(root, "briefs", "formato", EP, str(root / "a.json")) == 0
    assert (
        str(root / "episodes" / EP / "formato-brief.json") in capsys.readouterr().out
    )  # o data_dir das configurações
    assert run(root, "briefs", "formato", EP, str(root / "b.json"), "--atualizar") == 0
    assert run(root, "briefs", "formato", EP, str(root / "c.json"), "--atualizar") == 0
    folder = root / "episodes" / EP
    assert sorted(p.name for p in folder.glob("formato-brief*.json")) == [
        "formato-brief-2026-10-18.2.json",
        "formato-brief-2026-10-18.json",
        "formato-brief.json",
    ]


def test_music_adds_installs_and_refuses_what_it_must(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    track = root / "Alias.mp3"
    track.write_bytes(b"ID3-audio")
    add = ["adicionar", str(track), "--titulo", "Alias", "--clima", "calmo,foco", "--voz-cantada", "nao"]

    def vp_music(*argv: str) -> int:
        return run(root, "music", *argv)

    assert vp_music(*add) == 0
    assert "ytal-alias: 61 s, -18.0 LUFS, intensidade 3" in capsys.readouterr().out
    assert vp_music(*add) == 1
    assert "ytal-alias já está no catálogo" in capsys.readouterr().err
    assert vp_music("usar", EP, "ytal-alias") == 0
    assert "faixa e ativo copiados" in capsys.readouterr().out
    assert vp_music("usar", EP, "ytal-alias") == 0
    assert "já está no episódio" in capsys.readouterr().out
    assert vp_music("usar", EP, "ytal-nada") == 1
    assert "fora do catálogo" in capsys.readouterr().err
    assert vp_music("listar") == 0
    assert "ytal-alias: 61 s, intensidade 3, calmo, foco" in capsys.readouterr().out


def test_briefs_radar_needs_the_radar_folder_and_the_brief_file(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("RADAR_DIR", raising=False)
    assert run(root, "briefs", "radar", EP, "n") == 1
    assert "pasta do reels-radar ausente: use --radar ou RADAR_DIR no .env" in capsys.readouterr().err
    (root / "radar" / "briefs").mkdir(parents=True)
    assert run(root, "briefs", "radar", EP, "n", "--radar", str(root / "radar")) == 1
    assert "gere com `radar brief niches/n.toml` no reels-radar" in capsys.readouterr().err


def test_briefs_radar_reads_the_folder_from_the_environment(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / "radar" / "briefs").mkdir(parents=True)
    (root / "radar" / "briefs" / "n.json").write_text(radar_text("n"))
    monkeypatch.setenv("RADAR_DIR", str(root / "radar"))
    assert run(root, "briefs", "radar", EP, "n") == 0
    assert (root / "episodes" / EP / "radar-brief.json").is_file()
    assert "nicho n" in capsys.readouterr().out


def test_briefs_formato_says_which_measures_are_patterns(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / "p.json").write_text(format_text("a"))
    assert run(root, "briefs", "formato", EP, str(root / "p.json")) == 0
    out = capsys.readouterr().out
    assert out.endswith("pattern: voce_por_mil\n") and ": a, grupo " in out


def test_music_keeps_the_sung_voice_and_the_loop_flags_in_the_catalog(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    track = root / "Cantada.mp3"
    track.write_bytes(b"ID3-audio-2")
    args = ["music", "adicionar", str(track), "--titulo", "Cantada", "--clima", "alegre", "--bpm", "90"]
    assert run(root, *args, "--voz-cantada", "sim", "--loop") == 0
    capsys.readouterr()
    assert run(root, "music", "listar") == 0
    assert "ytal-cantada: 61 s, intensidade 3, alegre, voz cantada, loop" in capsys.readouterr().out
