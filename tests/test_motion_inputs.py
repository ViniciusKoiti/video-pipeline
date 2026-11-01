"""RF5 (G10): conteúdo do motion-video, fala gerada e narração validados na leitura; nada do kit se perde."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from app.pipeline.models.narration import Narration
from app.pipeline.motion_inputs import (
    MotionInputError,
    fit_content,
    load_content,
    load_narration,
    load_voiced,
    parse_content,
)


def content(**top: object) -> dict:
    return {
        "fps": 30,
        "scenes": [
            {"id": "gancho", "type": "hook", "durationSec": 2.0},
            {"id": "numero", "type": "number", "durationSec": 2.9},
            {"id": "final", "type": "end_card", "durationSec": 2.0},
        ],
        **top,
    }


def refuses(raw: object, match: str) -> None:
    with pytest.raises(MotionInputError, match=match):
        parse_content(raw, "content.pt.json")


# --- Os casos de `fit_durations` e `scene_starts` de antes, com a semântica nova --------------------------


def test_fitting_stretches_a_scene_until_the_speech_fits_and_never_shortens() -> None:
    fitted, rows = parse_content(content()).fitted({"gancho": 1.1, "numero": 3.84})
    # gancho: a fala cabe (1,1 + 0,3 < 2,0); numero: 3,84 + 0,3 = 4,14 → 4,2; final: sem fala, fica.
    assert [(r.scene, r.before, r.after, r.spoken) for r in rows] == [
        ("gancho", 2.0, 2.0, 1.1),
        ("numero", 2.9, 4.2, 3.84),
        ("final", 2.0, 2.0, None),
    ]
    assert [s["durationSec"] for s in fitted.raw["scenes"]] == [2.0, 4.2, 2.0]
    assert all("host" not in s for s in fitted.raw["scenes"])  # sem janela no vídeo, nenhuma cena ganha host


def test_fitting_ties_the_window_mouth_to_the_speech_and_respects_hidden_windows() -> None:
    raw = content(host={"assetId": "apresentador"})
    raw["scenes"][1]["host"] = {"corner": "top-left"}
    fitted, _ = parse_content(raw).fitted({"gancho": 1.1, "numero": 3.84})
    scenes = fitted.raw["scenes"]
    assert "host" not in scenes[0] and "host" not in scenes[2]  # a capa e o cartão final nunca têm janela
    assert scenes[1]["host"] == {"corner": "top-left", "speaking": [0.0, 3.84]}
    raw["scenes"][1]["host"] = False
    assert parse_content(raw).fitted({"numero": 1.0})[0].raw["scenes"][1]["host"] is False


def test_scene_starts_follow_the_whole_frames_of_the_motion_video() -> None:
    raw = content()
    raw["scenes"][1]["durationSec"] = 4.2
    assert parse_content(raw).starts() == {"gancho": 0.0, "numero": 2.0, "final": 6.2}
    assert parse_content({**raw, "fps": 25}).starts()["final"] == pytest.approx(6.2)
    assert parse_content({"scenes": raw["scenes"]}).fps == 30  # sem fps, o padrão do motion-video


# --- Nada do kit se perde e o original não muda ------------------------------------------------------


def test_fitting_returns_a_new_content_and_never_changes_the_original() -> None:
    raw = content(host={"assetId": "apresentador", "nested": {"a": [1, 2]}})
    snapshot = copy.deepcopy(raw)
    original = parse_content(raw)
    fitted, _ = original.fitted({"numero": 5.0})
    assert fitted is not original and original.raw == snapshot and raw == snapshot
    assert fitted.raw["scenes"][1]["durationSec"] == 5.3 and original.raw["scenes"][1]["durationSec"] == 2.9
    fitted.raw["host"]["nested"]["a"].append(3)  # o novo não compartilha estruturas com o original
    assert original.raw["host"]["nested"]["a"] == [1, 2]


def test_unknown_fields_survive_load_fit_and_dump(tmp_path: Path) -> None:
    raw = content(
        theme="editorial",
        meta={"autor": "Dono", "tags": ["pt", "açúcar"]},
        audio={"loudness": -14},
    )
    raw["scenes"][1].update({"value": 10_000_000, "label": "nós", "props": {"cor": "#fff", "peso": [1, 2]}})
    path = tmp_path / "content.pt.json"
    path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    fitted, _ = fit_content(load_content(path), {"numero": 3.84})
    dumped = json.loads(fitted.dumps())
    assert {k: v for k, v in dumped.items() if k != "scenes"} == {
        k: v for k, v in raw.items() if k != "scenes"
    }
    assert dumped["scenes"][1] == {**raw["scenes"][1], "durationSec": 4.2}
    assert "açúcar" in fitted.dumps() and fitted.dumps().endswith("}\n")  # sem escapar o texto


# --- O contrato do conteúdo --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda c: c.pop("scenes"), "'scenes' deve ser uma lista"),
        (lambda c: c.update(scenes=[]), "'scenes' deve ser uma lista"),
        (lambda c: c.update(scenes="nada"), "'scenes' deve ser uma lista"),
        (lambda c: c.update(fps=0), "fps deve ser um inteiro a partir de 1"),
        (lambda c: c.update(fps=-30), "fps deve ser um inteiro"),
        (lambda c: c.update(fps=29.97), "fps deve ser um inteiro"),
        (lambda c: c.update(fps=True), "fps deve ser um inteiro"),
        (lambda c: c.update(fps=math.nan), "fps deve ser um inteiro"),
        (lambda c: c["scenes"].append("texto"), "cena 4: a cena deve ser um objeto"),
        (lambda c: c["scenes"][0].pop("id"), "cena 1: id deve ser um texto não vazio"),
        (lambda c: c["scenes"][0].update(id=""), "cena 1: id deve ser um texto não vazio"),
        (lambda c: c["scenes"][0].update(id=7), "cena 1: id deve ser um texto não vazio"),
        (
            lambda c: c["scenes"][2].update(id="gancho"),
            r"cena 3 \(gancho\): o id aparece em mais de uma cena",
        ),
        (lambda c: c["scenes"][1].pop("durationSec"), r"cena 2 \(numero\): durationSec deve ser finito"),
        (lambda c: c["scenes"][1].update(durationSec=0), r"cena 2 \(numero\): durationSec deve ser finito"),
        (lambda c: c["scenes"][1].update(durationSec=-1.5), "durationSec deve ser finito e maior que zero"),
        (lambda c: c["scenes"][1].update(durationSec=math.nan), "durationSec deve ser finito"),
        (lambda c: c["scenes"][1].update(durationSec=math.inf), "durationSec deve ser finito"),
        (lambda c: c["scenes"][1].update(durationSec="2.9"), "durationSec deve ser finito"),
        (lambda c: c["scenes"][1].update(durationSec=True), "durationSec deve ser finito"),
        (lambda c: c["scenes"][1].pop("type"), r"cena 2 \(numero\): type deve ser um texto não vazio"),
    ],
)
def test_content_outside_the_contract_is_refused_naming_the_scene_and_the_field(mutate, match: str) -> None:  # type: ignore[no-untyped-def]
    raw = content()
    mutate(raw)
    refuses(raw, f"content.pt.json.*{match}|content.pt.json, {match}|{match}")


def test_a_content_that_is_not_an_object_or_not_json_is_refused(tmp_path: Path) -> None:
    refuses([1, 2], "'scenes' deve ser uma lista")
    refuses(None, "'scenes' deve ser uma lista")
    bad = tmp_path / "content.json"
    bad.write_text("{isto nao e json", encoding="utf-8")
    with pytest.raises(MotionInputError, match="content.json: JSON inválido"):
        load_content(bad)
    with pytest.raises(MotionInputError, match="content.json: não foi possível ler"):
        load_content(tmp_path / "nada" / "content.json")


@pytest.mark.parametrize(
    ("seconds", "match"),
    [
        ({"fantasma": 1.0}, "falas de cenas que não existem no JSON: fantasma"),
        ({"numero": -1.0}, "duração de fala inválida .* em: numero"),
        ({"numero": math.nan}, "duração de fala inválida"),
        ({"numero": math.inf}, "duração de fala inválida"),
    ],
)
def test_speech_durations_are_checked_before_fitting(seconds: dict, match: str) -> None:
    with pytest.raises(MotionInputError, match=match):
        fit_content(parse_content(content()), seconds)


# --- A narração --------------------------------------------------------------------------------------


def narration_file(tmp_path: Path, **raw: object) -> Path:
    path = tmp_path / "narracao.pt.json"
    path.write_text(json.dumps({"language": "pt-BR", "lines": [{"scene": "gancho", "text": "Oi."}], **raw}))
    return path


def test_a_valid_narration_loads_with_trimmed_text_and_no_scene_for_extra_lines(tmp_path: Path) -> None:
    lines = [{"scene": "gancho", "text": "  Oi.  ", "delivery": "hook"}, {"scene": None, "text": "Fora."}]
    narration = load_narration(narration_file(tmp_path, lines=lines))
    assert isinstance(narration, Narration)
    assert [(x.scene, x.text, x.delivery) for x in narration.lines] == [
        ("gancho", "Oi.", "hook"),
        (None, "Fora.", None),
    ]


@pytest.mark.parametrize("delivery", ["hook", "turn", "calm", "invite", "neutral"])
def test_the_five_deliveries_of_adr_022_are_accepted(tmp_path: Path, delivery: str) -> None:
    lines = [{"scene": "a", "text": "Oi.", "delivery": delivery}]
    assert load_narration(narration_file(tmp_path, lines=lines)).lines[0].delivery == delivery


@pytest.mark.parametrize(
    ("raw", "match"),
    [
        ({"lines": []}, "lines"),
        ({"lines": [{"scene": "a", "text": "   "}]}, "lines.0.text"),
        ({"lines": [{"scene": "a"}]}, "lines.0.text"),
        ({"lines": [{"scene": "", "text": "Oi."}]}, "lines.0.scene"),
        ({"lines": [{"scene": "a", "text": "Oi.", "delivery": "gritado"}]}, "lines.0.delivery"),
        ({"lines": [{"scene": "a", "text": "Oi."}, {"scene": "a", "text": "Tchau."}]}, "cenas da narração"),
        ({"lines": [{"scene": "a", "text": "Oi.", "extra": 1}]}, "extra"),
        ({"language": None}, "language"),
    ],
)
def test_a_narration_outside_the_contract_is_refused_with_the_field(
    tmp_path: Path, raw: dict, match: str
) -> None:
    with pytest.raises(MotionInputError, match=f"narracao.pt.json: .*{match}"):
        load_narration(narration_file(tmp_path, **raw))


def test_a_missing_or_invalid_narration_file_is_a_motion_input_error(tmp_path: Path) -> None:
    with pytest.raises(MotionInputError, match="não foi possível ler"):
        load_narration(tmp_path / "nada.json")
    bad = tmp_path / "ruim.json"
    bad.write_text("{x")
    with pytest.raises(MotionInputError, match="ruim.json: registro"):
        load_narration(bad)


# --- A fala gerada -----------------------------------------------------------------------------------


def voiced_folder(tmp_path: Path, lines: list[dict]) -> tuple[Path, Path]:
    (tmp_path / "voice").mkdir(exist_ok=True)
    for line in lines:
        wav = line.get("wav")
        if isinstance(wav, str) and wav.startswith("voice/"):
            (tmp_path / wav).write_bytes(b"RIFF")
    record = tmp_path / "narracao.pt.voz.json"
    record.write_text(json.dumps({"lines": lines}))
    return tmp_path, record


def seconds(_: Path) -> float:
    return 3.0


def line(scene: str | None = "gancho", wav: str = "voice/gancho.wav", speech: object = (0.1, 2.8)) -> dict:
    return {"scene": scene, "wav": wav, "speech": list(speech) if isinstance(speech, tuple) else speech}


def test_a_valid_voiced_record_maps_each_scene_to_its_wav_and_spoken_span(tmp_path: Path) -> None:
    folder, record = voiced_folder(
        tmp_path, [line(), line("numero", "voice/numero.wav", (0.0, 3.04)), line(None, "voice/fora-1.wav")]
    )
    speeches = load_voiced(folder, record, seconds)
    assert sorted(speeches) == ["gancho", "numero"]  # a fala sem cena não entra no mapa
    assert speeches["gancho"].wav == folder / "voice/gancho.wav" and speeches[
        "gancho"
    ].seconds == pytest.approx(2.7)
    assert speeches["numero"].end == 3.04  # até 50 ms além do WAV medido: arredondamento do ffprobe


@pytest.mark.parametrize(
    ("bad", "match"),
    [
        (line(wav="../fora.wav"), "wav deve ser um caminho relativo"),
        (line(wav="/etc/passwd"), "wav deve ser um caminho relativo"),
        (line(wav="voice\\gancho.wav"), "wav deve ser um caminho relativo"),
        (line(wav=""), "wav deve ser um caminho relativo"),
        (line(wav="voice/sumiu.wav"), r"falta o WAV voice/sumiu.wav \(rode `voz` de novo\)"),
        (line(speech=(0.5, 3.2)), "não cabe no WAV"),
        (line(speech=(-0.1, 2.0)), "não cabe no WAV"),
        (line(speech=(2.0, 2.0)), "não cabe no WAV"),
        (line(speech=(2.5, 1.0)), "não cabe no WAV"),
        (line(speech=[0.1]), r"speech deve ser \[começo, fim\]"),
        (line(speech=[0.1, "2"]), r"speech deve ser \[começo, fim\]"),
        (line(speech=[0.1, math.nan]), r"speech deve ser \[começo, fim\]"),
        (line(speech=[True, 2.0]), r"speech deve ser \[começo, fim\]"),
        (line(speech=None), r"speech deve ser \[começo, fim\]"),
    ],
)
def test_a_voiced_line_outside_the_contract_is_refused_with_the_record_and_line(
    tmp_path: Path, bad: dict, match: str
) -> None:
    (tmp_path / "voice").mkdir()
    (tmp_path / "voice" / "gancho.wav").write_bytes(b"RIFF")
    folder, record = voiced_folder(tmp_path, [bad])
    (tmp_path / "voice" / "sumiu.wav").unlink(missing_ok=True)  # o caso "WAV ausente"
    with pytest.raises(MotionInputError, match=f"narracao.pt.voz.json, fala 1: .*{match}"):
        load_voiced(folder, record, seconds)


def test_a_scene_with_two_speeches_a_missing_record_and_a_bad_shape_are_refused(tmp_path: Path) -> None:
    folder, record = voiced_folder(tmp_path, [line(), line("gancho", "voice/gancho.wav", (0.2, 2.0))])
    with pytest.raises(MotionInputError, match="fala 2: a cena 'gancho' tem mais de uma fala"):
        load_voiced(folder, record, seconds)
    with pytest.raises(MotionInputError, match=r"falta nada.voz.json: rode `voz` antes"):
        load_voiced(folder, folder / "nada.voz.json", seconds)
    for content_ in ('{"lines": []}', '{"lines": "x"}', "[1]", '{"lines": ["texto"]}', "{x"):
        record.write_text(content_)
        with pytest.raises(MotionInputError):
            load_voiced(folder, record, seconds)
