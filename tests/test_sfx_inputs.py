"""RF5 (G10): o `sounds.json` do kit e o `sfx.json` são validados na leitura, antes de qualquer uso."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.errors import PipelineError
from app.pipeline.sfx import load_kit, load_plan
from app.pipeline.sfx_inputs import SfxInputError, parse_kit
from tests.test_sfx import sound

ROOT = Path("kit")


def kit_text(*records: dict, **top: object) -> str:
    return json.dumps({"license": "CC0-1.0", "sounds": list(records), **top}, allow_nan=True)


def refuses(text: str, match: str) -> None:
    with pytest.raises(SfxInputError, match=match):
        parse_kit(ROOT, text)


def test_a_valid_kit_loads_with_its_sounds_and_ignores_the_fields_it_does_not_use() -> None:
    kit = parse_kit(ROOT, kit_text(sound("pop-in", tuning={"nota": "x"}), sound("riser", duration=2.2)))
    assert sorted(kit.sounds) == ["pop-in", "riser"] and kit.license == "CC0-1.0"
    assert (
        kit.sounds["pop-in"].onset == 0.05
        and kit.path(kit.sounds["pop-in"]) == ROOT / "sounds/pops/pop-in.wav"
    )


def test_a_missing_field_names_the_sound_and_the_field() -> None:
    record = sound("pop-in")
    del record["timing"]["body_end"]
    refuses(kit_text(record), r"som 1 \(pop-in\): falta o campo 'body_end'")
    no_sha = sound("riser")
    del no_sha["sha256"]
    refuses(kit_text(sound("pop-in"), no_sha), r"som 2 \(riser\): falta o campo 'sha256'")


@pytest.mark.parametrize(
    ("over", "match"),
    [
        ({"duration": 0}, "duration: Input should be greater than 0"),
        ({"duration": -1.0}, "duration: Input should be greater than 0"),
        ({"duration": float("nan")}, "duration"),
        ({"duration": float("inf")}, "duration"),
        ({"duration": "longo"}, "duration"),
        ({"sync": {"at": -0.1, "meets": "x", "how": ""}}, "sync_at"),
        ({"sync": {"at": 0.9, "meets": "x", "how": ""}}, r"sync.at \(0.9\) passa da duração"),
        ({"timing": {"onset": 0.4, "body_end": 0.3}}, "onset .* depois de timing.body_end"),
        ({"timing": {"onset": 0.0, "body_end": 0.9}}, r"body_end \(0.9\) passa da duração"),
        ({"under_voiceover_db": float("inf")}, "under_voiceover_db"),
        ({"sha256": "abc"}, "sha256"),
        ({"sha256": "G" * 64}, "sha256"),
        ({"file": "/etc/passwd"}, "file"),
        ({"file": "../fora/pop.wav"}, "file"),
        ({"file": ""}, "file"),
        ({"id": ""}, "id"),
    ],
)
def test_values_outside_the_contract_are_refused_with_the_sound_in_the_message(
    over: dict, match: str
) -> None:
    refuses(kit_text(sound("pop-in", **over)), rf"som 1 \(.*\): .*{match}")


def test_a_repeated_id_a_bad_shape_and_invalid_json_are_refused() -> None:
    refuses(kit_text(sound("pop-in"), sound("pop-in")), "o id 'pop-in' aparece mais de uma vez")
    refuses(json.dumps({"sounds": []}), "lista com ao menos um som")
    refuses(json.dumps({"sounds": "nada"}), "lista com ao menos um som")
    refuses(json.dumps([sound("pop-in")]), "lista com ao menos um som")
    refuses(kit_text(sound("pop-in"), "texto"), "som 2: o registro deve ser um objeto")
    refuses("{isto nao e json", "sounds.json: JSON inválido")


def test_the_loader_reads_the_kit_from_disk_and_a_missing_kit_is_none(tmp_path: Path) -> None:
    assert load_kit(tmp_path) is None
    folder = tmp_path / "sfx" / "kit"
    folder.mkdir(parents=True)
    (folder / "sounds.json").write_text(kit_text(sound("pop-in", duration=-3)), encoding="utf-8")
    with pytest.raises(SfxInputError, match="pop-in"):
        load_kit(tmp_path)


def plan_file(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "sfx.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_valid_plan_loads(tmp_path: Path) -> None:
    plan = load_plan(
        plan_file(tmp_path, '{"cues": [{"sound": "pop-in", "scene": "gancho", "offset_s": 0.5}]}')
    )
    assert [(c.sound, c.scene, c.offset_s) for c in plan.cues] == [("pop-in", "gancho", 0.5)]


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ('{"cues": [{"scene": "gancho"}]}', "cues.0.sound"),
        ('{"cues": [{"sound": "", "scene": "gancho"}]}', "cues.0.sound"),
        ('{"cues": [{"sound": "pop-in", "scene": ""}]}', "cues.0.scene"),
        ('{"cues": [{"sound": "pop-in", "scene": "g", "text": ""}]}', "cues.0.text"),
        ('{"cues": [{"sound": "pop-in", "scene": "g", "offset_s": NaN}]}', "cues.0.offset_s"),
        ('{"cues": [{"sound": "pop-in", "scene": "g", "gain_db": Infinity}]}', "cues.0.gain_db"),
        ('{"cues": [{"sound": "pop-in", "scene": "g", "gain_db": 9}]}', "cues.0.gain_db"),
        ('{"cues": "nada"}', "cues"),
        ("{isto nao e json", "Invalid JSON"),
    ],
)
def test_an_invalid_plan_is_a_pipeline_error_naming_the_field(tmp_path: Path, text: str, match: str) -> None:
    with pytest.raises(SfxInputError, match=f"sfx.json: .*{match}|sfx.json.*{match}") as raised:
        load_plan(plan_file(tmp_path, text))
    assert isinstance(raised.value, PipelineError)


def test_a_missing_plan_is_a_pipeline_error(tmp_path: Path) -> None:
    with pytest.raises(SfxInputError, match="sfx.json: não foi possível ler"):
        load_plan(tmp_path / "sfx.json")
