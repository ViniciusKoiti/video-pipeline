"""RF5: os scripts de resumo e de música são chamadores finos dos serviços; sem rede e sem ffmpeg."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.commands.errors import run as handled
from scripts.provisorio import catalogo_musica, formato_resumo, radar_resumo
from tests.test_briefs import EP, format_text, radar_text
from tests.test_music_library import PROBE


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "episodes" / EP).mkdir(parents=True)
    for module in (radar_resumo, formato_resumo, catalogo_musica):
        monkeypatch.setattr(module, "load_settings", lambda _root: SimpleNamespace(data_dir=tmp_path))
        monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(catalogo_musica, "duration_ms", PROBE.duration_ms)
    monkeypatch.setattr(catalogo_musica, "integrated_lufs", PROBE.lufs)
    monkeypatch.setattr(catalogo_musica, "intensity", PROBE.intensity)
    return tmp_path


def run(module: object, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    """O ponto de entrada real do script: `main` dentro do handler central (ADR 045)."""
    monkeypatch.setattr(sys, "argv", ["script", *argv])
    return handled("script", module.main)  # type: ignore[attr-defined]


def test_radar_resumo_installs_is_idempotent_refuses_a_swap_and_keeps_the_old_one(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    radar = root / "radar"
    (radar / "briefs").mkdir(parents=True)
    brief = radar / "briefs" / "n.json"
    args = (EP, "n", "--radar", str(radar))
    brief.write_text(radar_text("n", "2026-10-01T12:00:00+00:00"))
    assert run(radar_resumo, monkeypatch, *args) == 0
    assert "radar-brief.json: nicho n" in capsys.readouterr().out
    assert run(radar_resumo, monkeypatch, *args) == 0
    assert "já está atualizado" in capsys.readouterr().out
    brief.write_text(radar_text("n", "2026-10-12T03:21:19+00:00"))
    assert run(radar_resumo, monkeypatch, *args) == 1
    assert "use --atualizar para trocar" in capsys.readouterr().err
    assert run(radar_resumo, monkeypatch, *args, "--atualizar") == 0
    assert "resumo anterior guardado em radar-brief.20261001-120000.json" in capsys.readouterr().out
    assert (root / "episodes" / EP / "radar-brief.20261001-120000.json").is_file()


def test_radar_resumo_reports_a_missing_episode_and_a_brief_outside_the_contract(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    radar = root / "radar"
    (radar / "briefs").mkdir(parents=True)
    (radar / "briefs" / "n.json").write_text(radar_text("n"))
    assert run(radar_resumo, monkeypatch, "ep-fantasma", "n", "--radar", str(radar)) == 1
    assert "episódio ep-fantasma não existe" in capsys.readouterr().err
    assert not (root / "episodes" / "ep-fantasma").exists()


def test_formato_resumo_uses_the_data_dir_and_keeps_two_same_day_profiles(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, nicho in (("a", "a"), ("b", "b"), ("c", "c")):
        (root / f"{name}.json").write_text(format_text(nicho, "2026-10-18" if name != "c" else "2026-10-19"))
    assert run(formato_resumo, monkeypatch, EP, str(root / "a.json")) == 0
    assert (
        str(root / "episodes" / EP / "formato-brief.json") in capsys.readouterr().out
    )  # o data_dir das configurações
    assert run(formato_resumo, monkeypatch, EP, str(root / "b.json"), "--atualizar") == 0
    assert run(formato_resumo, monkeypatch, EP, str(root / "c.json"), "--atualizar") == 0
    folder = root / "episodes" / EP
    assert sorted(p.name for p in folder.glob("formato-brief*.json")) == [
        "formato-brief-2026-10-18.2.json",
        "formato-brief-2026-10-18.json",
        "formato-brief.json",
    ]


def test_catalogo_musica_adds_installs_and_refuses_what_it_must(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    track = root / "Alias.mp3"
    track.write_bytes(b"ID3-audio")
    add = ["adicionar", str(track), "--titulo", "Alias", "--clima", "calmo,foco", "--voz-cantada", "nao"]

    def music(*argv: str) -> int:
        monkeypatch.setattr(sys, "argv", ["script", *argv])
        return handled("script", lambda: catalogo_musica.main(list(argv)))

    assert music(*add) == 0
    assert "ytal-alias: 61 s, -18.0 LUFS, intensidade 3" in capsys.readouterr().out
    assert music(*add) == 1
    assert "ytal-alias já está no catálogo" in capsys.readouterr().err
    assert music("usar", EP, "ytal-alias") == 0
    assert "faixa e ativo copiados" in capsys.readouterr().out
    assert music("usar", EP, "ytal-alias") == 0
    assert "já está no episódio" in capsys.readouterr().out
    assert music("usar", EP, "ytal-nada") == 1
    assert "fora do catálogo" in capsys.readouterr().err
    assert music("listar") == 0
    assert "ytal-alias: 61 s, intensidade 3, calmo, foco" in capsys.readouterr().out
