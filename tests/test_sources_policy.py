"""Regime de fontes (ADR 056): schema, `vp check`, rodapé e `vp status` obedecem ao que o roteiro declara."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.cli import main
from app.pipeline.check import check_episode
from app.pipeline.schemas import ScenesManifest
from app.pipeline.sources_policy import footer_sources, policy_summary, policy_warnings
from app.storage.json_files import JsonFileStore
from tests.fakes import make_root
from tests.test_assembly import scenes_manifest
from tests.test_molde_check import PROPER, scenes, write_episode
from tests.test_render_command import EP, Env, run

NUMBER: dict[str, Any] = {"kind": "number", "anchor": "mil", "value": "1000", "label": "operários"}
CLAIM = {"text": "mil operários", "source_ids": ["source-01"]}


def script(policy: str | None = None, *, claims: bool = False, **extra: Any) -> dict[str, Any]:
    shot = {**NUMBER, **({"claims": [CLAIM]} if claims else {})}
    raw: dict[str, Any] = {
        "episode_id": "ep",
        "language": "pt-BR",
        "scenes": [{"id": "S01", "narration": "Eram mil operários na fábrica.", "shots": [shot]}],
        **extra,
    }
    if policy is not None:
        raw["sources_policy"] = policy
    return raw


def with_policy(manifest: ScenesManifest, policy: str, **extra: Any) -> ScenesManifest:
    raw = {**manifest.model_dump(mode="json"), "sources_policy": policy, **extra}
    return ScenesManifest.model_validate(raw)


# --- schema ------------------------------------------------------------------------------------------


def test_the_default_policy_is_documental_and_screen_facts_need_claims() -> None:
    assert ScenesManifest.model_validate(script(claims=True)).sources_policy == "documental"
    with pytest.raises(ValidationError, match=r"S01: number \('mil'\) na tela sem claim .*regime documental"):
        ScenesManifest.model_validate(script())
    with pytest.raises(ValidationError, match="regime ensaio"):
        ScenesManifest.model_validate(script("ensaio"))


def test_the_entertainment_policy_accepts_screen_facts_without_claims() -> None:
    parsed = ScenesManifest.model_validate(script("entretenimento"))
    assert parsed.sources_policy == "entretenimento" and parsed.scenes[0].shots[0].claims == []
    with pytest.raises(ValidationError, match="sources_policy"):
        ScenesManifest.model_validate(script("humor"))


# --- vp check --------------------------------------------------------------------------------------


def test_claimless_sentences_only_warn_in_the_documental_policy(tmp_path: Path) -> None:
    documental = scenes(PROPER)
    assert any("frase afirmativa em cena sem claims" in w for w in policy_warnings(documental))
    assert policy_warnings(with_policy(documental, "ensaio")) == []
    assert policy_warnings(with_policy(documental, "entretenimento")) == []
    assert policy_summary(with_policy(documental, "ensaio")).startswith("regime de fontes: ensaio (fichas")
    report = check_episode(write_episode(tmp_path, None, with_policy(documental, "ensaio")), "ep")
    assert report.ok and not any("frase afirmativa" in w for w in report.warnings)
    assert any(line.startswith("regime de fontes: ensaio") for line in report.checked)


def test_entertainment_with_a_news_objective_reminds_the_living_people_rule() -> None:
    news = {"kinds": ["noticiar"], "promise": "o que aconteceu", "event_date": "2026-11-01"}
    manifest = with_policy(scenes(PROPER), "entretenimento", objective=news)
    [warning] = policy_warnings(manifest)
    assert warning.startswith("regime entretenimento com objetivo noticiar")
    assert policy_warnings(with_policy(scenes(PROPER), "ensaio", objective=news)) == []


# --- rodapé ------------------------------------------------------------------------------------------


def test_the_footer_source_only_appears_in_the_documental_policy(env: Env, tmp_path: Path) -> None:
    sources = Path("tests/fixtures/episodes/pilot-example/sources.json")
    env.path("sources.json").write_text(sources.read_text())
    script_raw = json.loads(env.path("scenes.json").read_text())
    keyword = {"kind": "keyword", "text": "Primeira", "anchor": "Primeira", "claims": [CLAIM]}
    script_raw["scenes"][0]["shots"] = [keyword]
    for policy, expected in (("documental", True), ("ensaio", False), ("entretenimento", False)):
        env.path("scenes.json").write_text(json.dumps({**script_raw, "sources_policy": policy}))
        assert run(env, tmp_path, "--no-render") == 0
        shot = json.loads(env.path("episode.json").read_text())["scenes"][0]["shots"][0]
        assert bool(shot.get("source")) is expected, policy
    manifest = ScenesManifest.model_validate({**script_raw, "sources_policy": "ensaio"})
    assert footer_sources(manifest, None) is None


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


# --- vp status ---------------------------------------------------------------------------------------


def test_vp_status_shows_the_declared_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    store = JsonFileStore(root / "data" / "episodes")
    store.path(EP, "").mkdir(parents=True, exist_ok=True)
    store.write(EP, "scenes.json", with_policy(scenes_manifest(), "ensaio"))
    monkeypatch.chdir(root)
    assert main(["status", EP]) == 0
    out = capsys.readouterr().out
    assert "fontes regime ensaio" in out and "fonte só na descrição" in out
