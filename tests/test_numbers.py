"""Números do roteiro gerados do scenes.json e comparados com o perfil do nicho (#170, ADR 031 B e D)."""

from __future__ import annotations

import ast
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from app.cli import main
from app.pipeline.check import check_episode
from app.pipeline.gates import gate_report, record_check, record_decision
from app.pipeline.numbers import (
    BLOCK_END,
    BLOCK_START,
    SPOKEN,
    FormatBrief,
    format_warnings,
    image_changes,
    render_block,
    replace_block,
    script_numbers,
    shot_timings,
    strip_block,
)
from app.pipeline.schemas import Asset, CheckVerdict, Decision, ScenesManifest, Status, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME, make_root

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "numeros-death-note"
SKILL = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "analise-de-formato"
EPISODE = "numeros-death-note"
CPS = 14.0


def fixture() -> tuple[ScenesManifest, dict[str, Asset]]:
    scenes = ScenesManifest.model_validate_json((FIXTURE / "scenes.json").read_text(encoding="utf-8"))
    assets = {p.stem: Asset.model_validate_json(p.read_text()) for p in (FIXTURE / "assets").glob("*.json")}
    return scenes, assets


def scenes_of(*scenes: dict) -> ScenesManifest:
    return ScenesManifest.model_validate({"episode_id": "x", "language": "pt-BR", "scenes": list(scenes)})


def photo(anchor: str, asset: str | None = None, **extra: str) -> dict:
    shot = {"kind": "photo", "anchor": anchor, "visual_need": "contextual_stock", "search_query": "q"}
    return {**shot, "asset_id": asset, **extra}


def broll(anchor: str, asset: str) -> dict:
    return {
        "kind": "broll",
        "anchor": anchor,
        "visual_need": "contextual_stock",
        "search_query": "q",
        "asset_id": asset,
    }


# --- os números do recorte do Death Note (as 21 cenas da prévia de 2026-10-19) ---


def test_death_note_excerpt_numbers() -> None:
    scenes, assets = fixture()
    n = script_numbers(scenes, assets, CPS)
    assert (n.scenes, n.shots, n.text_shots, n.pauses, n.words) == (21, 36, 4, 2, 436)
    assert round(n.duration_ms / 1000) == 178
    assert (n.voce, n.voce_scenes, n.voce_closing) == (2, 2, 0)
    assert (n.opening[0], n.rest[0]) == (4, 32)
    assert [(t.scene_id, t.shot.kind) for t in n.rhythm_alerts] == [
        ("S039", "quote"),
        ("S120", "photo"),
        ("S055", "photo"),
        ("S056", "quote"),
    ]
    assert [(c.scene_id, c.asset_id, round(c.ms / 100) / 10) for c in n.citations] == [
        ("S145", "crunchyroll-trailer-naomi", 3.3),
        ("S057", "crunchyroll-de-trailer-light-gravata", 1.7),
        ("S060", "crunchyroll-trailer-light-olhos", 3.4),
    ]
    assert len(n.assets_by_use) == 10 and n.unused_assets == ["viz-trailer-omega-ryuk"]
    assert n.assets_by_use["pexels-video-15161525"] == [
        "S115",
        "S036",
        "S145",
        "S045",
        "S040",
        "S041",
        "S046",
    ]


def test_death_note_excerpt_niche_measures() -> None:
    scenes, assets = fixture()
    m = script_numbers(scenes, assets, CPS).measures
    assert round(m["palavras_min"]) == 147
    assert round(m["cortes_min"], 1) == 5.7  # trocas de imagem, não planos: 17 trocas em 36 planos
    assert round(m["voce_por_mil"], 1) == 4.6
    assert (m["palavras_60s"], m["voce_60s"], m["cortes_60s"]) == (178, 2, 6)


# --- as regras de cada número ---


def test_pause_weighs_in_time_but_not_in_words() -> None:
    plain = scenes_of({"id": "S01", "narration": "Uma frase curta aqui.", "shots": [photo("Uma")]})
    paused = scenes_of(
        {"id": "S01", "narration": "Uma frase <short pause> curta aqui.", "shots": [photo("Uma")]}
    )
    a, b = script_numbers(plain, {}, CPS), script_numbers(paused, {}, CPS)
    assert a.words == b.words == 4 and b.pauses == 1
    assert round(b.duration_ms - a.duration_ms) == round(10 / CPS * 1000)


def test_voce_counts_every_form_the_niche_counts() -> None:
    scenes = scenes_of(
        {"id": "S01", "narration": "Você sabe? E vocês, sabem. Isso é seu, você.", "shots": [photo("Você")]}
    )
    n = script_numbers(scenes, {}, CPS)
    assert (n.voce, n.voce_scenes) == (3, 1)


