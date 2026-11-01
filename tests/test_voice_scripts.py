"""RF6: os scripts de voz geram pela biblioteca e pelo narrador; sem rede, sem TTS real."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice import Narrator, VoiceIncomplete, VoiceLibrary
from app.providers.errors import QuotaExhausted
from app.storage.json_files import JsonFileStore
from scripts.provisorio import montar_episodio, shorts_tec
from tests.fakes import FakeBatchTTS, wav_duration_ms

SHORT_LINES = [
    shorts_tec.Line("gancho", "Uma lista ligada.", "hook"),
    shorts_tec.Line(None, "Fala solta, sem cena.", "neutral"),
    shorts_tec.Line("final", "Até a próxima.", "invite"),
]


EP = "ep-voz"


def store(tmp_path: Path) -> JsonFileStore:
    return JsonFileStore(tmp_path / "episodes")


def folder(tmp_path: Path) -> Path:
    return store(tmp_path).path(EP, "")


def names(where: Path) -> list[str]:
    return sorted(p.name for p in (where / "voice").iterdir())


# --- Short -----------------------------------------------------------------------------------------------


def test_the_short_voice_makes_one_wav_per_line_with_the_short_name_and_nothing_twice(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    paths = shorts_tec.generate_voice(tts, "pt-BR", SHORT_LINES, store(tmp_path), EP)
    assert [p.name.split("-fake-ptbr-")[0] for p in paths] == ["gancho", "fora-1", "final"]
    assert all(wav_duration_ms(p) > 0 for p in paths) and len(tts.calls) == 1 and tts.closed == 1
    again = FakeBatchTTS()
    assert shorts_tec.generate_voice(again, "pt-BR", SHORT_LINES, store(tmp_path), EP) == paths
    assert again.calls == []
    assert again.closed == 1  # fecha também quando nada precisou ser gerado


def test_the_short_voice_keeps_the_old_wav_when_the_new_one_fails_and_closes_the_tts(tmp_path: Path) -> None:
    first = shorts_tec.generate_voice(FakeBatchTTS(), "pt-BR", SHORT_LINES[:1], store(tmp_path), EP)
    old = first[0]
    changed = [shorts_tec.Line("gancho", "Outra frase.", "hook")]
    library = VoiceLibrary(folder(tmp_path) / "voice", Naming.SHORT)
    probe = Narrator(FakeBatchTTS(), "pt-BR", library, lambda w: 1.0)
    new_name = probe.key(SpeechLine("gancho", "Outra frase.", "hook")).file_name(Naming.SHORT)
    failing = FakeBatchTTS(scene_errors={new_name: QuotaExhausted("fake", "cota")})
    with pytest.raises(VoiceIncomplete, match=r"1 fala\(s\) sem WAV \(gancho: quota_exhausted"):
        shorts_tec.generate_voice(failing, "pt-BR", changed, store(tmp_path), EP)
    assert old.is_file() and failing.closed == 1  # a fala anterior segue utilizável
    shorts_tec.generate_voice(FakeBatchTTS(), "pt-BR", changed, store(tmp_path), EP)
    assert not old.exists() and names(folder(tmp_path)) == [new_name]


# --- Longo -----------------------------------------------------------------------------------------------


def scenes() -> ScenesManifest:
    raw = {
        "episode_id": "ep",
        "language": "pt-BR",
        "scenes": [
            {
                "id": "S01",
                "narration": "Primeira cena.",
                "visual_need": "contextual_stock",
                "search_query": "a",
            },
            {
                "id": "S02",
                "narration": "Uma frase com JSON.",
                "visual_need": "contextual_stock",
                "search_query": "b",
                "delivery": "turn",
            },
        ],
    }
    return ScenesManifest.model_validate(raw)


def test_the_long_voice_uses_the_long_name_and_the_glossary_and_prunes_only_after_success(
    tmp_path: Path,
) -> None:
    plain = montar_episodio.generate_voice(FakeBatchTTS(), scenes(), store(tmp_path), EP)
    assert sorted(plain) == ["S01", "S02"] and all(p.name.startswith(f"{s}-fake-") for s, p in plain.items())
    assert "ptbr" not in plain["S01"].name  # o longo não leva o idioma no nome
    glossary = {"termos": [{"escrita": "JSON", "fala": "jêison"}]}
    (folder(tmp_path) / "voice" / "glossary.json").write_text(json.dumps(glossary), encoding="utf-8")
    spelled = montar_episodio.generate_voice(FakeBatchTTS(), scenes(), store(tmp_path), EP)
    assert spelled["S01"] == plain["S01"]  # sem termo do glossário, o nome não muda
    assert spelled["S02"] != plain["S02"] and not plain["S02"].exists()  # a antiga saiu depois da nova pronta
    assert len(list((folder(tmp_path) / "voice").glob("S02-*.wav"))) == 1


def test_the_long_voice_stops_with_the_reason_per_scene_and_keeps_what_is_ready(tmp_path: Path) -> None:
    tts = FakeBatchTTS(max_batch_chars=1)
    probe = Narrator(tts, "pt-BR", VoiceLibrary(folder(tmp_path) / "voice", Naming.LONG), lambda w: 1.0)
    bad = probe.key(SpeechLine("S02", "Uma frase com JSON.", "turn")).file_name(Naming.LONG)
    failing = FakeBatchTTS(max_batch_chars=1, scene_errors={bad: QuotaExhausted("fake", "10 por dia")})
    with pytest.raises(VoiceIncomplete, match="S02: quota_exhausted"):
        montar_episodio.generate_voice(failing, scenes(), store(tmp_path), EP)
    assert failing.closed == 1 and len(list((folder(tmp_path) / "voice").glob("S01-*.wav"))) == 1
    ok = FakeBatchTTS(max_batch_chars=1)
    montar_episodio.generate_voice(ok, scenes(), store(tmp_path), EP)
    assert [c for call in ok.calls for c in call] == [bad]  # só a que faltava
