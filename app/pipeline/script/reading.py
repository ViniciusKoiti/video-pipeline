"""Leitura de um arquivo opcional do episódio para o `vp check`: fora do contrato vira erro no relatório."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.ports import M, ManifestInvalid, ManifestStore


def read_optional(
    store: ManifestStore, episode_id: str, name: str, model: type[M], report: CheckReport
) -> M | None:
    """O arquivo lido, ou nada quando ele não existe ou não passa no schema (o erro fica no relatório)."""
    if not store.exists(episode_id, name):
        return None
    try:
        return store.read(episode_id, name, model)
    except ManifestInvalid as error:
        report.errors.append(f"{name}: {error.details}")
        return None
