"""Efeitos sonoros (ADR 035): o kit é lido e conferido, o plano é validado e cada som cai no momento certo."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.pipeline import sfx
from app.pipeline.sfx import SfxCue, SfxPlan, Speech, load_kit, plan_problems, resolve_sfx

WAV = b"RIFF....WAVEfake"


def sound(id_: str, **over) -> dict:
    record = {
        "id": id_,
        "name": id_,
        "category": "pops",
        "file": f"sounds/pops/{id_}.wav",
        "description": "",
        "use_for": [],
        "avoid_for": [],
        "tags": [],
        "duration": 0.5,
        "channels": 1,
        "sync": {"at": 0.1, "meets": "instant", "how": ""},
        "timing": {"audible_start": 0, "onset": 0.05, "peak": 0.1, "body_end": 0.3, "audible_end": 0.5},
        "fits_seconds": None,
        "level": {"lufs": -20, "true_peak_dbtp": -3, "tier": "medium"},
        "under_voiceover_db": -2,
        "adapt": {"rate": [1, 1], "notes": ""},
        "sha256": hashlib.sha256(WAV).hexdigest(),
    }
    record.update(over)
    return record


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    kit = tmp_path / "sfx" / "kit"
    (kit / "sounds" / "pops").mkdir(parents=True)
    records = [
        sound("pop-in"),
        sound("riser", **{"sync": {"at": 2.0, "meets": "arrival", "how": ""}, "duration": 2.2}),
        sound("boom", avoid_for=["On top of speech: it masks the voice"]),
    ]
    for record in records:
        (kit / record["file"]).write_bytes(WAV)
    (kit / "sounds.json").write_text(
        json.dumps({"license": "CC0-1.0", "sounds": records}), encoding="utf-8"
    )
    return tmp_path


STARTS = {"gancho": 0.0, "codigo": 5.0}
DURATIONS = {"gancho": 5.0, "codigo": 10.0}
NARRATIONS = {"gancho": "A mesma lista.", "codigo": "São dez milhões de nós, <short pause> embaralhados."}
SPEECHES = {"gancho": Speech(seconds=4.0), "codigo": Speech(seconds=8.0)}


def problems(data_dir: Path, *cues: SfxCue) -> tuple[list[str], list[str]]:
    plan = SfxPlan(cues=list(cues))
    return plan_problems(plan, load_kit(data_dir), STARTS, DURATIONS, NARRATIONS, SPEECHES)


def test_kit_is_read_and_missing_kit_is_an_error(data_dir: Path, tmp_path: Path) -> None:
    kit = load_kit(data_dir)
    assert kit is not None and kit.license == "CC0-1.0" and set(kit.sounds) == {"pop-in", "riser", "boom"}
    assert kit.sounds["boom"].covers_speech and not kit.sounds["pop-in"].covers_speech
    errors, _ = plan_problems(SfxPlan(cues=[]), None, STARTS, DURATIONS, NARRATIONS, SPEECHES)
    assert errors and "falta o SFX Kit" in errors[0]


def test_sound_outside_the_kit_or_with_wrong_hash_is_refused(data_dir: Path) -> None:
    errors, _ = problems(data_dir, SfxCue(sound="nada", scene="gancho"))
    assert errors == ["sfx.json, efeito 1 (nada em gancho): som fora do kit"]
    (data_dir / "sfx" / "kit" / "sounds" / "pops" / "pop-in.wav").write_bytes(b"outro")
    errors, _ = problems(data_dir, SfxCue(sound="pop-in", scene="gancho"))
    assert any("não bate com o sha256" in e for e in errors)


def test_anchor_must_exist_in_the_scene_speech_and_inside_the_scene(data_dir: Path) -> None:
    errors, _ = problems(
        data_dir,
        SfxCue(sound="pop-in", scene="fecho"),
        SfxCue(sound="pop-in", scene="codigo", text="não está"),
        SfxCue(sound="pop-in", scene="gancho", offset_s=9.0),
    )
    assert [e.split(": ")[-1] for e in errors] == [
        "a cena não existe no vídeo",
        "'não está' não aparece na fala da cena",
        "o momento (9.00 s) cai fora da cena",
    ]


def test_sound_that_covers_speech_over_the_voice_is_a_warning(data_dir: Path) -> None:
    errors, warnings = problems(data_dir, SfxCue(sound="boom", scene="gancho", offset_s=1.0))
    assert errors == [] and len(warnings) == 1 and "cobre a voz" in warnings[0]
    _, quiet = problems(data_dir, SfxCue(sound="boom", scene="gancho", offset_s=4.8))  # depois da fala
    assert quiet == []


def test_too_many_effects_in_ten_seconds_is_a_warning(data_dir: Path) -> None:
    cues = [SfxCue(sound="pop-in", scene="codigo", offset_s=i * 0.5) for i in range(10)]
    _, warnings = problems(data_dir, *cues)
    assert any("10 efeitos em 10 s" in w for w in warnings)


def test_each_sound_starts_at_its_moment_minus_the_sync_point(data_dir: Path) -> None:
    kit = load_kit(data_dir)
    assert kit is not None
    plan = SfxPlan(
        cues=[
            SfxCue(sound="pop-in", scene="codigo", text="embaralhados"),
            SfxCue(sound="riser", scene="gancho"),  # começaria em −2 s: entra cortado
            SfxCue(sound="pop-in", scene="codigo", offset_s=9.5, gain_db=3),  # depois da fala de 8 s
        ]
    )
    placed = resolve_sfx(plan, kit, STARTS, NARRATIONS, SPEECHES, voice_lufs=-19.0)
    spoken = "São dez milhões de nós, embaralhados."
    position = spoken.find("embaralhados")
    narration = NARRATIONS["codigo"]
    timeline = sfx.timeline_position(narration, position) / sfx.timeline_length(narration)
    assert placed[0].moment_s == round(5.0 + timeline * 8.0, 3)
    assert placed[0].start_s == round(placed[0].moment_s - 0.1, 3)
    assert placed[0].under_speech and placed[0].gain_db == -3.0 - 2.0  # voz 3 dB abaixo de −16, e sob a fala
    assert placed[1].start_s == 0.0 and placed[1].trim_s == 2.0
    assert not placed[2].under_speech and placed[2].gain_db == 3.0 - 3.0
    assert placed[0].file == data_dir / "sfx" / "kit" / "sounds" / "pops" / "pop-in.wav"


def test_mix_filter_adds_effects_after_the_voices() -> None:
    from scripts.provisorio.shorts_tec import mix_filter

    graph = mix_filter([0, 5000], 12.0, trims=[(0, 4), (0, 8)], effects=[(4900, 0.0, -2.0), (0, 2.0, 1.0)])
    assert "[3:a]aformat=sample_rates=48000:channel_layouts=mono,volume=-2.0dB,adelay=4900|4900[e0]" in graph
    assert "[4:a]atrim=start=2.000,asetpts=PTS-STARTPTS,aformat" in graph and "adelay=0|0[e1]" in graph
    assert "[v0][v1][e0][e1]amix=inputs=4:" in graph


def test_mix_goes_stereo_before_loudnorm_so_the_measure_matches_playback() -> None:
    from scripts.provisorio.shorts_tec import mix_filter

    graph = mix_filter([0], 5.0, trims=[(0, 4)])
    tail = graph.split("amix=")[1]
    assert tail.index("aformat=channel_layouts=stereo") < tail.index("loudnorm=")
