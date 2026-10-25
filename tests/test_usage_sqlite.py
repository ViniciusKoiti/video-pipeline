from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from pydantic import ValidationError

from app.pipeline.usage import AgentRun, UsageBudget, UsageError, UsageRequest
from app.storage.usage_sqlite import SQLiteUsageLedger


@pytest.fixture
def ledger(tmp_path: Path) -> SQLiteUsageLedger:
    return SQLiteUsageLedger(tmp_path / "telemetry" / "usage.sqlite3")


def execution(run_id: str = "root", **overrides: object) -> AgentRun:
    return AgentRun.model_validate(
        {
            "id": run_id,
            "episode_id": "pilot",
            "stage": "roteiro",
            "agent_name": "roteirista",
            **overrides,
        }
    )


def budget(budget_id: str = "tokens", **overrides: object) -> UsageBudget:
    return UsageBudget.model_validate(
        {
            "id": budget_id,
            "episode_id": "pilot",
            "metric": "tokens_total",
            "limit_value": 100,
            **overrides,
        }
    )


def request(key: str = "req-1", **overrides: object) -> UsageRequest:
    return UsageRequest.model_validate(
        {
            "event_key": key,
            "model": "fable-test",
            "occurred_at": "2026-10-24T12:00:00Z",
            "input_tokens": 10,
            "output_tokens": 5,
            "cache_read_tokens": 20,
            "cache_write_tokens": 5,
            "cost_usd_micros": 7,
            **overrides,
        }
    )


def balances(ledger: SQLiteUsageLedger) -> dict[str, dict]:
    return {row["id"]: row for row in ledger.report("auto-play", "pilot")["budgets"]}