def test_long_broll_is_texture_but_long_photo_is_an_alert() -> None:
    text = "Uma fala longa o bastante para segurar a mesma imagem por bem mais de seis segundos na tela."
    held = script_numbers(scenes_of({"id": "S01", "narration": text, "shots": [broll("Uma", "v")]}), {}, CPS)
    still = script_numbers(scenes_of({"id": "S01", "narration": text, "shots": [photo("Uma", "f")]}), {}, CPS)
    assert held.rhythm_alerts == [] and len(still.rhythm_alerts) == 1


def test_image_changes_skip_continuing_texture_and_overlays() -> None:
    scenes = scenes_of(
        {
            "id": "S01",
            "narration": "Primeira parte da fala. Segunda parte da fala.",
            "shots": [broll("Primeira", "v1"), broll("Segunda", "v1")],
        },
        {
            "id": "S02",
            "narration": "Fulano de Tal disse isso. Depois veio outra coisa.",
            "shots": [
                photo("Fulano", "f1"),
                {
                    "kind": "lower_third",
                    "anchor": "disse isso",
                    "name": "Fulano",
                    "role": "autor",
                    "claims": [{"text": "Fulano é autor", "source_ids": ["source-01"]}],
                },
                broll("Depois", "v1"),
            ],
        },
    )
    changes = image_changes(shot_timings(scenes, CPS))
    assert len(changes) == 3  # v1, a foto e v1 de novo; a continuação e a tarja não trocam a tela


def test_a_reused_citation_counts_two_uses_of_one_asset() -> None:
    _, assets = fixture()
    frame = "crunchyroll-trailer-naomi"
    scenes = scenes_of(
        {"id": "S01", "narration": "Primeira menção ao quadro.", "shots": [photo("Primeira", frame)]},
        {"id": "S02", "narration": "Segunda menção ao quadro.", "shots": [photo("Segunda", frame)]},
    )
    n = script_numbers(scenes, {frame: assets[frame]}, CPS)
    assert len(n.citations) == 2 and len({c.asset_id for c in n.citations}) == 1


def test_same_patterns_as_the_niche_analysis() -> None:
    tree = ast.parse((SKILL / "analisar.py").read_text(encoding="utf-8"))
    node = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "SPOKEN" for t in n.targets)
    )
    theirs = {k.value: v.args[0].value for k, v in zip(node.keys, node.values, strict=True)}
    assert theirs == {name: rx.pattern for name, rx in SPOKEN.items()}


# --- bloco no outline ---


def test_block_is_stable_and_only_replaces_itself() -> None:
    scenes, assets = fixture()
    block = render_block(script_numbers(scenes, assets, CPS), None, CPS)
    assert block.startswith(BLOCK_START) and block.endswith(BLOCK_END)
    assert render_block(script_numbers(scenes, assets, CPS), None, CPS) == block
    outline = "# Outline\n\nTexto à mão.\n"
    once = replace_block(outline, block)
    assert replace_block(once, block) == once
    assert once.startswith(outline.rstrip("\n"))
    middle = "# A\n\n" + block + "\n\n# B escrito à mão\n"
    assert replace_block(middle, block.replace("cenas", "CENAS")).endswith("\n\n# B escrito à mão\n")


