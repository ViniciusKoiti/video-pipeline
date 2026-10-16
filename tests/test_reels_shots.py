"""Planos dos Reels (ADR 028): conta, nota, gancho, cartão final, selo da série e começo sem fade."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from app.pipeline.check import CheckReport, _check_scenes, arithmetic_errors, funnel_warnings
from app.pipeline.schemas import (
    EpisodeFormat,
    EpisodeManifest,
    EpisodeScene,
    EpisodeShot,
    ScenesManifest,
    Shot,
    VideoSpec,
)
from app.pipeline.shots import episode_shots
from app.render.remotion import RemotionEngine
from tests.test_shots import CLAIM

SHOT = TypeAdapter(Shot)
HOOK = "Você está cobrando o docinho errado."
COUNT = (
    "A lata custa dezoito e quarenta e quatro, dividido por trezentos e noventa e cinco gramas, "
    "vezes cento e noventa e cinco. Dá nove e dez na receita."
)
LAST = "Salva pra conferir na próxima encomenda."


def calculation(**extra: Any) -> dict[str, Any]:
    return {
        "kind": "calculation",
        "anchor": "A lata custa",
        "terms": [
            {"text": "R$ 18,44", "label": "a lata", "anchor": "dezoito e quarenta e quatro"},
            {"op": "÷", "text": "395 g", "label": "o peso", "anchor": "trezentos e noventa e cinco"},
            {"op": "×", "text": "195 g", "label": "a receita", "anchor": "cento e noventa e cinco"},
        ],
        "result": {"text": "R$ 9,10", "label": "na receita", "anchor": "Dá nove e dez"},
        "claims": [CLAIM],
        **extra,
    }


def receipt(total: str = "R$ 6,90") -> dict[str, Any]:
    return {
        "kind": "receipt",
        "anchor": "Farinha",
        "title": "Bolo de pote",
        "items": [
            {"label": "Farinha", "value": "R$ 2,10"},
            {"label": "Manteiga", "value": "R$ 4,80", "anchor": "manteiga"},
        ],
        "total": {"value": total, "anchor": "no total"},
        "claims": [CLAIM],
    }


def hook(text: str = HOOK, **extra: Any) -> dict[str, Any]:
    return {"kind": "hook", "anchor": "Você está", "text": text, "highlight": "errado", **extra}


def end_card(variant: str = "save") -> dict[str, Any]:
    return {"kind": "end_card", "anchor": "Salva", "variant": variant, "text": "Salve para fazer a conta"}


def manifest(
    first: list[dict[str, Any]] | None = None,
    last: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> ScenesManifest:
    scenes = [
        {"id": "S01", "narration": f"{HOOK} {COUNT}",
         "shots": first if first is not None else [hook(), calculation()]},
        {"id": "S02", "narration": LAST, "shots": last if last is not None else [end_card()]},
    ]
    raw = {"episode_id": "ep", "language": "pt-BR", "orientation": "portrait", "scenes": scenes, **extra}
    return ScenesManifest.model_validate(raw)


# --- Contrato -----------------------------------------------------------------------------------


def test_reels_script_with_hook_count_and_end_card_parses() -> None:
    parsed = manifest(series={"name": "Confeitaria", "part": 2, "total": 3})
    assert [s.kind for s in parsed.scenes[0].shots] == ["hook", "calculation"]
    assert parsed.series is not None and parsed.series.part == 2


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda c: c["terms"][0].update(op="+"), "primeiro termo da conta não tem operador"),
        (lambda c: c["terms"][1].pop("op"), "termo 2 da conta sem operador"),
        (lambda c: c["terms"][2].pop("anchor"), "termo 3 sem anchor"),
        (lambda c: c.update(claims=[]), "at least 1 item"),
    ],
)
def test_calculation_rules(change: Any, message: str) -> None:
    raw = calculation()
    change(raw)
    with pytest.raises(ValidationError, match=message):
        SHOT.validate_python(raw)


def test_calculation_parts_follow_the_narration_and_get_times() -> None:
    swapped = calculation()
    swapped["terms"][1]["anchor"], swapped["terms"][2]["anchor"] = "cento e noventa e cinco", "trezentos"
    with pytest.raises(ValidationError, match="termo 'trezentos' do plano calculation não aparece"):
        manifest(first=[hook(), swapped])
    scene = manifest().scenes[0]
    _, count = episode_shots(scene, 12_000, lambda _: None)
    assert len(count.steps_ms) == 4  # três termos e o resultado
    assert count.steps_ms == sorted(count.steps_ms) and count.steps_ms[-1] < count.duration_ms
    with pytest.raises(ValidationError, match="2 tempos de passo, esperado 4"):
        EpisodeShot(start_ms=0, duration_ms=3000, spec=count.spec, steps_ms=[0, 10])


def test_receipt_first_line_may_enter_with_the_shot() -> None:
    narration = "Farinha, depois a manteiga, e no total o pote custa isso."
    shots = episode_shots(
        ScenesManifest.model_validate({
            "episode_id": "ep", "language": "pt-BR", "orientation": "portrait",
            "scenes": [{"id": "S01", "narration": narration, "shots": [receipt()]}],
        }).scenes[0],
        6000,
        lambda _: None,
    )
    assert shots[0].steps_ms[0] == 0 and len(shots[0].steps_ms) == 3
    no_anchor = receipt()
    no_anchor["items"][1].pop("anchor")
    with pytest.raises(ValidationError, match="linha 2 sem anchor"):
        SHOT.validate_python(no_anchor)


def test_hook_is_literal_short_and_sourced_when_it_has_a_number() -> None:
    with pytest.raises(ValidationError, match="gancho 'Você cobra errado' não está na narração"):
        manifest(first=[hook("Você cobra errado", highlight="")])
    with pytest.raises(ValidationError, match="gancho com número precisa de claims"):
        SHOT.validate_python(hook("O docinho custa 60 centavos", highlight=""))
    sourced = hook("O docinho custa 60 centavos", highlight="", claims=[CLAIM])
    assert SHOT.validate_python(sourced).kind == "hook"
    with pytest.raises(ValidationError, match="fora do gancho"):
        SHOT.validate_python(hook(highlight="caro"))
    with pytest.raises(ValidationError, match="mais de 14 palavras"):
        SHOT.validate_python(hook(" ".join(["palavra"] * 15), highlight=""))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"orientation": "landscape"}, "plano hook só no vertical"),
        ({"first": [calculation()], "last": [hook("Salva pra conferir", highlight="", anchor="Salva")]},
         "S02: hook só no primeiro plano"),
        ({"first": [hook(), calculation(), {**end_card(), "anchor": "na receita"}],
          "last": [{"kind": "keyword", "anchor": "Salva", "text": "salva pra conferir"}]},
         "S01: end_card só no último plano"),
        ({"last": [end_card("next")]}, "cartão final next pede a série"),
        ({"last": [end_card("next")], "series": {"name": "x", "part": 3, "total": 3}}, "next pede a série"),
        ({"funnel": {"stage": "fundo", "cta": "Comenta PLANILHA.", "offer": "planilha"}},
         "sem a chamada do fundo"),
    ],
)
def test_where_the_reels_shots_go(kwargs: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        manifest(**kwargs)


def test_series_part_inside_the_total() -> None:
    with pytest.raises(ValidationError, match="parte 4 de 3"):
        manifest(series={"name": "x", "part": 4, "total": 3})


# --- vp check -----------------------------------------------------------------------------------


def _shot(raw: dict[str, Any]) -> Shot:
    return SHOT.validate_python(raw)


def test_check_redoes_the_count() -> None:
    assert arithmetic_errors("S01", _shot(calculation()), "pt-BR") == []
    wrong = calculation()
    wrong["result"]["text"] = "R$ 9,20"
    assert arithmetic_errors("S01", _shot(wrong), "pt-BR") == [
        "S01: calculation ('A lata custa'): R$ 18,44 ÷ 395 g × 195 g dá 9,10, e a tela mostra R$ 9,20"
    ]
    percent = calculation()
    percent["terms"] = [
        {"text": "R$ 6,00", "anchor": None},
        {"op": "×", "text": "20%", "anchor": "trezentos"},
    ]
    percent["result"]["text"] = "R$ 1,20"
    assert arithmetic_errors("S01", _shot(percent), "pt-BR") == []
    precedence = calculation()
    precedence["terms"] = [
        {"text": "2"},
        {"op": "+", "text": "3", "anchor": "trezentos"},
        {"op": "×", "text": "4", "anchor": "cento"},
    ]
    precedence["result"]["text"] = "14"
    assert arithmetic_errors("S01", _shot(precedence), "pt-BR") == []


def test_check_redoes_the_receipt_sum_in_one_unit() -> None:
    assert arithmetic_errors("S01", _shot(receipt()), "pt-BR") == []
    assert arithmetic_errors("S01", _shot(receipt("R$ 7,00")), "pt-BR") == [
        "S01: receipt ('Farinha'): as linhas somam 6,90, e o total mostra R$ 7,00"
    ]
    mixed = receipt()
    mixed["items"][1]["value"] = "4,80 kg"
    assert "unidades diferentes" in arithmetic_errors("S01", _shot(mixed), "pt-BR")[0]


def test_count_on_screen_only_when_the_video_explains() -> None:
    def errors(kinds: list[str]) -> list[str]:
        objective = {"kinds": kinds, "promise": "x"}
        if "explicar" in kinds:
            objective["question"] = "Quanto custa?"
        if "opinar" in kinds:
            objective |= {"thesis": "t", "thesis_by": "dono"}
        report = CheckReport()
        _check_scenes(manifest(objective=objective), None, None, {}, report)
        return [e for e in report.errors if "só em vídeo que explica" in e]

    assert errors(["explicar"]) == []
    assert errors(["opinar"]) == [
        "S01: calculation ('A lata custa'): conta na tela só em vídeo que explica (ADR 020)"
    ]


def test_end_card_matches_the_funnel() -> None:
    meio = {"stage": "meio", "cta": LAST}
    assert funnel_warnings(manifest(funnel=meio)) == []
    topo = {"stage": "topo", "cta": "Segue pra ver a próxima."}
    follow_scene = [end_card("save")]
    warnings = funnel_warnings(manifest(funnel=topo, last=follow_scene))
    assert "funil topo: cartão final save; o estágio pede follow" in warnings
    assert any("não é dita durante o cartão final" in w for w in warnings)


# --- Adaptador ----------------------------------------------------------------------------------


def test_props_start_without_fade_and_carry_the_series(tmp_path: Path) -> None:
    def scene(sid: str, start: int, spec: dict[str, Any]) -> EpisodeScene:
        return EpisodeScene(
            id=sid, start_ms=start, duration_ms=2000, narration="x", audio=f"voice/{sid}.wav",
            shots=[EpisodeShot(start_ms=0, duration_ms=2000, spec=SHOT.validate_python(spec))],
        )

    episode = EpisodeManifest(
        schema_version=2, episode_id="ep", title="t", language="pt-BR", format=EpisodeFormat.EXPLAINER,
        video=VideoSpec.for_orientation("portrait"),
        scenes=[scene("S01", 0, hook()), scene("S02", 2000, end_card())],
        series={"name": "Confeitaria", "part": 2, "total": 3},
    )
    first, last = RemotionEngine().scene_props(episode, tmp_path, preview=False)
    assert first["fadeIn"] is False and "fadeIn" not in last
    assert last["shots"][0]["series"] == {"name": "Confeitaria", "part": 2, "total": 3}
    assert "series" not in first["shots"][0]
