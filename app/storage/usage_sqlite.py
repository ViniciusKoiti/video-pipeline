"""Registro local de consumo e reservas, com transações curtas e sem rede (ADR 032)."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator, Mapping, Sequence
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.pipeline.usage import TOKEN_FIELDS, AgentRun, Count, UsageBudget, UsageError, UsageRequest

SCHEMA = (
    """CREATE TABLE runs (
        id TEXT PRIMARY KEY, project TEXT NOT NULL, episode_id TEXT NOT NULL,
        stage TEXT NOT NULL, agent_name TEXT NOT NULL, session_id TEXT,
        parent_run_id TEXT REFERENCES runs(id),
        status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','pending_reconciliation','closed')),
        started_at TEXT NOT NULL, finished_at TEXT
    ) STRICT""",
    """CREATE TABLE requests (
        event_key TEXT PRIMARY KEY, provider_request_id TEXT UNIQUE,
        run_id TEXT NOT NULL REFERENCES runs(id), model TEXT NOT NULL, occurred_at TEXT NOT NULL,
        input_tokens INTEGER CHECK(input_tokens >= 0), output_tokens INTEGER CHECK(output_tokens >= 0),
        cache_read_tokens INTEGER CHECK(cache_read_tokens >= 0),
        cache_write_tokens INTEGER CHECK(cache_write_tokens >= 0),
        cost_usd_micros INTEGER CHECK(cost_usd_micros >= 0), duration_ms INTEGER CHECK(duration_ms >= 0),
        status TEXT NOT NULL CHECK(status IN ('success','error'))
    ) STRICT""",
    """CREATE TABLE budgets (
        id TEXT PRIMARY KEY, project TEXT NOT NULL, episode_id TEXT NOT NULL,
        model_filter TEXT NOT NULL, metric TEXT NOT NULL CHECK(metric IN ('tokens_total','cost_usd_micros')),
        limit_value INTEGER NOT NULL CHECK(limit_value >= 0),
        spent_value INTEGER NOT NULL DEFAULT 0 CHECK(spent_value >= 0),
        UNIQUE(project, episode_id, model_filter, metric)
    ) STRICT""",
    """CREATE TABLE reservations (
        budget_id TEXT NOT NULL REFERENCES budgets(id), run_id TEXT NOT NULL REFERENCES runs(id),
        initial_value INTEGER NOT NULL CHECK(initial_value >= 0),
        remaining_value INTEGER NOT NULL CHECK(remaining_value >= 0),
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','pending_reconciliation','closed')),
        PRIMARY KEY(budget_id, run_id)
    ) STRICT""",
    "CREATE INDEX requests_run ON requests(run_id)",
    "CREATE INDEX runs_scope ON runs(project, episode_id)",
    "CREATE INDEX runs_parent ON runs(parent_run_id)",
)


class SQLiteUsageLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
        with self._transaction() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise UsageError("Versão do banco de consumo não suportada; nenhum dado foi migrado.")
            if version == 0:
                if db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
                    raise UsageError("O arquivo já contém tabelas de outro banco.")
                for statement in SCHEMA:
                    db.execute(statement)
                db.execute("PRAGMA user_version=1")

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(self.path, timeout=5, isolation_level=None)) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA synchronous=FULL")
            # shortcut: rollback journal evita o WAL-reset no SQLite 3.50.4 local; avaliar WAL após upgrade.
            if db.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
                raise UsageError("O banco de consumo precisa usar journal_mode=DELETE (ADR 032).")
            yield db

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    @staticmethod
    def _run(db: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        run = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if run is None:
            raise UsageError("Execução de consumo não encontrada.")
        return run

    def _root(self, db: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        run = self._run(db, run_id)
        while run["parent_run_id"]:
            run = self._run(db, run["parent_run_id"])
        return run

    @staticmethod
    def _totals(db: sqlite3.Connection, budget: sqlite3.Row, root_id: str | None = None) -> sqlite3.Row:
        value = (
            "q.cost_usd_micros"
            if budget["metric"] == "cost_usd_micros"
            else "+".join(f"q.{name}" for name in TOKEN_FIELDS)
        )
        return db.execute(
            f"""WITH RECURSIVE tree(id) AS (
                SELECT id FROM runs WHERE id=?
                UNION ALL SELECT r.id FROM runs r JOIN tree t ON r.parent_run_id=t.id
            )
            SELECT COALESCE(SUM({value}),0) AS spent, COUNT(*)-COUNT({value}) AS unknown
            FROM requests q JOIN runs r ON q.run_id=r.id
            WHERE r.project=? AND r.episode_id=? AND (?='*' OR q.model=?)
            AND (? IS NULL OR r.id IN (SELECT id FROM tree))""",
            (
                root_id,
                budget["project"],
                budget["episode_id"],
                budget["model_filter"],
                budget["model_filter"],
                root_id,
            ),
        ).fetchone()

    def _sync(self, db: sqlite3.Connection, scope: Mapping[str, Any]) -> None:
        for budget in db.execute(
            "SELECT * FROM budgets WHERE project=? AND episode_id=?", (scope["project"], scope["episode_id"])
        ).fetchall():
            total = self._totals(db, budget)
            db.execute("UPDATE budgets SET spent_value=? WHERE id=?", (total["spent"], budget["id"]))
            for reservation in db.execute(
                "SELECT * FROM reservations WHERE budget_id=? AND status!='closed'", (budget["id"],)
            ).fetchall():
                used = self._totals(db, budget, reservation["run_id"])["spent"]
                db.execute(
                    "UPDATE reservations SET remaining_value=? WHERE budget_id=? AND run_id=?",
                    (max(0, reservation["initial_value"] - used), budget["id"], reservation["run_id"]),
                )

    def create_run(self, run: AgentRun) -> None:
        with self._transaction() as db:
            existing = db.execute("SELECT * FROM runs WHERE id=?", (run.id,)).fetchone()
            if existing:
                if any(existing[key] != value for key, value in run.model_dump().items()):
                    raise UsageError("O id da execução já pertence a outro contexto.")
                return
            if run.parent_run_id:
                parent = self._run(db, run.parent_run_id)
                if (parent["project"], parent["episode_id"]) != (run.project, run.episode_id):
                    raise UsageError("Subagente precisa pertencer ao mesmo projeto e episódio.")
                if parent["status"] != "open" or self._root(db, parent["id"])["status"] != "open":
                    raise UsageError("Execução de origem já foi encerrada ou aguarda conciliação.")
            data = run.model_dump()
            columns = ",".join(data)
            db.execute(
                f"INSERT INTO runs ({columns},started_at) VALUES ({','.join('?' for _ in data)},?)",
                (*data.values(), datetime.now(UTC).isoformat()),
            )

    def set_budget(self, budget: UsageBudget) -> None:
        with self._transaction() as db:
            existing = db.execute("SELECT * FROM budgets WHERE id=?", (budget.id,)).fetchone()
            if existing and any(
                existing[key] != value for key, value in budget.model_dump(exclude={"limit_value"}).items()
            ):
                raise UsageError("O id do orçamento já pertence a outro escopo ou unidade.")
            db.execute(
                """INSERT INTO budgets (id,project,episode_id,model_filter,metric,limit_value)
                VALUES (?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET limit_value=excluded.limit_value""",
                tuple(budget.model_dump().values()),
            )
            self._sync(db, budget.model_dump())

    def reserve(self, run_id: str, allocations: Mapping[str, int]) -> None:
        amounts = TypeAdapter(dict[str, Count]).validate_python(dict(allocations))
        with self._transaction() as db:
            run = self._run(db, run_id)
            if run["parent_run_id"]:
                raise UsageError("Reserve na execução raiz; os subagentes compartilham essa reserva.")
            if run["status"] != "open":
                raise UsageError("Execução encerrada ou com conciliação pendente.")
            budgets = db.execute(
                "SELECT * FROM budgets WHERE project=? AND episode_id=?", (run["project"], run["episode_id"])
            ).fetchall()
            if not budgets or set(amounts) != {b["id"] for b in budgets}:
                raise UsageError("Informe uma reserva para cada orçamento do episódio, inclusive zero.")
            for budget in budgets:
                previous = db.execute(
                    "SELECT * FROM reservations WHERE budget_id=? AND run_id=?", (budget["id"], run_id)
                ).fetchone()
                if previous:
                    if previous["initial_value"] != amounts[budget["id"]]:
                        raise UsageError("Esta execução já possui outra reserva; não foi substituída.")
                    continue
                if db.execute(
                    """WITH RECURSIVE tree(id) AS (SELECT ? UNION ALL
                    SELECT r.id FROM runs r JOIN tree t ON r.parent_run_id=t.id)
                    SELECT 1 FROM requests WHERE run_id IN (SELECT id FROM tree) LIMIT 1""",
                    (run_id,),
                ).fetchone():
                    raise UsageError("A reserva precisa preceder o consumo da execução.")
                total = self._totals(db, budget)
                if total["unknown"]:
                    raise UsageError("Há consumo desconhecido neste orçamento; concilie antes de reservar.")
                reserved = db.execute(
                    "SELECT COALESCE(SUM(remaining_value),0) FROM reservations WHERE budget_id=?",
                    (budget["id"],),
                ).fetchone()[0]
                amount = amounts[budget["id"]]
                if total["spent"] + reserved + amount > budget["limit_value"]:
                    raise UsageError("Saldo insuficiente; nenhuma reserva foi criada.")
                db.execute(
                    "INSERT INTO reservations VALUES (?,?,?,?,'active')",
                    (
                        budget["id"],
                        run_id,
                        amount,
                        amount,
                    ),
                )

    def record(self, run_id: str, requests: Sequence[UsageRequest]) -> dict[str, int]:
        counts = {"inserted": 0, "updated": 0, "duplicates": 0}
        with self._transaction() as db:
            run = self._run(db, run_id)
            root = self._root(db, run_id)
            for request in requests:
                data = {**request.model_dump(mode="json"), "run_id": run_id}
                existing = db.execute(
                    "SELECT * FROM requests WHERE event_key=?", (request.event_key,)
                ).fetchone()
                if existing:
                    for key, value in data.items():
                        if value is not None and existing[key] is not None and existing[key] != value:
                            raise UsageError("Evento repetido com dados ou vínculo conflitantes.")
                    changed = {
                        key: value
                        for key, value in data.items()
                        if existing[key] is None and value is not None
                    }
                    if not changed:
                        counts["duplicates"] += 1
                        continue
                    UsageRequest.model_validate({**dict(existing), **changed})
                    db.execute(
                        f"UPDATE requests SET {','.join(f'{key}=?' for key in changed)} WHERE event_key=?",
                        (*changed.values(), request.event_key),
                    )
                    counts["updated"] += 1
                else:
                    db.execute(
                        f"INSERT INTO requests ({','.join(data)}) VALUES ({','.join('?' for _ in data)})",
                        tuple(data.values()),
                    )
                    counts["inserted"] += 1
                if root["status"] != "open":
                    db.execute(
                        "UPDATE runs SET status='pending_reconciliation',finished_at=NULL WHERE id=?",
                        (root["id"],),
                    )
                    db.execute(
                        "UPDATE reservations SET status='pending_reconciliation' WHERE run_id=?",
                        (root["id"],),
                    )
            self._sync(db, run)
        return counts

    def finish(self, run_id: str, *, reconciled: bool = False) -> str:
        with self._transaction() as db:
            run = self._run(db, run_id)
            if run["status"] == "closed":
                return "closed"
            incomplete = db.execute(
                """WITH RECURSIVE tree(id) AS (SELECT ? UNION ALL
                SELECT r.id FROM runs r JOIN tree t ON r.parent_run_id=t.id)
                SELECT 1 FROM requests WHERE run_id IN (SELECT id FROM tree) AND
                (input_tokens IS NULL OR output_tokens IS NULL OR cache_read_tokens IS NULL
                OR cache_write_tokens IS NULL OR cost_usd_micros IS NULL) LIMIT 1""",
                (run_id,),
            ).fetchone()
            children_open = db.execute(
                "SELECT 1 FROM runs WHERE parent_run_id=? AND status!='closed' LIMIT 1", (run_id,)
            ).fetchone()
            status = (
                "closed" if reconciled and not incomplete and not children_open else "pending_reconciliation"
            )
            db.execute(
                "UPDATE runs SET status=?,finished_at=? WHERE id=?",
                (
                    status,
                    datetime.now(UTC).isoformat() if status == "closed" else None,
                    run_id,
                ),
            )
            db.execute("UPDATE reservations SET status=? WHERE run_id=?", (status, run_id))
            if status == "closed":
                db.execute("UPDATE reservations SET remaining_value=0 WHERE run_id=?", (run_id,))
            self._sync(db, run)
        return status

    def report(self, project: str, episode_id: str) -> dict[str, Any]:
        with self._connection() as db:
            db.execute("BEGIN")
            scope = (project, episode_id)
            runs = [
                dict(row)
                for row in db.execute(
                    "SELECT * FROM runs WHERE project=? AND episode_id=? ORDER BY started_at,id", scope
                )
            ]
            models = [
                dict(row)
                for row in db.execute(
                    """SELECT r.stage, q.model, COUNT(*) AS requests,
                SUM(q.input_tokens) AS input_tokens, SUM(q.output_tokens) AS output_tokens,
                SUM(q.cache_read_tokens) AS cache_read_tokens,
                SUM(q.cache_write_tokens) AS cache_write_tokens,
                SUM(q.cost_usd_micros) AS cost_usd_micros,
                SUM(q.input_tokens IS NULL OR q.output_tokens IS NULL OR q.cache_read_tokens IS NULL
                OR q.cache_write_tokens IS NULL OR q.cost_usd_micros IS NULL) AS incomplete_requests
                FROM requests q JOIN runs r ON r.id=q.run_id
                WHERE r.project=? AND r.episode_id=?
                GROUP BY r.stage,q.model ORDER BY r.stage,q.model""",
                    scope,
                )
            ]
            budgets = []
            for row in db.execute(
                "SELECT * FROM budgets WHERE project=? AND episode_id=? ORDER BY id", scope
            ):
                budget = dict(row)
                reserved = db.execute(
                    "SELECT COALESCE(SUM(remaining_value),0) FROM reservations WHERE budget_id=?",
                    (row["id"],),
                ).fetchone()[0]
                budget.update(
                    reserved_value=reserved,
                    available_value=row["limit_value"] - row["spent_value"] - reserved,
                    unknown_requests=self._totals(db, row)["unknown"],
                )
                budgets.append(budget)
            return {
                "project": project,
                "episode_id": episode_id,
                "runs": runs,
                "models": models,
                "budgets": budgets,
            }
