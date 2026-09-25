from pathlib import Path

import pytest

from app.media.probe import ProbeError, duration_ms
from app.providers.tts.kokoro import apply_lexicon
from tests.fakes import write_silence


def test_duration_comes_from_ffprobe(tmp_path: Path) -> None:
    wav = tmp_path / "S01.wav"
    write_silence(wav, 2_500)
    assert duration_ms(wav) == 2_500


def test_probe_fails_clearly_on_non_media(tmp_path: Path) -> None:
    bogus = tmp_path / "S01.wav"
    bogus.write_text("not audio")
    with pytest.raises(ProbeError, match="S01.wav"):
        duration_ms(bogus)


def test_lexicon_uses_kokoro_phoneme_syntax_in_one_pass() -> None:
    lexicon = {"Greely": "ɡɹˈili", "Lady Franklin Bay": "lˈeɪdi fɹˈæŋklɪn bˈeɪ", "Franklin": "fɹˈæŋklɪn"}
    text = "Greely reached Lady Franklin Bay. Franklin was far away; Greelys is not a match."
    assert apply_lexicon(text, lexicon) == (
        "[Greely](/ɡɹˈili/) reached [Lady Franklin Bay](/lˈeɪdi fɹˈæŋklɪn bˈeɪ/). "
        "[Franklin](/fɹˈæŋklɪn/) was far away; Greelys is not a match."
    )
    assert apply_lexicon(text, {}) == text
