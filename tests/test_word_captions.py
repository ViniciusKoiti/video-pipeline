"""Legenda palavra a palavra (ADR 023): texto do roteiro com o tempo do reconhecedor, sem rede."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.media.word_captions import (
    VERSION,
    WORDS,
    CaptionWord,
    SceneSpeech,
    match_words,
    scene_word_frames,
    script_words,
    sync_words,
)
from app.providers.alignment.base import TimedWord
from app.providers.errors import QuotaExhausted


def heard(*items: tuple[str, int, int]) -> list[TimedWord]:
    return [TimedWord(text, start, end) for text, start, end in items]


def test_script_words_drop_the_pause_marks() -> None:
    assert script_words("Meia lata, <short pause> quanto custa?") == ["Meia", "lata,", "quanto", "custa?"]


def test_words_that_match_take_the_recognized_time() -> None:
    words = match_words(["Meia", "lata,", "quanto?"], heard(("meia", 100, 400), ("Lata", 450, 800),
                                                          ("quanto", 900, 1300)), 1500)
    assert words == [CaptionWord("Meia", 100, 400, True), CaptionWord("lata,", 450, 800, True),
                     CaptionWord("quanto?", 900, 1300, True)]


def test_a_number_spelled_out_splits_the_time_of_the_digits() -> None:
    script = ["tem", "trezentos", "e", "noventa", "gramas"]
    words = match_words(script, heard(("tem", 0, 200), ("390", 250, 1250), ("gramas", 1300, 1700)), 2000)
    middle = words[1:4]
    assert [w.matched for w in words] == [True, False, False, False, True]
    assert middle[0].start_ms == 200 and middle[-1].end_ms == 1300  # entre as vizinhas que casaram
    assert all(a.end_ms == b.start_ms for a, b in zip(middle, middle[1:], strict=False))
    assert middle[0].end_ms - middle[0].start_ms > middle[1].end_ms - middle[1].start_ms  # pelo tamanho


def test_without_anything_recognized_the_words_split_the_whole_scene() -> None:
    words = match_words(["um", "dois"], [], 1000)
    # pesos pelo tamanho mais o espaço: 3 e 5
    assert [(w.start_ms, w.end_ms, w.matched) for w in words] == [(0, 375, False), (375, 1000, False)]


def test_times_go_forward_and_stay_inside_the_audio() -> None:
    words = match_words(["a", "b", "c"], heard(("a", 500, 900), ("b", 400, 450), ("c", 1200, 2600)), 2000)
    starts = [w.start_ms for w in words]
    assert starts == sorted(starts)
    assert all(w.start_ms <= w.end_ms <= 2000 for w in words)


SCENES = [SceneSpeech("S01", "voice/S01-a.wav", "Meia lata.", 1000),
          SceneSpeech("S02", "voice/S02-b.wav", "Quanto custa?", 1200)]


def recognizer(calls: list[str]):  # type: ignore[no-untyped-def]
    def recognize(scene: SceneSpeech) -> list[TimedWord]:
        calls.append(scene.id)
        spoken = enumerate(scene.narration.split())
        return [TimedWord(w.strip(".?"), i * 300, i * 300 + 250) for i, w in spoken]

    return recognize


def test_only_scenes_with_a_new_audio_are_recognized(tmp_path: Path) -> None:
    path, calls = tmp_path / WORDS, []
    report = sync_words(path, SCENES, recognizer(calls), "groq/whisper")
    assert calls == ["S01", "S02"] and report.with_words == ["S01", "S02"] and report.unmatched == 0
    changed = [SCENES[0], SceneSpeech("S02", "voice/S02-c.wav", "Quanto custa agora?", 1500)]
    sync_words(path, changed, recognizer(calls), "groq/whisper")
    assert calls == ["S01", "S02", "S02"]
    data = json.loads(path.read_text())
    assert data["version"] == VERSION and [s["audio"] for s in data["scenes"]] == [s.audio for s in changed]


def test_without_the_request_a_scene_without_words_stays_on_phrase_captions(tmp_path: Path) -> None:
    path = tmp_path / WORDS
    sync_words(path, SCENES[:1], recognizer([]), "groq/whisper")
    report = sync_words(path, SCENES, None, "groq/whisper")
    assert report.with_words == ["S01"] and report.without == ["S02"]


def test_a_quota_error_keeps_what_was_already_recognized(tmp_path: Path) -> None:
    path, calls = tmp_path / WORDS, []
    ok = recognizer(calls)

    def recognize(scene: SceneSpeech) -> list[TimedWord]:
        if scene.id == "S02":
            raise QuotaExhausted("groq", "limite")
        return ok(scene)

    with pytest.raises(QuotaExhausted):
        sync_words(path, SCENES, recognize, "groq/whisper")
    assert [s["id"] for s in json.loads(path.read_text())["scenes"]] == ["S01"]


def test_scene_word_frames_are_relative_to_the_scene(tmp_path: Path) -> None:
    path = tmp_path / WORDS
    sync_words(path, SCENES, recognizer([]), "groq/whisper")
    frames = scene_word_frames(path, "voice/S02-b.wav", 30)
    assert frames == [{"text": "Quanto", "from": 0, "to": 8}, {"text": "custa?", "from": 9, "to": 16}]
    assert scene_word_frames(path, "voice/outra.wav", 30) == []
    path.write_text(json.dumps({"version": VERSION + 1, "scenes": []}))
    assert scene_word_frames(path, "voice/S02-b.wav", 30) == []