def test_adding_the_block_keeps_an_approved_script_valid(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    folder = store.path(EPISODE, "")
    shutil.copytree(FIXTURE, folder)
    (folder / "outline.md").write_text("# Outline\n\nTexto à mão.\n")
    for name in ("sources.json", "facts.json"):
        (folder / name).write_text("{}")
    review = JsonReviewGate(store)
    record_check(store, EPISODE, CheckVerdict.APPROVED, [], reviewer="verificador", now=lambda: FIXED_TIME)
    record_decision(
        store, review, EPISODE, Step.SCRIPT, Decision.APPROVED, reviewer="Dono", now=lambda: FIXED_TIME
    )
    scenes, assets = fixture()
    block = render_block(script_numbers(scenes, assets, CPS), None, CPS)
    outline = folder / "outline.md"
    outline.write_text(replace_block(outline.read_text(), block))
    assert strip_block(outline.read_bytes()) == b"# Outline\n\nTexto \xc3\xa0 m\xc3\xa3o.\n"
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert row.valid
    outline.write_text(outline.read_text().replace("Texto à mão.", "Texto mudou."))
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert not row.valid


# --- perfil do nicho ---


def brief(measure: str, high: float, low: float, force: str) -> FormatBrief:
    return FormatBrief.model_validate(
        {
            "schema": "formato_brief.v1",
            "nicho": "teste",
            "grupo": "H",
            "data": "2026-10-18",
            "n": 20,
            "medidas": {measure: {"alto": high, "baixo": low, "rho": 0.5, "n": 20, "forca": force}},
        }
    )


def test_only_a_strong_pattern_on_the_bottom_side_warns() -> None:
    scenes, assets = fixture()
    n = script_numbers(scenes, assets, CPS)  # voce_por_mil ~4,6
    assert format_warnings(n, brief("voce_por_mil", 9.0, 4.0, "pattern"))
    assert format_warnings(n, brief("voce_por_mil", 9.0, 4.0, "hint")) == []
    assert format_warnings(n, brief("voce_por_mil", 5.0, 1.0, "pattern")) == []  # perto do terço de cima
    assert format_warnings(n, None) == []


def test_brief_strength_rule() -> None:
    spec = importlib.util.spec_from_file_location("brief_skill", SKILL / "brief.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.strength(10, 5, 0.45, 20) == "pattern"
    assert module.strength(10, 5, -0.45, 20) == "hint"  # o terço de cima contradiz o ρ
    assert module.strength(10, 5, 0.39, 20) == "hint"
    assert module.strength(10, 5, 0.6, 18) == "hint"


def test_brief_from_the_saved_analysis(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("brief_skill", SKILL / "brief.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    (tmp_path / "tercos.csv").write_text(
        "grupo,terco,voce_por_mil,cortes_min\nH,baixo,4.6,19.0\nH,alto,7.9,14.9\n", encoding="utf-8"
    )
    (tmp_path / "correlacoes.csv").write_text(
        "grupo,medida,n,rho_log_views,rho_views_por_inscrito\nH,voce_por_mil,20,0.28,0.26\nH,cortes_min,20,-0.45,0.2\n",
        encoding="utf-8",
    )
    from datetime import date

    built = module.build(tmp_path, "teste", date(2026, 10, 18))["H"]
    parsed = FormatBrief.model_validate(built)
    assert parsed.medidas["voce_por_mil"].forca == "hint"
    assert parsed.medidas["cortes_min"].forca == "pattern"  # cima < baixo e ρ negativo


# --- vp check e vp numeros ---


def episode(tmp_path: Path) -> Path:
    folder = tmp_path / "data" / "episodes" / EPISODE
    shutil.copytree(FIXTURE, folder)
    (folder / "outline.md").write_text("# Outline\n\nTexto à mão.\n", encoding="utf-8")
    return folder


def warnings(tmp_path: Path) -> list[str]:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    return check_episode(store, EPISODE, chars_per_second=CPS).warnings


def test_check_warns_about_a_missing_or_stale_block(tmp_path: Path) -> None:
    folder = episode(tmp_path)
    assert any("sem o bloco de números" in w for w in warnings(tmp_path))
    scenes, assets = fixture()
    brief_ = FormatBrief.model_validate_json((folder / "formato-brief.json").read_text())
    block = render_block(script_numbers(scenes, assets, CPS), brief_, CPS)
    outline = folder / "outline.md"
    outline.write_text(replace_block(outline.read_text(), block))
    assert not any("bloco de números" in w for w in warnings(tmp_path))
    outline.write_text(outline.read_text().replace("21 cenas", "20 cenas"))
    assert any("bloco de números desatualizado" in w for w in warnings(tmp_path))


def test_check_warns_when_used_in_scenes_drifts(tmp_path: Path) -> None:
    folder = episode(tmp_path)
    path = folder / "assets" / "commons-kant-c1790.json"
    data = json.loads(path.read_text())
    path.write_text(json.dumps({**data, "used_in_scenes": ["S999"]}))
    assert any("commons-kant-c1790.json: used_in_scenes" in w for w in warnings(tmp_path))


def test_cli_numeros_writes_once_and_respects_approved_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    folder = episode(tmp_path)
    monkeypatch.chdir(make_root(tmp_path))
    assert main(["numeros", EPISODE]) == 0
    assert "outline.md: sem o bloco" in capsys.readouterr().out
    assert main(["numeros", EPISODE, "--escrever"]) == 0
    out = capsys.readouterr().out
    assert "gravado: outline.md, plano-imagens.md" in out and "Formato × nicho" in out
    assert (folder / "plano-imagens.md").is_file()
    assert main(["numeros", EPISODE, "--escrever"]) == 0
    assert "gravado: nada mudou" in capsys.readouterr().out
    for asset_id, status in (
        ("commons-kant-c1790", Status.APPROVED),
        ("pexels-video-4320605", Status.NEEDS_REVIEW),
    ):
        path = folder / "assets" / f"{asset_id}.json"
        data = json.loads(path.read_text())
        path.write_text(json.dumps({**data, "used_in_scenes": [], "review_status": status.value}))
    assert main(["numeros", EPISODE, "--used-in-scenes"]) == 0
    out = capsys.readouterr().out
    assert "commons-kant-c1790: aprovado, não mudo" in out
    fixed = json.loads((folder / "assets" / "pexels-video-4320605.json").read_text())
    assert fixed["used_in_scenes"][0] == "S119"
    kant = json.loads((folder / "assets" / "commons-kant-c1790.json").read_text())
    assert kant["used_in_scenes"] == []
