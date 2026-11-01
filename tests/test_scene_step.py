"""RF2: etapa por cena com falha parcial e retomada, provada com ações falsas e o manifest.json em disco."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.pipeline.models.scene_run import SceneRun
from app.pipeline.ports import EpisodeLocked
from app.pipeline.scene_step import run_scenes
from app.pipeline.schemas import Status, Step
from app.pipeline.state import (
    Action,
    InputChanged,
    InputHash,
    OutputMissing,
    StaleApproval,
    StepState,
    approve_step,
    load_state,
    plan,
)
from app.providers.errors import ModelUnavailable, QuotaExhausted
from app.storage.json_files import JsonFileStore
from tests.fakes import InMemoryReviewGate

EP = "ep-voz"
SCENES = ["S01", "S02", "S03"]


class Clock:
    def __init__(self) -> None:
        self.t = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.t += timedelta(seconds=1)
        return self.t


class Maker:
    """Ação por cena: escreve `voice/<cena>.wav`, conta as tentativas e falha onde mandarem."""

    def __init__(self, store: JsonFileStore, failures: dict[str, Exception] | None = None) -> None:
        self.store, self.failures = store, dict(failures or {})
        self.calls: Counter[str] = Counter()

    def __call__(self, scene_id: str) -> list[str]:
        self.calls[scene_id] += 1
        if scene_id in self.failures:
            raise self.failures[scene_id]
        name = f"voice/{scene_id}.wav"
        path = self.store.path(EP, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"RIFF" + scene_id.encode())
        return [name]


@pytest.fixture
def store(tmp_path: Path) -> JsonFileStore:
    return JsonFileStore(tmp_path / "episodes")


def run(
    store: JsonFileStore, action: Callable[[str], list[str]], *, hash_: InputHash = "sha256:v1", **kw: bool
) -> SceneRun:
    return run_scenes(store, EP, Step.VOICE, hash_, SCENES, action, now=Clock(), **kw)


def state_of(store: JsonFileStore) -> StepState:
    return load_state(store, EP).get(Step.VOICE)


def test_a_failed_scene_leaves_the_others_valid_and_marks_the_step_incomplete(store: JsonFileStore) -> None:
    maker = Maker(store, {"S02": QuotaExhausted("gemini", "cota diária esgotada")})
    result = run(store, maker)
    assert (result.action, result.state.status) == (Action.RUN, Status.NEEDS_REVIEW)
    assert [(o.scene_id, o.status, o.reason) for o in result.outcomes] == [
        ("S01", Status.COMPLETED, ""), ("S02", Status.NEEDS_REVIEW, "quota_exhausted"),
        ("S03", Status.COMPLETED, ""),
    ]
    assert store.path(EP, "voice/S01.wav").is_file() and store.path(EP, "voice/S03.wav").is_file()
    assert state_of(store).pending_scenes == ["S02"]
    assert state_of(store).outputs == ["voice/S01.wav", "voice/S03.wav"]


def test_rerunning_the_same_input_tries_only_the_pending_scene(store: JsonFileStore) -> None:
    run(store, Maker(store, {"S02": ModelUnavailable("gemini", "modelo ausente")}))
    retry = Maker(store)
    result = run(store, retry)  # mesma entrada; needs_review parcial não impede a tentativa
    assert (result.action, result.state.status, dict(retry.calls)) == (
        Action.RUN, Status.COMPLETED, {"S02": 1},
    )
    assert state_of(store).pending_scenes == [] and len(state_of(store).outputs) == 3
    again = Maker(store)
    assert run(store, again).action is Action.REUSE and not again.calls


def test_awaiting_human_review_is_not_incomplete_production(store: JsonFileStore) -> None:
    run(store, Maker(store), needs_review=True)
    assert state_of(store).status is Status.NEEDS_REVIEW and state_of(store).pending_scenes == []
    again = Maker(store)
    result = run(store, again, needs_review=True)
    assert (result.action, dict(again.calls)) == (Action.REUSE, {})  # resultado íntegro: não se refaz


def test_reused_outcomes_are_rebuilt_from_disk_after_a_restart(store: JsonFileStore, tmp_path: Path) -> None:
    run(store, Maker(store, {"S02": QuotaExhausted("gemini", "cota")}))
    run(store, Maker(store))
    reborn = JsonFileStore(tmp_path / "episodes")  # processo novo: nenhum estado em memória
    result = run(reborn, Maker(reborn))
    assert result.action is Action.REUSE
    assert [o.value for o in result.outcomes] == [[f"voice/{s}.wav"] for s in SCENES]


def test_a_missing_or_empty_output_is_recovered_for_that_scene_only(store: JsonFileStore) -> None:
    run(store, Maker(store))
    store.path(EP, "voice/S01.wav").unlink()
    store.path(EP, "voice/S03.wav").write_bytes(b"")  # inválido: arquivo vazio
    retry = Maker(store)
    result = run(store, retry)
    assert (result.action, dict(retry.calls)) == (Action.RUN, {"S01": 1, "S03": 1})
    assert store.path(EP, "voice/S01.wav").read_bytes() and result.state.status is Status.COMPLETED


def approved(store: JsonFileStore) -> None:
    run(store, Maker(store), needs_review=True)
    approve_step(store, InMemoryReviewGate(), EP, Step.VOICE, reviewer="Dono", now=Clock())


def test_an_approved_step_is_never_recreated_automatically(store: JsonFileStore) -> None:
    approved(store)
    assert run(store, Maker(store), needs_review=True).action is Action.REUSE
    store.path(EP, "voice/S02.wav").unlink()
    recreate = Maker(store)
    with pytest.raises(OutputMissing, match="S02.*vp reopen"):
        run(store, recreate, needs_review=True)
    assert not recreate.calls and not store.path(EP, "voice/S02.wav").exists()
    with pytest.raises(StaleApproval):
        run(store, recreate, hash_="sha256:v2", needs_review=True)
    assert not recreate.calls


def test_the_lock_is_exclusive_and_released_on_error(store: JsonFileStore) -> None:
    def nested(scene_id: str) -> list[str]:
        run(store, Maker(store))  # segunda execução no meio: não se aninha o lock
        return []

    with pytest.raises(EpisodeLocked):
        run(store, nested)
    assert state_of(store).status is Status.FAILED
    assert run(store, Maker(store)).state.status is Status.COMPLETED  # o lock foi liberado


def test_input_changing_during_the_run_never_yields_a_mixed_result(store: JsonFileStore) -> None:
    current = {"hash": "sha256:v1"}

    def maker(scene_id: str) -> list[str]:
        out = Maker(store)(scene_id)
        current["hash"] = "sha256:v2"  # alguém edita a entrada no meio da etapa
        return out

    with pytest.raises(InputChanged):
        run(store, maker, hash_=lambda: current["hash"])
    assert state_of(store).status is Status.FAILED
    redo = Maker(store)
    run(store, redo, hash_=current["hash"])  # a entrada nova refaz todas as cenas
    assert dict(redo.calls) == {"S01": 1, "S02": 1, "S03": 1}


def test_an_unexpected_error_is_recorded_raised_and_keeps_finished_scenes(store: JsonFileStore) -> None:
    broken = Maker(store, {"S02": KeyError("bug")})
    with pytest.raises(KeyError):
        run(store, broken)
    assert dict(broken.calls) == {"S01": 1, "S02": 1}  # S03 não foi tentada
    state = state_of(store)
    assert state.status is Status.FAILED and state.error.startswith("erro_inesperado")
    assert list(state.scenes) == ["S01"]
    retry = Maker(store)
    run(store, retry)
    assert dict(retry.calls) == {"S02": 1, "S03": 1}  # S01 segue íntegra


def test_a_recoverable_failure_blocks_only_its_dependents(store: JsonFileStore) -> None:
    deps = {"S03": ["S02"]}
    result = run_scenes(
        store, EP, Step.VOICE, "sha256:v1", [*SCENES, "S04"],
        Maker(store, {"S02": QuotaExhausted("gemini", "cota")}), now=Clock(), depends_on=deps,
    )
    got = {o.scene_id: (o.status, o.reason) for o in result.outcomes}
    assert got == {
        "S01": (Status.COMPLETED, ""), "S02": (Status.NEEDS_REVIEW, "quota_exhausted"),
        "S03": (Status.PENDING, "blocked"), "S04": (Status.COMPLETED, ""),
    }
    retry = Maker(store)
    run_scenes(store, EP, Step.VOICE, "sha256:v1", [*SCENES, "S04"], retry, now=Clock(), depends_on=deps)
    assert dict(retry.calls) == {"S02": 1, "S03": 1}


def test_an_interrupted_scene_is_never_recorded_as_completed(store: JsonFileStore) -> None:
    class Interrupted(Maker):
        def __call__(self, scene_id: str) -> list[str]:
            if scene_id == "S02":
                store.path(EP, "voice").mkdir(parents=True, exist_ok=True)
                store.path(EP, "voice/S02.wav").write_bytes(b"RIFF-parcial")
                raise KeyboardInterrupt
            return super().__call__(scene_id)

    with pytest.raises(KeyboardInterrupt):
        run(store, Interrupted(store))
    state = state_of(store)
    assert state.status is Status.RUNNING and list(state.scenes) == ["S01"]  # nada de S02 como concluído
    retry = Maker(store)
    result = run(store, retry)  # o lock saiu com o processo: quem retoma é o próximo
    assert (dict(retry.calls), result.state.status) == ({"S02": 1, "S03": 1}, Status.COMPLETED)
    assert store.path(EP, "voice/S02.wav").read_bytes() == b"RIFFS02"


def test_an_action_that_leaves_no_output_is_an_error_not_a_completed_scene(store: JsonFileStore) -> None:
    with pytest.raises(OutputMissing, match="S01"):
        run(store, lambda scene_id: ["voice/inexistente.wav"])
    assert state_of(store).status is Status.FAILED and state_of(store).scenes == {}


@pytest.mark.parametrize(
    ("state", "missing", "expected"),
    [
        (StepState(status=Status.COMPLETED, input_hash="h"), (), Action.REUSE),
        (StepState(status=Status.COMPLETED, input_hash="h"), ("voice/S01.wav",), Action.RUN),
        (StepState(status=Status.RUNNING, input_hash="h"), (), Action.RUN),
    ],
)
def test_plan_reuses_only_an_intact_result(
    state: StepState, missing: tuple[str, ...], expected: Action
) -> None:
    assert plan(state, "h", missing=missing) is expected
