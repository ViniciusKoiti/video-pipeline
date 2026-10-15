"""Legenda por frase a partir do áudio real (#17, ADR 021), sem rede e sem modelo."""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.media.captions import (
    CAPTIONS,
    KEY,
    OLD_CAPTIONS,
    Cue,
    Phrase,
    SceneAudio,
    captions_key,
    episode_cues,
    parse_srt,
    phrases,
    review_hints,
    scene_cues,
    sync_captions,
    timing_problems,
    to_srt,
)
from app.media.pauses import silences


def test_pause_marks_and_sentences_split_the_phrases() -> None:
    found = phrases("Quanto custa? <short pause> Meia lata. Só isso.")
    assert found == [Phrase("Quanto custa?", pause_after=True), Phrase("Meia lata."), Phrase("Só isso.")]


def test_a_long_sentence_breaks_at_commas_then_near_the_middle() -> None:
    text = ("Preço, dividido pelo peso, vezes o que usa, meia lata pela receita são cento e noventa e "
            "cinco gramas")
    found = phrases(text, max_chars=40)
    assert all(len(p.text) <= 40 for p in found)
    assert " ".join(p.text for p in found) == text
    assert found[0].text == "Preço, dividido pelo peso,"


def test_a_single_word_longer_than_the_limit_stays_whole() -> None:
    assert phrases("Anticonstitucionalissimamente", max_chars=10) == [Phrase("Anticonstitucionalissimamente")]


def test_boundaries_fall_at_the_end_of_the_silence_near_the_estimate() -> None:
    scene = SceneAudio(start_ms=1000, duration_ms=6000, narration="Primeira frase aqui. Segunda frase aqui.",
                       silences_ms=[(2800, 3200)])
    cues, approximate = scene_cues(scene)
    assert approximate == 0
    assert cues == [Cue(1000, 4200, "Primeira frase aqui."), Cue(4200, 7000, "Segunda frase aqui.")]


def test_without_a_silence_nearby_the_boundary_is_proportional_and_counted() -> None:
    scene = SceneAudio(start_ms=0, duration_ms=4000, narration="Uma frase. Outra frase.",
                       silences_ms=[(200, 400)])
    cues, approximate = scene_cues(scene)
    assert approximate == 1
    assert cues == [Cue(0, 1833, "Uma frase."), Cue(1833, 4000, "Outra frase.")]  # 11 de 24 caracteres


def test_a_pause_mark_looks_further_for_its_silence() -> None:
    narration = "Se a sua receita pede meia lata, <short pause> quanto custa?"
    scene = SceneAudio(start_ms=0, duration_ms=5000, narration=narration, silences_ms=[(3500, 3900)])
    cues, approximate = scene_cues(scene)
    assert approximate == 0
    assert cues[0].end_ms == 3900


def test_many_phrases_in_a_short_scene_still_go_forward() -> None:
    scene = SceneAudio(start_ms=0, duration_ms=6, narration="A. B. C. D. E. F.", silences_ms=[])
    cues, _ = scene_cues(scene)
    assert [(c.start_ms, c.end_ms) for c in cues] == [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]


def test_episode_cues_cover_every_scene_back_to_back() -> None:
    scenes = [
        SceneAudio(start_ms=0, duration_ms=3000, narration="Primeira.", silences_ms=[]),
        SceneAudio(start_ms=3000, duration_ms=2000, narration="Segunda.", silences_ms=[]),
    ]
    cues, approximate = episode_cues(scenes)
    assert approximate == 0
    assert cues == [Cue(0, 3000, "Primeira."), Cue(3000, 5000, "Segunda.")]


def test_srt_round_trip_and_format_problems() -> None:
    cues = [Cue(0, 1500, "Olá."), Cue(1500, 3_723_004, "Tchau.")]
    text = to_srt(cues)
    assert "01:02:03,004" in text
    assert parse_srt(text) == (cues, [])
    found, problems = parse_srt("1\nsem tempo\nOlá\n\n2\n00:00:01,000 --> 00:00:02,000\n\n")
    assert found == []
    assert problems == ["bloco 1: sem a linha de tempo 'hh:mm:ss,mmm --> hh:mm:ss,mmm'", "bloco 2: sem texto"]


