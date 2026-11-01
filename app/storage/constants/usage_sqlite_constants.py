"""Constantes de usage_sqlite; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class UsageSqliteConstants:
    SCHEMA: Final = (
        (
            "CREATE TABLE runs (\n        id TEXT PRIMARY KEY, project TEXT NOT NULL, "
            "episode_id TEXT NOT NULL,\n        stage TEXT NOT NULL, agent_name TEXT NOT "
            "NULL, session_id TEXT,\n        parent_run_id TEXT REFERENCES runs(id),\n    "
            "    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN "
            "('open','pending_reconciliation','closed')),\n        started_at TEXT NOT "
            "NULL, finished_at TEXT\n    ) STRICT"
        ),
        (
            "CREATE TABLE requests (\n        event_key TEXT PRIMARY KEY, "
            "provider_request_id TEXT UNIQUE,\n        run_id TEXT NOT NULL REFERENCES "
            "runs(id), model TEXT NOT NULL, occurred_at TEXT NOT NULL,\n        "
            "input_tokens INTEGER CHECK(input_tokens >= 0), output_tokens INTEGER "
            "CHECK(output_tokens >= 0),\n        cache_read_tokens INTEGER "
            "CHECK(cache_read_tokens >= 0),\n        cache_write_tokens INTEGER "
            "CHECK(cache_write_tokens >= 0),\n        cost_usd_micros INTEGER "
            "CHECK(cost_usd_micros >= 0), duration_ms INTEGER CHECK(duration_ms >= 0),\n "
            "       status TEXT NOT NULL CHECK(status IN ('success','error'))\n    ) STRICT"
        ),
        (
            "CREATE TABLE budgets (\n        id TEXT PRIMARY KEY, project TEXT NOT NULL, "
            "episode_id TEXT NOT NULL,\n        model_filter TEXT NOT NULL, metric TEXT "
            "NOT NULL CHECK(metric IN ('tokens_total','cost_usd_micros')),\n        "
            "limit_value INTEGER NOT NULL CHECK(limit_value >= 0),\n        spent_value "
            "INTEGER NOT NULL DEFAULT 0 CHECK(spent_value >= 0),\n        "
            "UNIQUE(project, episode_id, model_filter, metric)\n    ) STRICT"
        ),
        (
            "CREATE TABLE reservations (\n        budget_id TEXT NOT NULL REFERENCES "
            "budgets(id), run_id TEXT NOT NULL REFERENCES runs(id),\n        "
            "initial_value INTEGER NOT NULL CHECK(initial_value >= 0),\n        "
            "remaining_value INTEGER NOT NULL CHECK(remaining_value >= 0),\n        "
            "status TEXT NOT NULL DEFAULT 'active' CHECK(status IN "
            "('active','pending_reconciliation','closed')),\n        PRIMARY "
            "KEY(budget_id, run_id)\n    ) STRICT"
        ),
        "CREATE INDEX requests_run ON requests(run_id)",
        "CREATE INDEX runs_scope ON runs(project, episode_id)",
        "CREATE INDEX runs_parent ON runs(parent_run_id)",
    )
