"""Manifesto fora do contrato: o `JsonFileStore` levanta `ManifestInvalid` e os comandos saem com mensagem."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import BaseModel, ValidationError

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.errors import PipelineError
from app.pipeline.ports import ManifestInvalid, ManifestNotFound
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS

EP = "ep-invalido"


class Pair(BaseModel):
    name: str
    count: int


def store(tmp_path: Path) -> JsonFileStore:
    return JsonFileStore(tmp_path / "episodes")


def put(where: JsonFileStore, name: str, text: str) -> None:
    path = where.path(EP, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_field_out_of_the_contract_names_the_file_and_the_field(tmp_path: Path) -> None:
    where = store(tmp_path)
    put(where, "pair.json", '{"name": "x", "count": "muitos"}')
    with pytest.raises(ManifestInvalid) as caught:
        where.read(EP, "pair.json", Pair)
    error = caught.value
    assert str(error).startswith(f"{EP}/pair.json fora do contrato: count: ")
    assert error.details.startswith("count: ") and "integer" in error.details
    assert isinstance(error, PipelineError)
    assert isinstance(error, ValueError)  # quem pegava ValueError segue pegando
    assert isinstance(error.__cause__, ValidationError)  # o erro original fica na cadeia, para depurar


def test_broken_json_and_a_root_error_are_reported_without_a_field(tmp_path: Path) -> None:
    where = store(tmp_path)
    put(where, "pair.json", "{isto nao e json")
    with pytest.raises(ManifestInvalid, match=r"pair\.json fora do contrato: \(arquivo\): "):
        where.read(EP, "pair.json", Pair)
    put(where, "pair.json", "[1, 2]")
    with pytest.raises(ManifestInvalid, match=r"\(arquivo\): "):
        where.read(EP, "pair.json", Pair)


def test_only_the_first_five_problems_are_listed(tmp_path: Path) -> None:
    class Wide(BaseModel):
        a: int
        b: int
        c: int
        d: int
        e: int
        f: int
        g: int

    where = store(tmp_path)
    put(where, "wide.json", "{}")
    with pytest.raises(ManifestInvalid) as caught:
        where.read(EP, "wide.json", Wide)
    fields = [part.split(":")[0] for part in caught.value.details.split("; ")]
    assert fields == ["a", "b", "c", "d", "e"]


def test_a_missing_file_is_still_not_found_and_a_good_one_is_read(tmp_path: Path) -> None:
    where = store(tmp_path)
    with pytest.raises(ManifestNotFound):
        where.read(EP, "pair.json", Pair)
    put(where, "pair.json", '{"name": "x", "count": 2}')
    assert where.read(EP, "pair.json", Pair) == Pair(name="x", count=2)


def test_a_command_stops_with_a_short_message_on_an_invalid_scenes_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    where = store(tmp_path)
    put(where, "scenes.json", json.dumps({"episode_id": EP, "language": "pt-BR", "scenes": "nenhuma"}))
    tts = FakeBatchTTS()
    context = SimpleNamespace(store=where, tts=tts, tts_final=tts, tts_named=lambda name: tts)
    args = build_parser().parse_args(["voice", EP])
    assert handled("vp voice", lambda: HANDLERS["voice"](args, context)) == 1  # type: ignore[arg-type]
    err = capsys.readouterr().err
    assert err.startswith(f"vp voice: {EP}/scenes.json fora do contrato: scenes: ") and "Traceback" not in err
    assert tts.calls == []  # nenhuma voz antes de o contrato valer


def test_the_check_still_lists_the_problems_of_each_file(tmp_path: Path) -> None:
    from datetime import date

    from app.pipeline.check import check_episode

    where = store(tmp_path)
    put(where, "scenes.json", json.dumps({"episode_id": EP, "language": "pt-BR", "scenes": "nenhuma"}))
    report = check_episode(where, EP, region_codes=set(), chars_per_second=15.0, today=date(2026, 11, 1))
    assert any(line.startswith("scenes.json: scenes: ") for line in report.errors)


def test_an_unreadable_asset_is_not_approved_for_the_final_and_is_left_out_of_the_listing(
    tmp_path: Path,
) -> None:
    from app.pipeline.assembly import assembly_problems
    from app.pipeline.check import episode_assets
    from tests.test_assembly import EP as ASSEMBLY_EP
    from tests.test_assembly import Env

    env = Env(tmp_path)
    assert set(episode_assets(env.store, ASSEMBLY_EP)) == {"pexels-video-1", "pexels-video-2"}
    env.path("assets/pexels-video-1.json").write_text('{"id": 1}', encoding="utf-8")  # fora do contrato
    assert set(episode_assets(env.store, ASSEMBLY_EP)) == {"pexels-video-2"}  # fica de fora, sem erro
    problems = assembly_problems(env.store, ASSEMBLY_EP, env.scenes, env.episode, final=True)
    assert "ativo pexels-video-1: não aprovado no gate 3 (o render final exige)" in problems