def test_database_is_private_persistent_and_uses_supported_schema(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record("root", [request()])
    reopened = SQLiteUsageLedger(ledger.path)
    assert reopened.report("auto-play", "pilot")["models"][0]["input_tokens"] == 10
    assert ledger.path.stat().st_mode & 0o777 == 0o600
    with sqlite3.connect(ledger.path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1
        assert db.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_duplicates_and_restarts_do_not_count_twice(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    ledger.record("root", [request()])
    ledger = SQLiteUsageLedger(ledger.path)
    ledger.create_run(execution())
    ledger.reserve("root", {"tokens": 70})
    assert ledger.record("root", [request()]) == {"inserted": 0, "updated": 0, "duplicates": 1}
    row = balances(ledger)["tokens"]
    assert (row["spent_value"], row["reserved_value"], row["available_value"]) == (40, 30, 30)


def test_import_conflict_rolls_back_the_entire_batch(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.record("root", [request()])
    with pytest.raises(UsageError, match="conflitantes"):
        ledger.record("root", [request("req-2"), request(input_tokens=11)])
    assert ledger.report("auto-play", "pilot")["models"][0]["requests"] == 1
    assert balances(ledger)["tokens"]["spent_value"] == 40


def test_request_cannot_move_to_another_execution(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.create_run(execution("other"))
    ledger.record("root", [request()])
    with pytest.raises(UsageError, match="conflitantes"):
        ledger.record("other", [request()])


def test_provider_request_id_prevents_duplicate_events_with_different_keys(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record("root", [request(provider_request_id="provider-1")])
    with pytest.raises(sqlite3.IntegrityError):
        ledger.record("root", [request("other-key", provider_request_id="provider-1")])
    assert ledger.report("auto-play", "pilot")["models"][0]["requests"] == 1


def test_missing_usage_stays_unknown_and_can_be_completed(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.create_run(execution("next"))
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    ledger.record("root", [request(cache_read_tokens=None, cost_usd_micros=None)])
    row = balances(ledger)["tokens"]
    assert (row["spent_value"], row["reserved_value"], row["unknown_requests"]) == (0, 70, 1)
    assert ledger.finish("root", reconciled=True) == "pending_reconciliation"
    with pytest.raises(UsageError, match="desconhecido"):
        ledger.reserve("next", {"tokens": 1})
    assert ledger.record("root", [request()])["updated"] == 1
    assert ledger.finish("root", reconciled=True) == "closed"
    assert balances(ledger)["tokens"]["available_value"] == 60


def test_total_and_model_budget_do_not_double_count_the_report(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.set_budget(budget("fable", model_filter="fable-test"))
    ledger.set_budget(budget("haiku", model_filter="haiku-test"))
    ledger.record("root", [request(), request("req-2", model="haiku-test")])
    rows = balances(ledger)
    assert rows["tokens"]["spent_value"] == 80
    assert rows["fable"]["spent_value"] == rows["haiku"]["spent_value"] == 40
    assert sum(m["requests"] for m in ledger.report("auto-play", "pilot")["models"]) == 2


def test_budget_created_after_historical_import_includes_the_history(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record("root", [request()])
    ledger.set_budget(budget())
    assert balances(ledger)["tokens"]["spent_value"] == 40
    ledger.set_budget(budget(limit_value=30))
    assert balances(ledger)["tokens"]["available_value"] == -10
    with pytest.raises(UsageError, match="escopo"):
        ledger.set_budget(budget(episode_id="other"))


def test_child_consumes_parent_reservation_and_must_finish_first(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.create_run(execution("child", parent_run_id="root", agent_name="verificador"))
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    with pytest.raises(UsageError, match="raiz"):
        ledger.reserve("child", {"tokens": 10})
    ledger.record("child", [request()])
    assert balances(ledger)["tokens"]["reserved_value"] == 30
    assert ledger.finish("root", reconciled=True) == "pending_reconciliation"
    assert ledger.finish("child", reconciled=True) == "closed"
    assert ledger.finish("root", reconciled=True) == "closed"
    assert ledger.finish("root") == "closed"
    assert balances(ledger)["tokens"]["reserved_value"] == 0


def test_cross_episode_or_closed_parent_is_rejected(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    with pytest.raises(UsageError, match="mesmo projeto e episódio"):
        ledger.create_run(execution("bad", parent_run_id="root", episode_id="other"))
    ledger.finish("root")
    with pytest.raises(UsageError, match="encerrada"):
        ledger.create_run(execution("bad", parent_run_id="root"))


def test_all_reservations_roll_back_if_one_budget_is_insufficient(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.set_budget(budget("cost", metric="cost_usd_micros", limit_value=10))
    with pytest.raises(UsageError, match="Saldo insuficiente"):
        ledger.reserve("root", {"tokens": 40, "cost": 11})
    assert all(row["reserved_value"] == 0 for row in balances(ledger).values())


def test_concurrent_reservations_cannot_spend_the_same_balance(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution("a"))
    ledger.create_run(execution("b"))
    ledger.set_budget(budget(limit_value=60))
    barrier = Barrier(2)

    def reserve(run_id: str) -> bool:
        barrier.wait(timeout=5)
        try:
            ledger.reserve(run_id, {"tokens": 40})
            return True
        except UsageError:
            return False

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(reserve, ["a", "b"]))
    assert sorted(results) == [False, True]
    assert balances(ledger)["tokens"]["available_value"] == 20


def test_unreconciled_finish_retains_reservation_after_restart(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    ledger.record("root", [request()])
    assert ledger.finish("root") == "pending_reconciliation"
    assert balances(SQLiteUsageLedger(ledger.path))["tokens"]["reserved_value"] == 30


def test_late_usage_is_preserved_and_requires_another_reconciliation(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    ledger.record("root", [request()])
    ledger.finish("root", reconciled=True)
    ledger.record("root", [request("late")])
    report = ledger.report("auto-play", "pilot")
    assert report["runs"][0]["status"] == "pending_reconciliation"
    assert balances(ledger)["tokens"]["spent_value"] == 80
    assert ledger.finish("root", reconciled=True) == "closed"


def test_overspend_is_recorded_instead_of_rejected(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.set_budget(budget(limit_value=20))
    ledger.reserve("root", {"tokens": 20})
    ledger.record("root", [request()])
    assert balances(ledger)["tokens"]["available_value"] == -20


def test_scope_isolation_and_run_identity(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.create_run(execution("other", episode_id="other"))
    ledger.set_budget(budget())
    ledger.record("other", [request()])
    assert balances(ledger)["tokens"]["spent_value"] == 0
    assert ledger.report("another-project", "pilot")["models"] == []
    with pytest.raises(UsageError, match="outro contexto"):
        ledger.create_run(execution(agent_name="another"))


def test_raw_text_and_credentials_are_not_persisted(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record("root", [request(prompt="private-sentinel-xyz", authorization="private-sentinel-xyz")])
    assert b"private-sentinel-xyz" not in ledger.path.read_bytes()


@pytest.mark.parametrize("value", [-1, True, "10", 1.5, 2**63])
def test_counters_reject_invalid_or_out_of_range_values(value: object) -> None:
    with pytest.raises(ValidationError):
        request(input_tokens=value)


def test_timestamps_require_timezone_and_token_sum_fits_sqlite() -> None:
    with pytest.raises(ValidationError):
        request(occurred_at="2026-10-24T12:00:00")
    with pytest.raises(ValidationError):
        request(input_tokens=2**63 - 1)


def test_flat_claude_event_aliases_preserve_all_four_token_categories() -> None:
    record = UsageRequest.model_validate(
        {
            "request_id": "req-1",
            "model": "fable-test",
            "event.timestamp": "2026-10-24T09:00:00-03:00",
            "input_tokens": 1,
            "output_tokens": 2,
            "cache_read_tokens": 3,
            "cache_creation_tokens": 4,
            "cost_usd_micros": 5,
        }
    )
    assert record.event_key == record.provider_request_id == "req-1"
    assert record.cache_write_tokens == 4
    assert record.occurred_at.isoformat() == "2026-10-24T12:00:00+00:00"


def test_unknown_schema_version_is_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "future.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE future (value TEXT)")
        db.execute("INSERT INTO future VALUES ('keep-me')")
        db.execute("PRAGMA user_version=2")
    with pytest.raises(UsageError, match="Versão"):
        SQLiteUsageLedger(path)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT value FROM future").fetchone()[0] == "keep-me"


def test_report_groups_usage_by_stage_and_model(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution("research", stage="fichamento"))
    ledger.create_run(execution())
    ledger.record("research", [request("research-request")])
    ledger.record("root", [request()])
    rows = ledger.report("auto-play", "pilot")["models"]
    assert {(row["stage"], row["model"], row["requests"]) for row in rows} == {
        ("fichamento", "fable-test", 1),
        ("roteiro", "fable-test", 1),
    }


def test_zero_is_known_and_reservations_cannot_change_or_follow_usage(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.create_run(execution("other"))
    ledger.set_budget(budget())
    ledger.reserve("root", {"tokens": 70})
    with pytest.raises(UsageError, match="outra reserva"):
        ledger.reserve("root", {"tokens": 80})
    zero = request(
        input_tokens=0, output_tokens=0, cache_read_tokens=0, cache_write_tokens=0, cost_usd_micros=0
    )
    ledger.record("other", [zero])
    assert balances(ledger)["tokens"]["unknown_requests"] == 0
    with pytest.raises(UsageError, match="preceder"):
        ledger.reserve("other", {"tokens": 1})


def test_partial_updates_cannot_overflow_the_combined_token_count(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record(
        "root",
        [
            request(
                input_tokens=2**63 - 1, output_tokens=None, cache_read_tokens=None, cache_write_tokens=None
            )
        ],
    )
    with pytest.raises(ValidationError):
        ledger.record("root", [request(input_tokens=None)])


def test_sql_values_do_not_execute_as_statements(ledger: SQLiteUsageLedger) -> None:
    hostile_id = "pilot'; DROP TABLE runs; --"
    ledger.create_run(execution(episode_id=hostile_id))
    ledger.record("root", [request()])
    assert ledger.report("auto-play", hostile_id)["models"][0]["requests"] == 1


def test_import_and_late_enrichment_are_atomic_for_other_unique_keys(ledger: SQLiteUsageLedger) -> None:
    ledger.create_run(execution())
    ledger.record("root", [request("a"), request("b", provider_request_id="provider-b")])
    with pytest.raises(sqlite3.IntegrityError):
        ledger.record("root", [request("c"), request("a", provider_request_id="provider-b")])
    assert ledger.report("auto-play", "pilot")["models"][0]["requests"] == 2
