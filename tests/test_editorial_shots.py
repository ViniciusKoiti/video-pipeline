"""Planos editoriais (ADR 011): contrato, passos da rede, fonte no rodapé e alertas do `vp check`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from app.pipeline.attribution import shot_attribution, source_label
from app.pipeline.check import check_episode, variety_warnings
from app.pipeline.schemas import (
    Claim,
    EpisodeFormat,
    EpisodeManifest,
    EpisodeScene,
    EpisodeShot,
    NetworkShot,
    Scene,
    Shot,
    Source,
    SourcesManifest,
    screen_number,
)
from app.pipeline.shots import episode_shots
from app.render.remotion import RemotionEngine
from tests.test_research import EP, episode, facts_file, scenes, source
from tests.test_shots import CLAIM, photo

SHOT = TypeAdapter(Shot)
FIXTURE_IMAGE = (
    Path(__file__).parent / "fixtures" / "episodes" / "engine-test" / "assets" / "commons-lc-usz62-136192.jpg"
)
NET = "O grupo tomou crédito no banco. Depois, o governo deu o aval. No fim, a cadeia ficou clara."


def network(anchor: str = "O grupo", **extra: Any) -> dict[str, Any]:
    return {
        "kind": "network",
        "anchor": anchor,
        "root": "grupo",
        "nodes": [
            {"id": "grupo", "label": "Empresa A", "kind": "company"},
            {"id": "banco", "label": "Banco B", "kind": "bank"},
            {"id": "governo", "label": "Governo", "kind": "government"},
        ],
        "edges": [
            {"from": "banco", "to": "grupo", "label": "empresta a", "flow": True, "claims": [CLAIM]},
            {"from": "governo", "to": "banco", "label": "avaliza", "style": "dashed", "claims": [CLAIM]},
        ],
        "steps": [
            {"anchor": "no banco", "nodes": ["banco"]},
            {"anchor": "o governo", "nodes": ["governo"]},
            {"anchor": "No fim", "highlight": ["grupo", "banco", "governo"]},
        ],
        "claims": [CLAIM],
        **extra,
    }


def make_scene(shots: list[dict[str, Any]], narration: str, scene_id: str = "S01") -> Scene:
    return Scene.model_validate({"id": scene_id, "narration": narration, "shots": shots})


def sources_of(*items: dict[str, Any]) -> SourcesManifest:
    return SourcesManifest.model_validate({"episode_id": EP, "sources": list(items)})


# --- Contrato -----------------------------------------------------------------------------------


def test_new_kinds_parse_and_keep_from_in_json() -> None:
    narration = NET + " O crédito era maior que o capital."
    parsed = make_scene(
        [
            network(),
            {"kind": "compare", "anchor": "O crédito", "mode": "scale", "claims": [CLAIM],
             "left": {"value": "69 mil", "label": "crédito"},
             "right": {"value": "60 mil", "label": "capital"}},
            {"kind": "keyword", "anchor": "maior que o capital", "text": "Maior que o capital",
             "highlight": "capital"},
        ],
        narration,
    )
    assert [s.kind for s in parsed.shots] == ["network", "compare", "keyword"]
    dumped = parsed.model_dump_json()
    assert '"from":"banco"' in dumped and "from_" not in dumped
    assert Scene.model_validate_json(dumped) == parsed


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda n: n["edges"][0].update(to="fundo"), "nós inexistentes na rede: fundo"),
        (lambda n: n.update(root="fundo"), "raiz 'fundo' não está entre os nós"),
        (lambda n: n["steps"].pop(1), "nós que nunca entram na rede: governo"),
        (lambda n: n["edges"][0].update(claims=[]), "at least 1 item"),
        (lambda n: n["steps"][0].update(nodes=["grupo", "banco"]), "a raiz já abre o plano"),
        (lambda n: n["steps"][2].update(highlight=[]), "sem nós novos nem destaque"),
    ],
)
def test_network_graph_must_be_consistent(change: Any, message: str) -> None:
    raw = network()
    change(raw)
    with pytest.raises(ValidationError, match=message):
        SHOT.validate_python(raw)


def test_network_steps_follow_the_narration_inside_the_shot() -> None:
    out_of_order = network()
    steps = out_of_order["steps"]
    steps[0], steps[1] = steps[1], steps[0]
    with pytest.raises(ValidationError, match="passo 'no banco' da rede não aparece"):
        make_scene([out_of_order], NET)
    after_next_shot = [network(), photo("o governo")]  # o passo "o governo" cairia no plano seguinte
    with pytest.raises(ValidationError, match="passo 'o governo' da rede"):
        make_scene(after_next_shot, NET)


def test_network_steps_get_times_relative_to_the_shot() -> None:
    scene = make_scene([photo("O grupo", asset_id="f"), network("crédito no banco")], NET)
    _, net = episode_shots(scene, 9000, lambda _: "assets/f.jpg")
    first = round(NET.find("no banco") / len(NET) * 9000) - net.start_ms
    assert net.steps_ms[0] == first and len(net.steps_ms) == 3
    assert net.steps_ms == sorted(net.steps_ms) and net.steps_ms[-1] < net.duration_ms


def test_episode_shot_needs_one_time_per_network_step() -> None:
    spec = NetworkShot.model_validate(network())
    with pytest.raises(ValidationError, match="2 tempos de passo, esperado 3"):
        EpisodeShot(start_ms=0, duration_ms=3000, spec=spec, steps_ms=[0, 100])
    with pytest.raises(ValidationError, match="fora de ordem ou fora do plano"):
        EpisodeShot(start_ms=0, duration_ms=3000, spec=spec, steps_ms=[0, 3500, 100])
    stamp = SHOT.validate_python({"kind": "stamp", "anchor": "x", "date": "1918", "claims": [CLAIM]})
    with pytest.raises(ValidationError, match="1 tempos de passo, esperado 0"):
        EpisodeShot(start_ms=0, duration_ms=3000, spec=stamp, steps_ms=[0])


def test_keyword_is_short_and_literal_in_the_narration() -> None:
    def keyword(text: str, highlight: str = "") -> dict[str, Any]:
        return {"kind": "keyword", "anchor": "O grupo", "text": text, "highlight": highlight}

    assert make_scene([keyword("o grupo tomou crédito")], NET).shots[0].kind == "keyword"
    with pytest.raises(ValidationError, match="não está na narração"):
        make_scene([keyword("o grupo pagou a dívida")], NET)
    with pytest.raises(ValidationError, match="mais de 8 palavras"):
        SHOT.validate_python(keyword("um dois três quatro cinco seis sete oito nove"))
    with pytest.raises(ValidationError, match="fora da frase"):
        SHOT.validate_python(keyword("o grupo tomou crédito", highlight="governo"))


def test_screen_numbers_keep_prefix_and_suffix() -> None:
    assert screen_number("R$ 47,6 bi") == ("R$", 47.6, "bi")
    assert screen_number("1.500") == ("", 1500.0, "")
    assert screen_number("6ª") == ("", 6.0, "ª")
    assert screen_number("muito") is None


@pytest.mark.parametrize(
    ("left", "right", "message"),
    [("R$ 5 mil", "8 vezes", "unidades diferentes"), ("muito", "pouco", "dois números")],
)
def test_compare_in_scale_needs_two_numbers_in_the_same_unit(left: str, right: str, message: str) -> None:
    raw = {"kind": "compare", "anchor": "x", "mode": "scale", "claims": [CLAIM],
           "left": {"value": left, "label": "a"}, "right": {"value": right, "label": "b"}}
    with pytest.raises(ValidationError, match=message):
        SHOT.validate_python(raw)
    # lado a lado aceita qualquer texto
    assert SHOT.validate_python({**raw, "mode": "side"}).kind == "compare"


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ({"highlight": "2030"}, "não é um dos rótulos"),
        ({"type": "line", "points": [{"label": "começo", "value": 1}, {"label": "fim", "value": 2}]},
         "precisam ser anos"),
        ({"type": "share", "points": [{"label": "a", "value": -1}, {"label": "b", "value": 2}]},
         "sem valor negativo"),
        ({"rest": "outros"}, "rest só vale"),
    ],
)
def test_chart_type_and_highlight_rules(extra: dict[str, Any], message: str) -> None:
    raw = {"kind": "chart", "anchor": "x", "title": "t", "claims": [CLAIM],
           "points": [{"label": "1918", "value": 1}, {"label": "1923", "value": 2}], **extra}
    with pytest.raises(ValidationError, match=message):
        SHOT.validate_python(raw)


def test_chart_line_and_share_are_valid() -> None:
    base = {"kind": "chart", "anchor": "x", "title": "t", "claims": [CLAIM]}
    line = SHOT.validate_python({**base, "type": "line", "highlight": "1923-05",
                                 "points": [{"label": "1918", "value": 1}, {"label": "1923-05", "value": 2}]})
    share = SHOT.validate_python({**base, "type": "share", "rest": "outros",
                                  "points": [{"label": "a", "value": 61}, {"label": "b", "value": 39}]})
    # linha a partir do zero; sem destaque, nenhum ponto em dourado
    assert (line.y_from_zero, share.highlight) == (True, None)


def test_quote_document_needs_its_header() -> None:
    base = {"kind": "quote", "anchor": "x", "text": "trecho", "attribution": "fonte", "claims": [CLAIM]}
    with pytest.raises(ValidationError, match="precisa do cabeçalho"):
        SHOT.validate_python({**base, "style": "document"})
    with pytest.raises(ValidationError, match="só vale nos estilos"):
        SHOT.validate_python({**base, "document": {"title": "Relatório"}})
    page = SHOT.validate_python({**base, "style": "document", "variant": "letter",
                                 "document": {"title": "Relatório", "issuer": "Empresa A", "date": "1956"}})
    assert page.document.title == "Relatório"


def test_map_routes_highlight_and_claims() -> None:
    base = {"kind": "map", "anchor": "x", "scope": "world",
            "places": [{"name": "A", "lat": 51.5, "lon": -0.1}, {"name": "B", "lat": -23.5, "lon": -47.5}]}
    with pytest.raises(ValidationError, match="precisa de claims"):
        SHOT.validate_python({**base, "routes": [{"from": "A", "to": "B"}]})
    with pytest.raises(ValidationError, match="lugar fora de places: C"):
        SHOT.validate_python({**base, "routes": [{"from": "A", "to": "C"}], "claims": [CLAIM]})
    with pytest.raises(ValidationError, match="should match pattern"):
        SHOT.validate_python({**base, "highlight": ["Brasil"], "claims": [CLAIM]})
    ok = SHOT.validate_python({**base, "highlight": ["BRA", "BR-SP"], "routes": [{"from": "A", "to": "B"}],
                               "claims": [CLAIM]})
    assert ok.model_dump(mode="json")["routes"] == [{"from": "A", "to": "B"}]


def test_timeline_when_matches_the_written_year() -> None:
    def timeline(*events: dict[str, Any]) -> Any:
        raw = {"kind": "timeline", "anchor": "x", "claims": [CLAIM], "events": list(events)}
        return SHOT.validate_python(raw)

    with pytest.raises(ValidationError, match="não bate com o ano"):
        timeline({"date": "7 jan. 1918", "label": "a", "when": "1919"}, {"date": "1925", "label": "b"})
    ok = timeline(
        {"date": "anos 1920", "label": "a", "when": 1920},
        {"date": "desfecho", "label": "b", "when": "1974-03"},
    )
    assert [e.when for e in ok.events] == ["1920", "1974-03"]


# --- Fonte no rodapé ----------------------------------------------------------------------------


def test_source_label_from_authors_or_title() -> None:
    def label(**extra: Any) -> str:
        return source_label(Source.model_validate(source(1, **extra)))

    assert label(authors=["Silva, Gustavo", "Dalla Costa, Armando"]) == "Silva e Dalla Costa"
    assert label(authors=["A, x", "B, y", "C, z"]) == "A e outros"
    assert label(title="Relatório Anual 2025 — Empresa A") == "Relatório Anual 2025"
    long = label(title="Um título de documento muito comprido que passa do limite do rodapé do vídeo")
    assert long.endswith("…") and len(long) <= 60


def test_shot_attribution_merges_authors_and_flags_interested_sources() -> None:
    manifest = sources_of(
        source(1, authors=["Silva, G"]), source(2, authors=["Silva, G"]),
        source(3, title="Relatório Anual — Empresa A", interested=True), source(4, title="Jornal B"),
    )

    def claims(*ids: int) -> list[Claim]:
        return [Claim(text="x", source_ids=[f"source-0{i}" for i in ids])]

    assert shot_attribution(claims(1, 2), manifest) == ("Silva", None)
    assert shot_attribution(claims(3), manifest) == ("Relatório Anual", "fonte interessada")
    assert shot_attribution(claims(3, 1), manifest) == ("Relatório Anual; Silva", None)
    assert shot_attribution(claims(1, 3, 4), manifest) == ("Silva; Relatório Anual e outras", None)


def test_episode_shots_carry_the_source_of_their_claims() -> None:
    manifest = sources_of(source(1, authors=["Silva, G"]))
    scene = make_scene([photo("O grupo", asset_id="f"), network("crédito no banco")], NET)
    media, net = episode_shots(scene, 9000, lambda _: "assets/f.jpg", manifest)
    assert (media.source, net.source) == (None, "Silva")


# --- Props do template --------------------------------------------------------------------------


def test_remotion_props_carry_source_and_step_frames(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "f.jpg").write_bytes(FIXTURE_IMAGE.read_bytes())
    manifest = sources_of(source(1, interested=True))
    scene = make_scene([photo("O grupo", asset_id="f"), network("crédito no banco")], NET)
    shots = episode_shots(scene, 9000, lambda _: "assets/f.jpg", manifest)
    episode_manifest = EpisodeManifest(
        schema_version=2, episode_id="teste", title="teste", language="pt-BR",
        format=EpisodeFormat.EXPLAINER,
        scenes=[EpisodeScene(id="S01", start_ms=0, duration_ms=9000, narration=NET, audio="voice/S01.wav",
                             shots=shots)],
    )
    (props,) = RemotionEngine().scene_props(episode_manifest, tmp_path, preview=False)
    photo_props, net_props = props["shots"]
    assert "source" not in photo_props and "stepFrames" not in photo_props
    assert (net_props["source"], net_props["sourceFlag"]) == ("Fonte 1", "fonte interessada")
    assert net_props["stepFrames"] == [round(ms * 30 / 1000) for ms in shots[1].steps_ms]
    assert net_props["spec"]["edges"][0]["from"] == "banco"


# --- vp check -----------------------------------------------------------------------------------


def test_quote_on_screen_must_be_literal_in_its_excerpt(tmp_path: Path) -> None:
    def with_quote(text: str) -> dict[str, Any]:
        raw = scenes()
        raw["scenes"][0]["shots"][0] = {
            "kind": "quote", "anchor": "Em 1918", "text": text, "attribution": "Fonte 1",
            "claims": [{"text": "compra", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E2"]}],
        }
        return raw

    literal = check_episode(episode(tmp_path / "a", facts=facts_file(), scenes_json=with_quote(
        "adquiriu a fábrica de tecidos [...] em leilão")), EP)
    assert literal.ok, literal.errors
    invented = check_episode(episode(tmp_path / "b", facts=facts_file(), scenes_json=with_quote(
        "comprou a fábrica")), EP)
    assert invented.errors == ["S01: citação na tela não está nos trechos citados: 'comprou a fábrica'"]


def test_short_chart_warns_about_reading_time(tmp_path: Path) -> None:
    raw = scenes()
    raw["scenes"][0]["shots"][0] = {
        "kind": "chart", "anchor": "Em 1918", "title": "t", "claims": raw["scenes"][0]["shots"][0]["claims"],
        "points": [{"label": "a", "value": 1}, {"label": "b", "value": 2}, {"label": "c", "value": 3}],
    }
    report = check_episode(episode(tmp_path, facts=facts_file(), scenes_json=raw), EP)
    assert report.warnings == ["S01: chart ('Em 1918') com ~3.6 s; precisa de 4 s para ser lido"]


WORDS = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
MAKERS: dict[str, Any] = {
    "photo": lambda a: photo(a),
    "stamp": lambda a: {"kind": "stamp", "anchor": a, "date": "1918", "claims": [CLAIM]},
    "number": lambda a: {"kind": "number", "anchor": a, "value": "10", "label": "x", "claims": [CLAIM]},
    "lower_third": lambda a: {
        "kind": "lower_third", "anchor": a, "name": "N", "role": "R", "claims": [CLAIM]
    },
    "keyword": lambda a: {"kind": "keyword", "anchor": a, "text": a},
    "timeline": lambda a: {"kind": "timeline", "anchor": a, "claims": [CLAIM],
                           "events": [{"date": "1918", "label": "a"}, {"date": "1925", "label": "b"}]},
    "chart2": lambda a: {"kind": "chart", "anchor": a, "title": "t", "claims": [CLAIM],
                         "points": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]},
}


RUN = "5 planos gráficos seguidos sem foto nem B-roll"


def planned(kinds: list[str], scene_id: str = "S01") -> Scene:
    words = WORDS[: len(kinds)]
    return make_scene([MAKERS[k](w) for k, w in zip(kinds, words, strict=True)], " ".join(words), scene_id)


@pytest.mark.parametrize(
    ("plans", "expected"),
    [
        ([["stamp", "number", "timeline", "number", "stamp"]], [f"S01: {RUN}"]),
        ([["stamp", "number", "stamp"], ["number", "stamp"]], [f"S01–S02: {RUN}"]),
        ([["photo", "number", "stamp", "keyword", "lower_third", "number"]], []),  # tudo por cima da foto
        ([["lower_third", "photo"]], ["S01: tarja ('alfa') sem foto nem B-roll por baixo"]),
        ([["photo", "number", "number"]], ["S01: number duas vezes seguidas"]),
        ([["chart2", "photo"]], ["S01: gráfico de barras com 2 pontos ('alfa'); use compare"]),
        ([["keyword", "photo", "keyword"]], ["S01: 2 frases na tela na mesma cena; use uma"]),
        ([["photo", "stamp"] * 5], ["carimbos em 5 de 10 planos (50%); o limite é 10%"]),
    ],
)
def test_variety_warnings(plans: list[list[str]], expected: list[str]) -> None:
    scenes_list = [planned(kinds, f"S0{i + 1}") for i, kinds in enumerate(plans)]
    assert variety_warnings(scenes_list) == expected


# --- Template (etapa 2) -------------------------------------------------------------------------


def test_template_handles_every_shot_kind() -> None:
    """Todo tipo que o contrato aceita tem um `case` no despacho do template (video/src/ShotView.tsx)."""
    from typing import get_args

    from app.render.remotion import PROJECT

    kinds = {model.model_fields["kind"].default for model in get_args(get_args(Shot)[0])}
    dispatch = (PROJECT / "src" / "ShotView.tsx").read_text()
    missing = sorted(kind for kind in kinds if f'case "{kind}":' not in dispatch)
    assert missing == []


def test_region_codes_come_from_the_template_outlines() -> None:
    from app.render.remotion import region_codes

    codes = region_codes()
    assert {"BRA", "BR-SP", "GBR", "ARG"} <= codes
    assert "Brasil" not in codes


def test_unknown_map_code_is_an_error(tmp_path: Path) -> None:
    raw = scenes()
    raw["scenes"][0]["shots"][1] = {
        "kind": "map", "anchor": "comprada num leilão", "highlight": ["BR-SP", "BR-XX"],
        "places": [{"name": "Sorocaba", "lat": -23.5, "lon": -47.46}],
        "claims": raw["scenes"][0]["shots"][0]["claims"],
    }
    report = check_episode(episode(tmp_path, facts=facts_file(), scenes_json=raw), EP,
                           region_codes=frozenset({"BR-SP"}))
    assert report.errors == ["S01: código BR-XX fora dos contornos do mapa"]


# --- Skills (etapa 3) ---------------------------------------------------------------------------

SKILL = Path(__file__).parents[1] / ".claude" / "skills" / "roteiro-explicativo"


def _json_blocks(path: Path) -> list[str]:
    import re

    return re.findall(r"```json\n(.*?)```", path.read_text(), flags=re.S)


def test_shot_examples_in_the_skill_follow_the_contract() -> None:
    """Os exemplos que o roteirista copia passam no schema: a skill não fica atrás do contrato."""
    import json

    blocks = _json_blocks(SKILL / "planos.md")
    kinds = [SHOT.validate_python(json.loads(block)).kind for block in blocks]
    assert set(kinds) == {"compare", "network", "chart", "quote", "map", "timeline", "keyword"}
    (example,) = _json_blocks(SKILL / "SKILL.md")
    from app.pipeline.schemas import ScenesManifest

    assert ScenesManifest.model_validate_json(example).scenes[0].shots[-1].kind == "keyword"
