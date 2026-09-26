"""Estados, cache por input_hash e imutabilidade do aprovado (etapa 10, §5, §2.6)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.pipeline.ports import EpisodeLocked, ImmutableManifest
from app.pipeline.schemas import SourcesManifest, Status, Step
from app.pipeline.state import (
    MANIFEST,
    Action,
    InvalidTransition,
    StaleApproval,
    StepResult,
    StepState,
    approve_step,
    compute_input_hash,
    load_state,
    plan,
    reopen_step,
    run_step,
    transition,
    write_output,
)
from app.providers.errors import QuotaExhausted
from app.storage.json_files import JsonFileStore
from tests.fakes import InMemoryReviewGate

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"
EP = "engine-test"


class Clock:
    def __init__(self) -> None:
        self.t = datetime(2026, 9, 26, 12, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.t += timedelta(seconds=1)
        return self.t


class Counter:
    """Ação de etapa que conta as execuções e grava sources.json pelo guarda de imutabilidade."""

    def __init__(self, store: JsonFileStore, needs_review: bool = True) -> None:
        self.store, self.needs_review, self.calls = store, needs_review, 0

    def __call__(self) -> StepResult:
        self.calls += 1
        sources = SourcesManifest.model_validate_json((FIXTURE / "sources.json").read_text())
        write_output(self.store, EP, "sources.json", sources)
        return StepResult(outputs=["sources.json"], needs_review=self.needs_review)


@pytest.fixture
def store(tmp_path: Path) -> JsonFileStore:
    return JsonFileStore(tmp_path / "episodes")


# --- Máquina de estados -------------------------------------------------------------------------


def test_transitions_follow_section_5() -> None:
    state = transition(StepState(), Status.RUNNING)
    state = transition(state, Status.NEEDS_REVIEW)
    state = transition(state, Status.APPROVED)
    assert transition(state, Status.COMPLETED).status is Status.COMPLETED
    with pytest.raises(InvalidTransition):
        transition(StepState(), Status.APPROVED)  # aprovar exige passar por revisão
    with pytest.raises(InvalidTransition):
        transition(StepState(status=Status.APPROVED), Status.RUNNING)  # refazer aprovado só reabrindo


@pytest.mark.parametrize(
    ("status", "same_input", "expected"),
    [
        (Status.PENDING, False, Action.RUN),
        (Status.FAILED, True, Action.RUN),
        (Status.NEEDS_REVIEW, True, Action.REUSE),
        (Status.NEEDS_REVIEW, False, Action.RUN),
        (Status.COMPLETED, True, Action.REUSE),
        (Status.COMPLETED, False, Action.RUN),
        (Status.APPROVED, True, Action.REUSE),
    ],
)
def test_cache_plan(status: Status, same_input: bool, expected: Action) -> None:
    state = StepState(status=status, input_hash="sha256:a")
    assert plan(state, "sha256:a" if same_input else "sha256:b") is expected


def test_approved_step_with_new_input_requires_reopening() -> None:
    with pytest.raises(StaleApproval, match="vp reopen"):
        plan(StepState(status=Status.APPROVED, input_hash="sha256:a"), "sha256:b")


def test_input_hash_covers_file_content_and_parameters(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    a.write_text("excerpt")
    first = compute_input_hash([a], {"model": "qwen3.5:9b"}, base=tmp_path)
    assert first == compute_input_hash([a], {"model": "qwen3.5:9b"}, base=tmp_path)
    assert first != compute_input_hash([a], {"model": "qwen3.5:4b"}, base=tmp_path)  # trocar o modelo refaz
    a.write_text("excerpt editado")
    assert first != compute_input_hash([a], {"model": "qwen3.5:9b"}, base=tmp_path)


# --- Cache e imutabilidade de ponta a ponta -----------------------------------------------------


def test_same_input_does_not_redo_work(store: JsonFileStore) -> None:
    action, clock = Counter(store), Clock()
    first = run_step(store, EP, Step.SOURCES, "sha256:v1", action, now=clock)
    second = run_step(store, EP, Step.SOURCES, "sha256:v1", action, now=clock)
    assert (first.action, second.action, action.calls) == (Action.RUN, Action.REUSE, 1)
    assert load_state(store, EP).get(Step.SOURCES).status is Status.NEEDS_REVIEW
    assert store.path(EP, MANIFEST).is_file()


def test_step_without_human_gate_reruns_when_input_changes(store: JsonFileStore) -> None:
    action, clock = Counter(store, needs_review=False), Clock()
    run_step(store, EP, Step.SUBS, "sha256:v1", action, now=clock)
    rerun = run_step(store, EP, Step.SUBS, "sha256:v2", action, now=clock)
    assert (rerun.action, rerun.state.status, action.calls) == (Action.RUN, Status.COMPLETED, 2)


def test_approved_output_is_never_overwritten(store: JsonFileStore) -> None:
    review, action, clock = InMemoryReviewGate(), Counter(store), Clock()
    run_step(store, EP, Step.SOURCES, "sha256:v1", action, now=clock)
    approve_step(store, review, EP, Step.SOURCES, reviewer="Vinicius Koiti", now=clock)
    with pytest.raises(StaleApproval):  # entrada nova não refaz etapa aprovada
        run_step(store, EP, Step.SOURCES, "sha256:v2", action, now=clock)
    sources = SourcesManifest.model_validate_json((FIXTURE / "sources.json").read_text())
    with pytest.raises(ImmutableManifest):  # nem escrita direta no arquivo aprovado
        write_output(store, EP, "sources.json", sources)
    assert action.calls == 1
    assert review.log(EP).entries[-1].input_hash == "sha256:v1"


def test_reopening_is_explicit_and_recorded(store: JsonFileStore) -> None:
    review, action, clock = InMemoryReviewGate(), Counter(store), Clock()
    run_step(store, EP, Step.SOURCES, "sha256:v1", action, now=clock)
    approve_step(store, review, EP, Step.SOURCES, reviewer="Vinicius Koiti", now=clock)
    reopen_step(
        store, review, EP, Step.SOURCES, reviewer="Vinicius Koiti", reason="fonte nova do jornal", now=clock
    )
    rerun = run_step(store, EP, Step.SOURCES, "sha256:v2", action, now=clock)
    assert (rerun.action, action.calls) == (Action.RUN, 2)
    assert review.log(EP).entries[-1].notes == "reaberta: fonte nova do jornal"
    with pytest.raises(InvalidTransition):  # só aprovado/concluído se reabre
        reopen_step(store, review, EP, Step.SCRIPT, reviewer="Vinicius Koiti", reason="x", now=clock)


def test_failure_is_recorded_and_raised(store: JsonFileStore) -> None:
    def action() -> StepResult:
        raise QuotaExhausted("workers_ai", "cota diária esgotada")

    with pytest.raises(QuotaExhausted):
        run_step(store, EP, Step.ASSETS, "sha256:v1", action, now=Clock())
    state = load_state(store, EP).get(Step.ASSETS)
    assert state.status is Status.FAILED and state.error.startswith("quota_exhausted")


def test_one_execution_per_episode(store: JsonFileStore) -> None:
    def nested() -> StepResult:
        run_step(store, EP, Step.SCRIPT, "sha256:x", Counter(store), now=Clock())  # segunda execução no meio
        return StepResult(outputs=[], needs_review=False)

    with pytest.raises(EpisodeLocked):
        run_step(store, EP, Step.SOURCES, "sha256:v1", nested, now=Clock())