def test_timing_problems_reject_inverted_overlapping_and_beyond_the_audio() -> None:
    assert timing_problems([Cue(0, 1000, "a"), Cue(1000, 2000, "b")], 2000) == []
    problems = timing_problems([Cue(500, 400, "a"), Cue(300, 900, "b"), Cue(900, 2500, "c")], 2000)
    assert problems[0].startswith("bloco 1: fim")
    assert problems[1] == "bloco 2: começa antes de o bloco 1 acabar"
    assert problems[2].startswith("bloco 3: termina em 00:00:02,500")
    assert timing_problems([], 1000) == ["nenhum bloco de legenda"]


def test_review_hints_point_to_numbers_and_proper_names() -> None:
    cues = [Cue(0, 1, "São cento e noventa e cinco gramas."), Cue(1, 2, "Comprei no Carrefour."),
            Cue(2, 3, "Custa 18 reais."), Cue(3, 4, "Nada aqui.")]
    hints = dict(review_hints(cues))
    assert hints[1].startswith("número")
    assert hints[2].startswith("nome: Carrefour")
    assert hints[3].startswith("número")
    assert 4 not in hints


def test_the_edited_file_is_kept_until_the_speech_changes(tmp_path: Path) -> None:
    first = [Cue(0, 1000, "Texto gerado.")]
    assert sync_captions(tmp_path, first, "k1").startswith("gerada")
    (tmp_path / CAPTIONS).write_text(to_srt([Cue(0, 1000, "Texto revisado.")]))
    assert sync_captions(tmp_path, first, "k1").startswith("mantida")
    assert "revisado" in (tmp_path / CAPTIONS).read_text()
    assert sync_captions(tmp_path, [Cue(0, 900, "Voz nova.")], "k2").startswith("refeita")
    assert "Voz nova." in (tmp_path / CAPTIONS).read_text()
    assert "revisado" in (tmp_path / OLD_CAPTIONS).read_text()
    assert (tmp_path / KEY).read_text().strip() == "k2"


def test_the_key_changes_with_the_audio_and_the_limit() -> None:
    base = captions_key(["S01-kokoro-abc.wav"])
    assert base == captions_key(["S01-kokoro-abc.wav"])
    assert base != captions_key(["S01-chatterbox-abc.wav"])
    assert base != captions_key(["S01-kokoro-abc.wav"], max_chars=40)


def _speech(path: Path, pieces: list[tuple[str, float]]) -> Path:
    """Tom (fala) e silêncio alternados, como em test_pauses."""
    inputs: list[str] = []
    for kind, seconds in pieces:
        source = f"sine=frequency=220:sample_rate=24000:duration={seconds}" if kind == "tom" else (
            f"anullsrc=r=24000:cl=mono:d={seconds}"
        )
        inputs += ["-f", "lavfi", "-i", source]
    joined = "".join(f"[{i}:a]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", joined, "-map", "[a]",
                    "-ac", "1", "-c:a", "pcm_s16le", str(path)], check=True)
    return path


def test_real_audio_puts_the_switch_where_the_speech_starts_again(tmp_path: Path) -> None:
    wav = _speech(tmp_path / "s.wav", [("tom", 1.6), ("pausa", 0.4), ("tom", 1.4)])
    found = [(round(a * 1000), round(b * 1000)) for a, b in silences(wav)]
    narration = "Meia lata custa quanto? <short pause> Veja a conta."
    scene = SceneAudio(start_ms=0, duration_ms=3400, narration=narration, silences_ms=found)
    cues, approximate = scene_cues(scene)
    assert approximate == 0
    assert abs(cues[0].end_ms - 2000) <= 40
