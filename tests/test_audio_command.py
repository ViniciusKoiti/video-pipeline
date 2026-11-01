"""RF7: `vp audio` confere o áudio de um vídeo pronto com o earshot (mockado: sem modelo, sem CPU)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.storage.json_files import JsonFileStore
from tests.test_earshot import timeline_json

CONTENT = {
    "scenes": [
        {"id": "a", "type": "title", "durationSec": 2.0},
        {"id": "b", "type": "title", "durationSec": 3.0},
        {"id": "c", "type": "title", "durationSec": 1.0},
    ]
}  # as cenas começam em 0, 2 e 5 s


class Env:
    def __init__(self, root: Path, python: Path | None = Path("/earshot/python")) -> None:
        self.root = root
        self.video = root / "final.mp4"
        self.video.write_bytes(b"mp4")
        self.content = root / "content.voz.json"
        self.content.write_text(json.dumps(CONTENT), encoding="utf-8")
        self.data = root / "data"
        self.store = JsonFileStore(self.data / "episodes")
        earshot = SimpleNamespace(python=python, threads=3)
        self.context = SimpleNamespace(
            settings=SimpleNamespace(earshot=earshot, data_dir=self.data), store=self.store
        )
        self.calls: list[tuple[Any, ...]] = []
        self.review: dict[str, Any] = timeline_json()

    def install(self, monkeypatch: pytest.MonkeyPatch, probe: float = 0.05) -> None:
        def fake(python: Path, media: Path, cuts: list[float], out: Path, threads: int) -> dict[str, Any]:
            self.calls.append((python, media, cuts, out, threads))
            return self.review

        monkeypatch.setattr("app.commands.audio.run_timeline", fake)
        monkeypatch.setattr("app.commands.audio.cpu_probe", lambda: probe)

    def run(self, *argv: str) -> int:
        args = build_parser().parse_args(["audio", *argv])
        return handled("vp audio", lambda: HANDLERS["audio"](args, self.context))  # type: ignore[arg-type]

    def kit(self) -> None:
        folder = self.data / "sfx" / "kit" / "sounds" / "pops"
        folder.mkdir(parents=True)
        (folder / "pop.wav").write_bytes(b"wav")
        sound = {
            "id": "pop",
            "name": "pop",
            "category": "pops",
            "file": "sounds/pops/pop.wav",
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
            "sha256": hashlib.sha256(b"wav").hexdigest(),
        }
        index = {"license": "CC0-1.0", "sounds": [sound]}
        (self.data / "sfx" / "kit" / "sounds.json").write_text(json.dumps(index), encoding="utf-8")

    def plan(self, *cues: dict[str, Any]) -> Path:
        path = self.root / "sfx.json"
        path.write_text(json.dumps({"cues": list(cues)}), encoding="utf-8")
        return path


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    environment = Env(tmp_path)
    environment.install(monkeypatch)
    return environment


def test_a_short_is_cut_at_the_start_of_each_scene_and_reported(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    assert env.run(str(env.video), "--content", str(env.content)) == 0
    [(python, media, cuts, out, threads)] = env.calls
    assert (python, media, cuts, threads) == (Path("/earshot/python"), env.video, [2.0, 5.0], 3)
    assert out == Path(f"{env.video}.earshot.json")  # padrão: ao lado do vídeo
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == (
        "audio: final.mp4 (38.2 s) volume efetivo -14.0 LUFS, pico -1.5 dBTP, trilha sem batida; "
        "2 corte(s), 2 com ataque a 40 ms (acaso ~37%)"
    )
    assert lines[1] == "  ok    5.20 s     +26 ms  chat message pop"
    assert lines[2] == "  ok   15.60 s      -9 ms  short swish"
    assert lines[-1] == f"json: {out}"


def test_a_beat_is_reported_and_a_custom_output_path_is_used(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    env.review = timeline_json(pulse=0.4)
    out = env.root / "medida.json"
    assert env.run(str(env.video), "--content", str(env.content), "--saida", str(out)) == 0
    assert env.calls[0][3] == out
    assert "trilha 75 bpm, pulso 0.40;" in capsys.readouterr().out


def test_a_long_video_is_cut_from_the_episode_scenes(env: Env) -> None:
    episode = {"scenes": [{"start_ms": 0}, {"start_ms": 4200}, {"start_ms": 9100}]}
    env.store.path("longo", "").mkdir(parents=True)
    env.store.path("longo", "episode.json").write_text(json.dumps(episode), encoding="utf-8")
    assert env.run(str(env.video), "--episodio", "longo") == 0
    assert env.calls[0][2] == [4.2, 9.1]


def test_the_sound_plan_adds_the_expected_attacks_as_cuts_and_checks_them(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    env.kit()
    plan = env.plan(
        {"sound": "pop", "scene": "b", "offset_s": 1.0},  # ataque em 2 + 1 − 0,1 + 0,05 = 2,95 s
        {"sound": "pop", "scene": "a", "offset_s": 0.2},  # 0,15 s: colado no começo, o earshot não mede
        {"sound": "pop", "scene": "c", "text": "ancorado"},  # ancorado na fala: fora desta conferência
        {"sound": "nada", "scene": "c"},  # fora do kit: o `vp short sfx` é quem acusa
        {"sound": "pop", "scene": "sumiu"},  # cena que não existe: idem
    )
    env.review = timeline_json(
        items=[
            {"t": 2.0, "offset_ms": 10.0, "status": "OK", "event": None},
            {"t": 2.95, "offset_ms": None, "status": "no hit", "event": None},
            {"t": 5.0, "offset_ms": 5.0, "status": "OK", "event": None},
        ]
    )
    assert env.run(str(env.video), "--content", str(env.content), "--sfx", str(plan)) == 1
    assert env.calls[0][2] == [2.0, 2.95, 5.0]
    out = capsys.readouterr().out.splitlines()
    assert any(
        line.startswith("  -- ") and line.endswith("(efeito no plano)") and "sem som" in line for line in out
    )
    assert any(line.startswith("  ok ") and "2.00 s" in line for line in out)
    assert sum("(efeito no plano)" in line for line in out) == 1
    assert "  problema: corte em 2.95 s tinha efeito no plano e ficou sem som" in out


def test_a_plan_without_the_kit_is_an_error_before_the_machine_probe(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = env.plan({"sound": "pop", "scene": "b"})
    assert env.run(str(env.video), "--content", str(env.content), "--sfx", str(plan)) == 1
    assert "vp audio: falta o SFX Kit em data/sfx/kit/" in capsys.readouterr().err
    assert env.calls == []


def test_out_of_target_volume_is_a_problem_and_the_exit_code_says_so(
    env: Env, capsys: pytest.CaptureFixture[str]
) -> None:
    env.review = timeline_json(lufs=-12.0)
    assert env.run(str(env.video), "--content", str(env.content)) == 1
    assert "  problema: volume efetivo (mono nos dois alto-falantes" in capsys.readouterr().out


def test_without_the_earshot_environment_nothing_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = Env(tmp_path, python=None)
    env.install(monkeypatch)
    assert env.run(str(env.video), "--content", str(env.content)) == 1
    assert "vp audio: configure EARSHOT_PYTHON no .env" in capsys.readouterr().err
    assert env.calls == []


def test_a_limited_machine_invalidates_the_measure_and_nothing_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = Env(tmp_path)
    env.install(monkeypatch, probe=0.31)
    assert env.run(str(env.video), "--content", str(env.content)) == 1
    assert "vp audio: máquina limitada (sonda 0.31 s > 0.3); medida inválida" in capsys.readouterr().err
    assert env.calls == []
    env.install(monkeypatch, probe=0.3)  # exatamente no limite ainda vale
    assert env.run(str(env.video), "--content", str(env.content)) == 0


def test_one_source_of_cuts_is_required_and_only_one(env: Env) -> None:
    for argv in ([str(env.video)], [str(env.video), "--episodio", "x", "--content", str(env.content)]):
        with pytest.raises(SystemExit) as stop:
            build_parser().parse_args(["audio", *argv])
        assert stop.value.code == 2
