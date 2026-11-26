"""Especulação declarada por cena (ADR 065, série "E se…?"): a cena `especulacao` dispensa claims na fala; o
dado na tela pede claims ou `estimate: true`; o `vp check` avisa a cena sem marca, a abertura sem aviso e o
ano na fala (sinal de crônica)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.models.check_report import CheckReport
from app.pipeline.models.episode_scene import EpisodeScene
from app.pipeline.models.scenes_manifest import ScenesManifest
from app.pipeline.script.checks import speculation
from app.pipeline.script.checks.registry import EPISODE_RULES
from app.pipeline.script.molde import claimless_statements

OPENING = "E se o Brasil tivesse feito a bomba? A partir daqui eu vou mudar uma coisa só na história."
REAL = "Em 1990 o governo Collor fechou o poço da Serra do Cachimbo, no Pará."
GUESS = "O mais provável é que o Brasil seria cobrado por sanções da Argentina e dos Estados Unidos."
CHRONICLE = "O Brasil testa a bomba no Cachimbo e a Argentina responde com tropas na fronteira."


def scene(sid: str, narration: str, *, mode: str | None = None, **extra: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {"id": sid, "narration": narration, **extra}
    if "shots" not in raw:
        raw |= {"visual_need": "illustrative_reconstruction", "search_query": "mapa"}
    if mode is not None:
        raw["mode"] = mode
    return raw


def manifest(*scenes: dict[str, Any]) -> ScenesManifest:
    return ScenesManifest.model_validate({"episode_id": "ep", "language": "pt-BR", "scenes": list(scenes)})


def number_shot(*, estimate: bool | None = None, claims: bool = False) -> dict[str, Any]:
    shot: dict[str, Any] = {"kind": "number", "anchor": "sanções", "value": "30%", "label": "do PIB"}
    if estimate is not None:
        shot["estimate"] = estimate
    if claims:
        shot["claims"] = [{"text": "30%", "source_ids": ["source-01"]}]
    return shot


def report(scenes: ScenesManifest) -> CheckReport:
    return CheckReport(
        warnings=speculation.speculation_warnings(scenes),
        attention=speculation.speculation_attention(scenes),
    )


def test_rule_is_registered_in_vp_check() -> None:
    assert speculation.check in EPISODE_RULES


def test_old_script_without_mode_is_real_and_unchanged() -> None:
    parsed = manifest(scene("S01", OPENING), scene("S02", REAL))
    assert [s.mode for s in parsed.scenes] == ["real", "real"]
    dumped = parsed.model_dump(mode="json")
    assert all("mode" not in s for s in dumped["scenes"])  # o roteiro regravado não ganha campo
    assert report(parsed) == CheckReport()
    assert claimless_statements(parsed)  # a cena real com número segue avisando


def test_speculation_scene_has_no_claimless_warning() -> None:
    parsed = manifest(scene("S01", OPENING), scene("S02", REAL, mode="especulacao"))
    assert claimless_statements(parsed) == []


def test_fact_on_screen_in_speculation_needs_claims_or_estimate() -> None:
    with pytest.raises(ValidationError, match="S02: plano number sem claims.*estimate: true"):
        manifest(scene("S01", OPENING), scene("S02", GUESS, mode="especulacao", shots=[number_shot()]))
    with pytest.raises(ValidationError, match="S02: plano number sem claims"):
        manifest(
            scene("S01", OPENING),
            scene("S02", GUESS, mode="especulacao", shots=[number_shot(estimate=False)]),
        )
    estimated = manifest(
        scene("S01", OPENING), scene("S02", GUESS, mode="especulacao", shots=[number_shot(estimate=True)])
    )
    assert estimated.scenes[1].shots[0].estimate is True  # type: ignore[union-attr]
    sourced = manifest(
        scene("S01", OPENING), scene("S02", GUESS, mode="especulacao", shots=[number_shot(claims=True)])
    )
    assert sourced.scenes[1].shots[0].claims


def test_estimate_does_not_excuse_claims_in_a_real_scene() -> None:
    with pytest.raises(ValidationError, match="S01: plano number sem claims"):
        manifest(scene("S01", GUESS, shots=[number_shot(estimate=True)]))
    parsed = manifest(scene("S01", GUESS, shots=[number_shot(estimate=True, claims=True)]))
    assert any("estimate: true numa cena real" in line for line in report(parsed).warnings)


def test_speculation_without_mark_warns() -> None:
    parsed = manifest(scene("S01", OPENING), scene("S02", CHRONICLE, mode="especulacao"))
    assert any("S02: cena especulacao sem marca" in line for line in report(parsed).warnings)
    marked = manifest(scene("S01", OPENING), scene("S02", GUESS, mode="especulacao"))
    assert report(marked).warnings == []


@pytest.mark.parametrize(
    "mark", ["Provavelmente", "talvez", "na minha leitura", "Poderiam", "o mais provável"]
)
def test_each_mark_counts_without_case_or_accent(mark: str) -> None:
    parsed = manifest(scene("S01", OPENING), scene("S02", f"{mark} a Argentina reage.", mode="especulacao"))
    assert report(parsed).warnings == []


def test_mark_inside_another_word_does_not_count() -> None:
    parsed = manifest(
        scene("S01", OPENING), scene("S02", "A Argentina reage seriamente.", mode="especulacao")
    )
    assert any("sem marca" in line for line in report(parsed).warnings)


def test_speculation_before_the_opening_warns() -> None:
    first = manifest(scene("S01", GUESS, mode="especulacao"))
    assert any("S01: primeira cena especulacao antes" in line for line in report(first).warnings)
    silent = manifest(scene("S01", REAL), scene("S02", GUESS, mode="especulacao"))
    assert any("S02: primeira cena especulacao antes" in line for line in report(silent).warnings)
    told = manifest(scene("S01", OPENING), scene("S02", GUESS, mode="especulacao"))
    assert not any("abertura" in line for line in report(told).warnings)


def test_year_in_speculation_is_attention() -> None:
    parsed = manifest(
        scene("S01", OPENING), scene("S02", f"Em 1995 {GUESS[0].lower()}{GUESS[1:]}", mode="especulacao")
    )
    assert report(parsed).attention == [
        "especulação: S02: ano na fala (1995); data no futuro alternativo narra a linha inventada como "
        "crônica (ADR 065)"
    ]
    real_year = manifest(scene("S01", OPENING), scene("S02", REAL), scene("S03", GUESS, mode="especulacao"))
    assert report(real_year).attention == []  # o ano da cena real não conta


def test_number_that_is_not_a_year_is_not_attention() -> None:
    parsed = manifest(
        scene("S01", OPENING),
        scene("S02", f"{GUESS} Seriam 1.500 soldados ou 12345 reais.", mode="especulacao"),
    )
    assert report(parsed).attention == []


def test_mode_and_estimate_reach_episode_json_only_when_set() -> None:
    base: dict[str, Any] = {
        "id": "S01",
        "start_ms": 0,
        "duration_ms": 1000,
        "narration": GUESS,
        "audio": "a.wav",
    }
    shot = {"start_ms": 0, "duration_ms": 1000, "spec": number_shot(estimate=True)}
    speculative = EpisodeScene.model_validate({**base, "mode": "especulacao", "shots": [shot]})
    data = json.loads(speculative.model_dump_json())
    assert data["mode"] == "especulacao"
    assert data["shots"][0]["spec"]["estimate"] is True
    plain_shot = {**shot, "spec": number_shot(claims=True)}
    real = json.loads(EpisodeScene.model_validate({**base, "shots": [plain_shot]}).model_dump_json())
    assert (
        "mode" not in real and "estimate" not in real["shots"][0]["spec"]
    )  # o episode.json de antes não muda
