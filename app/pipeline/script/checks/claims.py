"""Afirmações de uma cena (`claims`, ADR 008): cada uma aponta trechos que existem e que estão numa ficha."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import Scene
from app.pipeline.script.models.checked_episode import CheckedEpisode


def check(scene: Scene, episode: CheckedEpisode, report: CheckReport) -> None:
    facts, sources = episode.facts, episode.sources
    fact_excerpts = {e.excerpt_id for f in facts.facts for e in f.evidence} if facts else set()
    claims = scene.claims + [c for shot in scene.shots for c in shot.claims]
    for claim in claims:
        if facts is not None and not claim.excerpt_ids:
            report.errors.append(f"{scene.id}: afirmação sem trecho: {claim.text!r}")
        for excerpt_id in claim.excerpt_ids:
            if sources is not None and excerpt_id not in episode.excerpts:
                report.errors.append(f"{scene.id}: trecho {excerpt_id} não existe")
            elif facts is not None and excerpt_id not in fact_excerpts:
                report.errors.append(f"{scene.id}: trecho {excerpt_id} não está em nenhuma ficha")
