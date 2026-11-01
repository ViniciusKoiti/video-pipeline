"""RF7: `vp assets` (search e take) usa a busca e a entrada de ativos; sem rede e sem banco real."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands import assets as command
from app.commands.errors import run as handled
from app.pipeline.models.archive_availability import ArchiveAvailability
from app.pipeline.models.skipped_archive import SkippedArchive
from app.pipeline.schemas import Asset
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.errors import PaidApiBlocked
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.test_assets import EP, Bank, make_asset


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path


def run(root: Path, *argv: str) -> int:
    """O caminho real do comando: parser do `vp`, `HANDLERS` e o handler central de erros (ADR 045)."""
    args = build_parser().parse_args(["assets", *argv])
    store = JsonFileStore(root / "episodes")
    settings = SimpleNamespace(data_dir=root)
    context = SimpleNamespace(store=store, review=JsonReviewGate(store), settings=settings)
    return handled("vp assets", lambda: HANDLERS["assets"](args, context))  # type: ignore[arg-type]


def banks(monkeypatch: pytest.MonkeyPatch, availability: ArchiveAvailability) -> None:
    monkeypatch.setattr(command, "available_archives", lambda settings: availability)


class RecordingBank(Bank):
    """O banco de mentira que também guarda as consultas que recebeu."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.queries: list[AssetQuery] = []

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]:
        self.queries.append(query)
        return super().search_assets(query)


def requests_file(root: Path) -> Path:
    path = root / "pedidos.json"
    path.write_text(json.dumps({"pedidos": [{"id": "cimento", "plano": "S01", "consultas": ["cimento"]}]}))
    return path


def test_search_with_no_available_bank_stops_without_writing_candidates(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    none = ArchiveAvailability((), (SkippedArchive("pexels", "PEXELS_API_KEY ausente"),))
    banks(monkeypatch, none)
    assert run(root, "search", EP, str(requests_file(root))) == 1
    assert "vp assets: nenhum banco disponível (pexels: PEXELS_API_KEY ausente)" in capsys.readouterr().err
    assert not (root / "episodes" / EP / "candidatos").exists()  # não é uma busca vazia


def test_search_records_failures_and_skipped_banks_in_the_candidates_file(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.providers.errors import QuotaExhausted

    good = Bank("pixabay", found=[make_asset("pixabay-video-9", provider="pixabay")])
    quota = Bank("pexels", error=QuotaExhausted("pexels", "limite"))
    avail = ArchiveAvailability((quota, good), (SkippedArchive("unsplash", "sem chave"),))
    banks(monkeypatch, avail)
    assert run(root, "search", EP, str(requests_file(root))) == 0
    saved = json.loads((root / "episodes" / EP / "candidatos" / "cimento.json").read_text())
    assert [c["ativo"]["id"] for c in saved["candidatos"]] == ["pixabay-video-9"]
    assert [(f["banco"], f["razao"]) for f in saved["falhas"]] == [("pexels", "quota_exhausted")]
    assert saved["bancos_pulados"] == [{"banco": "unsplash", "motivo": "sem chave"}]


def test_a_blocked_paid_provider_stops_the_search_with_a_message(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    avail = ArchiveAvailability((Bank("pexels", error=PaidApiBlocked("pexels", "plano pago")),))
    banks(monkeypatch, avail)
    assert run(root, "search", EP, str(requests_file(root))) == 1
    assert "vp assets: pexels: plano pago" in capsys.readouterr().err


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
    banks(monkeypatch, ArchiveAvailability((bank,)))
    codes = [run(root, "take", EP, scene, asset.id) for scene in ("S01", "S02", "S02")]
    assert codes == [0, 0, 0]  # repetir não é erro
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
    banks(monkeypatch, ArchiveAvailability((Bank("pexels"),)))
    assert run(root, "take", EP, "S01", "pexels-video-404", asset.id) == 1
    captured = capsys.readouterr()
    assert "pexels-video-404: ERRO" in captured.err and "não está em candidatos" in captured.err
    assert f"{asset.id}: baixado" in captured.out  # o outro ativo seguiu


def test_download_of_an_unavailable_bank_says_why(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    asset = make_asset(provider="pixabay")
    write_candidates(root, asset)
    avail = ArchiveAvailability((Bank("pexels"),), (SkippedArchive("pixabay", "PIXABAY_API_KEY ausente"),))
    banks(monkeypatch, avail)
    assert run(root, "take", EP, "S01", asset.id) == 1
    assert "o banco pixabay não está disponível (PIXABAY_API_KEY ausente)" in capsys.readouterr().err


def test_a_request_orientation_that_is_not_known_is_an_error_before_any_search(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bank = RecordingBank("pexels", found=[make_asset()])
    banks(monkeypatch, ArchiveAvailability((bank,)))
    path = root / "pedidos.json"
    path.write_text(json.dumps({"pedidos": [{"id": "a", "consultas": ["x"], "orientacao": "quadrada"}]}))
    assert run(root, "search", EP, str(path)) == 1
    assert "a: orientacao é landscape ou portrait, não 'quadrada'" in capsys.readouterr().err
    assert bank.queries == []


def test_the_search_uses_the_episode_orientation_and_a_request_can_override_it(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bank = RecordingBank("pexels", found=[make_asset()])
    banks(monkeypatch, ArchiveAvailability((bank,)))
    folder = root / "episodes" / EP
    folder.mkdir(parents=True)
    (folder / "scenes.json").write_text(json.dumps({"orientation": "portrait"}))
    path = root / "pedidos.json"
    pedidos = [{"id": "a", "consultas": ["x"]}, {"id": "b", "consultas": ["y"], "orientacao": "landscape"}]
    path.write_text(json.dumps({"pedidos": pedidos}))
    assert run(root, "search", EP, str(path), "--limit", "3") == 0
    assert [(q.text, q.orientation, q.limit) for q in bank.queries] == [
        ("x", "portrait", 3),
        ("y", "landscape", 3),
    ]
    assert "a (portrait): 1 candidatos" in capsys.readouterr().out


def test_the_minimum_duration_applies_only_to_video_queries(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bank = RecordingBank("pexels", found=[make_asset()])
    banks(monkeypatch, ArchiveAvailability((bank,)))
    path = root / "pedidos.json"
    pedido = {"id": "a", "consultas": ["x"], "midias": ["video", "photo"], "min_duration_s": 4}
    path.write_text(json.dumps({"pedidos": [pedido]}))
    assert run(root, "search", EP, str(path)) == 0
    assert [(q.media, q.min_duration_s) for q in bank.queries] == [("video", 4), ("photo", None)]
