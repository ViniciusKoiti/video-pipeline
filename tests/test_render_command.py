"""RF7: `vp render` monta voz, tempo, legendas e `episode.json` e entrega ao motor; sem rede nem Remotion."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.gates import record_decision
from app.pipeline.schemas import Asset, Decision, EpisodeManifest, Status, Step
from app.providers.errors import QuotaExhausted
from app.settings.models.voice_polish_settings import VoicePolishSettings
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME, FakeBatchTTS, FakeRender, FakeWordAligner
from tests.test_assembly import scenes_manifest
from tests.test_gates import stock_asset

EP = "ep-montagem"


class Spy(FakeRender):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, bool]] = []

    def render(self, episode, episode_dir, out, *, preview=False):  # type: ignore[no-untyped-def]
        self.calls.append((out.name, preview))
        return super().render(episode, episode_dir, out, preview=preview)


class CountingAligner(FakeWordAligner):
    def __init__(self, error: Exception | None = None, stop_after: int = 99) -> None:
        super().__init__()
        self.heard: list[str] = []
        self.error, self.stop_after = error, stop_after

    def recognize_words(self, audio, language, prompt=""):  # type: ignore[no-untyped-def]
        if self.error and len(self.heard) >= self.stop_after:
            raise self.error
        self.heard.append(audio.name)
        return super().recognize_words(audio, language, prompt)


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.store = JsonFileStore(tmp_path / "data" / "episodes")
        self.review = JsonReviewGate(self.store)
        self.engine, self.aligner, self.tts = Spy(), CountingAligner(), FakeBatchTTS()
        self.store.write(EP, "scenes.json", scenes_manifest())
        folder = self.store.path(EP, "")
        for asset_id in ("pexels-video-1", "pexels-video-2"):
            (folder / "assets").mkdir(exist_ok=True)
            stock_asset(folder, asset_id)

    def context(self, tmp_path: Path) -> SimpleNamespace:
        settings = SimpleNamespace(
            data_dir=tmp_path / "data",
            providers=SimpleNamespace(word_aligner="fake"),
            groq_whisper=SimpleNamespace(model="fake-whisper"),
            voice_polish=VoicePolishSettings(),
        )
        return SimpleNamespace(
            store=self.store,
            review=self.review,
            settings=settings,
            tts=self.tts,
            tts_final=self.tts,
            tts_named=lambda name: self.tts,
            word_aligner=self.aligner,
            renderer=lambda fmt: self.engine,
        )

    def path(self, name: str) -> Path:
        return self.store.path(EP, name)

    def approve_assets(self) -> None:
        for asset_id in ("pexels-video-1", "pexels-video-2"):
            asset = self.store.read(EP, f"assets/{asset_id}.json", Asset)
            approved = Asset.model_validate({**asset.model_dump(), "review_status": Status.APPROVED})
            self.path(f"assets/{asset_id}.json").write_text(approved.model_dump_json(indent=2))


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def run(env: Env, tmp_path: Path, *argv: str, episode: str = EP) -> int:
    args = build_parser().parse_args(["render", episode, *argv])
    context = env.context(tmp_path)
    return handled("vp render", lambda: HANDLERS["render"](args, context))  # type: ignore[arg-type]


def test_a_preview_makes_voice_timing_captions_the_episode_json_and_calls_the_engine(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path, "--preview") == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("S01:") and "photo" in out[0] and out[1].startswith("S02:")
    assert any(line.startswith("voz: ") for line in out) and any(line.startswith("legenda: ") for line in out)
    assert any(line.startswith("ritmo: ") for line in out) and any(
        line.startswith("render: ") for line in out
    )
    assert env.engine.calls == [("preview.mp4", True)] and env.path("renders/preview.mp4").is_file()
    assert len(list(env.path("voice").glob("*.wav"))) == 2 and env.path("captions.srt").is_file()
    episode = EpisodeManifest.model_validate_json(env.path("episode.json").read_text())
    assert (episode.title, [s.id for s in episode.scenes]) == (f"{EP} (rascunho)", ["S01", "S02"])
    assert episode.scenes[1].start_ms == episode.scenes[0].duration_ms  # em sequência, pela voz real


def test_no_render_checks_and_writes_the_episode_but_never_calls_the_engine(env: Env, tmp_path: Path) -> None:
    assert run(env, tmp_path, "--no-render") == 0
    assert env.path("episode.json").is_file() and env.engine.calls == []
    assert not env.path("renders").exists()


def test_the_final_render_needs_every_asset_approved_in_gate_3(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path) == 1
    assert "vp render: render final incompleto (2)" in capsys.readouterr().err and env.engine.calls == []
    env.approve_assets()
    assert run(env, tmp_path) == 0
    assert env.engine.calls == [("final.mp4", False)]


def test_an_approved_gate_4_refuses_a_second_render_over_the_stamped_mp4(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path, "--preview") == 0
    record_decision(
        env.store, env.review, EP, Step.PREVIEW, Decision.APPROVED, reviewer="Dono", now=lambda: FIXED_TIME
    )
    capsys.readouterr()
    assert run(env, tmp_path, "--preview") == 1
    assert "carimbado pelo gate de preview" in capsys.readouterr().err
    assert len(env.engine.calls) == 1


def test_a_hand_edited_srt_survives_the_next_run_while_the_speech_is_the_same(
    env: Env, tmp_path: Path
) -> None:
    assert run(env, tmp_path, "--no-render") == 0
    srt = env.path("captions.srt")
    srt.write_text(srt.read_text().replace("Primeira", "PRIMEIRA"))
    assert run(env, tmp_path, "--no-render") == 0
    assert "PRIMEIRA" in srt.read_text()


def test_a_srt_outside_the_audio_stops_before_the_render(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path, "--no-render") == 0
    srt = env.path("captions.srt")
    srt.write_text("1\n00:00:00,000 --> 00:09:00,000\nlonga demais\n")
    capsys.readouterr()
    assert run(env, tmp_path, "--preview") == 1
    assert "vp render: captions.srt:" in capsys.readouterr().err and env.engine.calls == []


def test_word_captions_only_recognize_when_asked_and_are_reused_after(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path, "--no-render") == 0
    assert "palavra a palavra" not in capsys.readouterr().out and env.aligner.heard == []
    assert run(env, tmp_path, "--no-render", "--legenda-palavra") == 0
    assert "legenda palavra a palavra: 2 cena(s)" in capsys.readouterr().out and len(env.aligner.heard) == 2
    words = json.loads(env.path("captions.words.json").read_text())
    assert words["aligner"] == "fake/fake-whisper"
    assert run(env, tmp_path, "--no-render") == 0  # sem o pedido, reaproveita o arquivo
    assert "legenda palavra a palavra: 2 cena(s)" in capsys.readouterr().out and len(env.aligner.heard) == 2


def test_a_provider_stop_keeps_the_recognized_scenes_and_says_so(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env.aligner = CountingAligner(QuotaExhausted("fake", "limite"), stop_after=1)
    assert run(env, tmp_path, "--no-render", "--legenda-palavra") == 1
    err = capsys.readouterr().err
    assert "vp render: legenda palavra a palavra: quota_exhausted" in err and "rode de novo depois" in err
    assert len(json.loads(env.path("captions.words.json").read_text())["scenes"]) == 1  # a primeira ficou


def test_a_missing_script_is_an_error(env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(env, tmp_path, episode="nao-existe") == 1
    assert capsys.readouterr().err.startswith("vp render:")


def test_the_footer_source_comes_from_sources_json_when_the_file_exists(env: Env, tmp_path: Path) -> None:
    sources = Path("tests/fixtures/episodes/pilot-example/sources.json")
    script = json.loads(env.path("scenes.json").read_text())
    keyword = {
        "kind": "keyword",
        "text": "Primeira",
        "anchor": "Primeira",
        "claims": [{"text": "fato", "source_ids": ["source-01"]}],
    }
    script["scenes"][0]["shots"] = [keyword]
    env.path("scenes.json").write_text(json.dumps(script))
    assert run(env, tmp_path, "--no-render") == 0
    assert json.loads(env.path("episode.json").read_text())["scenes"][0]["shots"][0].get("source") is None
    env.path("sources.json").write_text(sources.read_text())
    assert run(env, tmp_path, "--no-render") == 0
    shot = json.loads(env.path("episode.json").read_text())["scenes"][0]["shots"][0]
    assert shot["source"]  # o rodapé sai das claims e do sources.json (ADR 011)


def test_an_approved_gate_4_refuses_a_new_captions_file_before_touching_it(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(env, tmp_path, "--preview") == 0
    record_decision(
        env.store, env.review, EP, Step.PREVIEW, Decision.APPROVED, reviewer="Dono", now=lambda: FIXED_TIME
    )
    before = env.path("captions.srt").read_text()
    script = json.loads(env.path("scenes.json").read_text())
    script["scenes"][0]["narration"] = "Primeira cena mudou de texto."
    env.path("scenes.json").write_text(json.dumps(script))
    capsys.readouterr()
    assert run(env, tmp_path, "--preview") == 1
    assert "captions.srt está carimbado pelo gate de preview" in capsys.readouterr().err
    assert env.path("captions.srt").read_text() == before


def with_music(env: Env, tmp_path: Path) -> None:
    from app.pipeline.schemas import MusicCatalog, MusicPlan
    from tests.test_music import cue, track

    plan = MusicPlan(episode_id=EP, cues=[cue(("S01", None), ("S02", None))])
    env.path("music.json").write_text(plan.model_dump_json())
    (tmp_path / "data" / "music").mkdir(parents=True)
    (tmp_path / "data" / "music" / "catalog.json").write_text(
        MusicCatalog(tracks=[track()]).model_dump_json()
    )
    env.path("assets/ytal-noite.json").write_text("{}")
    env.path("assets/ytal-noite.mp3").write_bytes(b"mp3")


def test_a_render_with_music_prints_the_music_and_the_final_loudness_with_the_alert_when_off_target(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    with_music(env, tmp_path)
    monkeypatch.setattr("app.commands.render.integrated_lufs", lambda path: -14.0)
    assert run(env, tmp_path, "--preview") == 0
    out = capsys.readouterr().out
    assert "trilha: 1 trecho(s), 1 faixa(s)" in out and out.rstrip().endswith("volume: -14.0 LUFS ok")
    monkeypatch.setattr("app.commands.render.integrated_lufs", lambda path: -20.0)
    env.path("renders/preview.mp4").unlink()
    assert run(env, tmp_path, "--preview") == 0
    assert "volume: -20.0 LUFS — alerta: volume final -20.0 LUFS" in capsys.readouterr().out
    assert run(env, tmp_path, "--no-render") == 0  # sem render, a loudness não se mede
    assert "volume:" not in capsys.readouterr().out
