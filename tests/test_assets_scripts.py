"""RF5: os scripts de ativos são chamadores finos do serviço; sem rede e sem banco real."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.pipeline.models.archive_availability import ArchiveAvailability
from app.pipeline.models.skipped_archive import SkippedArchive
from app.pipeline.schemas import Asset
from app.providers.errors import PaidApiBlocked
from scripts.provisorio import baixar_escolhidos, buscar_candidatos
from tests.test_assets import EP, Bank, make_asset


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for module in (baixar_escolhidos, buscar_candidatos):
        monkeypatch.setattr(module, "load_settings", lambda _root: SimpleNamespace(data_dir=tmp_path))
        monkeypatch.setattr(module, "ROOT", tmp_path)
    return tmp_path


def run(module: object, monkeypatch: pytest.MonkeyPatch, *argv: str) -> None:
    monkeypatch.setattr(sys, "argv", ["script", *argv])
    module.main()  # type: ignore[attr-defined]


def requests_file(root: Path) -> Path:
    path = root / "pedidos.json"
    path.write_text(json.dumps({"pedidos": [{"id": "cimento", "plano": "S01", "consultas": ["cimento"]}]}))
    return path


def test_search_with_no_available_bank_stops_without_writing_candidates(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    none = ArchiveAvailability((), (SkippedArchive("pexels", "PEXELS_API_KEY ausente"),))
    monkeypatch.setattr(buscar_candidatos, "available_archives", lambda settings: none)
    with pytest.raises(SystemExit, match="nenhum banco disponível.*pexels: PEXELS_API_KEY ausente"):
        run(buscar_candidatos, monkeypatch, EP, str(requests_file(root)))
    assert not (root / "episodes" / EP / "candidatos").exists()  # não é uma busca vazia


def test_search_records_failures_and_skipped_banks_in_the_candidates_file(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.providers.errors import QuotaExhausted

    good = Bank("pixabay", found=[make_asset("pixabay-video-9", provider="pixabay")])
    quota = Bank("pexels", error=QuotaExhausted("pexels", "limite"))
    avail = ArchiveAvailability((quota, good), (SkippedArchive("unsplash", "sem chave"),))
    monkeypatch.setattr(buscar_candidatos, "available_archives", lambda settings: avail)
    run(buscar_candidatos, monkeypatch, EP, str(requests_file(root)))
    saved = json.loads((root / "episodes" / EP / "candidatos" / "cimento.json").read_text())
    assert [c["ativo"]["id"] for c in saved["candidatos"]] == ["pixabay-video-9"]
    assert [(f["banco"], f["razao"]) for f in saved["falhas"]] == [("pexels", "quota_exhausted")]
    assert saved["bancos_pulados"] == [{"banco": "unsplash", "motivo": "sem chave"}]


def test_a_blocked_paid_provider_stops_the_search_with_a_message(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    avail = ArchiveAvailability((Bank("pexels", error=PaidApiBlocked("pexels", "plano pago")),))
    monkeypatch.setattr(buscar_candidatos, "available_archives", lambda settings: avail)
    with pytest.raises(SystemExit, match="provedor pago bloqueado"):
        run(buscar_candidatos, monkeypatch, EP, str(requests_file(root)))


def write_candidates(root: Path, asset: Asset) -> None:
    folder = root / "episodes" / EP / "candidatos"
    folder.mkdir(parents=True)
    (folder / "cimento.json").write_text(
        json.dumps({"candidatos": [{"ativo": asset.model_dump(mode="json")}]})
    )


def test_download_keeps_earlier_scenes_and_a_repeat_is_not_an_error(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    asset, bank = make_asset(), Bank("pexels")
    write_candidates(root, asset)
    monkeypatch.setattr(
        baixar_escolhidos, "available_archives", lambda settings: ArchiveAvailability((bank,))
    )
    run(baixar_escolhidos, monkeypatch, EP, "S01", asset.id)
    run(baixar_escolhidos, monkeypatch, EP, "S02", asset.id)
    run(baixar_escolhidos, monkeypatch, EP, "S02", asset.id)
    out = capsys.readouterr().out
    assert "baixado; cenas ['S01']" in out and "cena acrescentada; cenas ['S01', 'S02']" in out
    assert "nada a fazer" in out and bank.downloads == [asset.id]
    saved = json.loads((root / "episodes" / EP / "assets" / f"{asset.id}.json").read_text())
    assert saved["used_in_scenes"] == ["S01", "S02"]


def test_download_reports_each_failure_and_exits_nonzero_without_stopping_the_others(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    asset = make_asset()
    write_candidates(root, asset)
    monkeypatch.setattr(
        baixar_escolhidos, "available_archives", lambda settings: ArchiveAvailability((Bank("pexels"),))
    )
    with pytest.raises(SystemExit) as stopped:
        run(baixar_escolhidos, monkeypatch, EP, "S01", "pexels-video-404", asset.id)
    assert stopped.value.code == 1
    captured = capsys.readouterr()
    assert "pexels-video-404: ERRO" in captured.err and "não está em candidatos" in captured.err
    assert f"{asset.id}: baixado" in captured.out  # o outro ativo seguiu


def test_download_of_an_unavailable_bank_says_why(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    asset = make_asset(provider="pixabay")
    write_candidates(root, asset)
    avail = ArchiveAvailability((Bank("pexels"),), (SkippedArchive("pixabay", "PIXABAY_API_KEY ausente"),))
    monkeypatch.setattr(baixar_escolhidos, "available_archives", lambda settings: avail)
    with pytest.raises(SystemExit):
        run(baixar_escolhidos, monkeypatch, EP, "S01", asset.id)
    assert "o banco pixabay não está disponível (PIXABAY_API_KEY ausente)" in capsys.readouterr().err
