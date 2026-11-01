"""Constantes de metrics; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final

from app.pipeline.constants.schemas_constants import SchemasConstants


class MetricsConstants:
    EPISODES_DIR: Final[str] = "episodes"
    PUBLICATIONS_DIR: Final[str] = "publicacoes"
    REGISTRY_FILE: Final[str] = "registro.jsonl"
    METRICS_DIR: Final[str] = "metricas"
    TABLE_FILE: Final[str] = "metricas.csv"
    CSV_COLUMNS: Final = (
        "id",
        "platform",
        "channel",
        "format",
        "series",
        "published_at",
        "duration_s",
        "hypothesis",
        "window",
        "due",
        "read_at",
        *SchemasConstants.READING_NUMBERS,
        "traffic_sources",
        "requests",
        "notes",
        "url",
        "post_id",
    )
