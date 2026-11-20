"""Citações (`Citacao`) no bloco do `vp numeros`: quadros parados e clipes (ADR 007, emenda de 2026-11-03)."""

from __future__ import annotations

from collections.abc import Sequence

from app.pipeline.models.citation import Citation
from app.pipeline.models.shot_timing import ShotTiming
from app.pipeline.schemas import Asset


def _seconds(ms: float) -> str:
    return f"~{ms / 1000:.1f} s".replace(".", ",")


def citation_of(timing: ShotTiming, asset: Asset) -> Citation:
    """Uma citação (quadro ou clipe) do roteiro, com a obra, o timecode e a origem do ativo."""
    return Citation(
        timing.scene_id,
        timing.shot.anchor,
        asset.id,
        timing.ms,
        clip=asset.media == "clip",
        work=asset.work or "",
        timecode=asset.timecode or "",
        origin=asset.origin or "",
    )


def citation_lines(citations: Sequence[Citation]) -> list[str]:
    """Quadros parados e clipes `Citacao`: o que o dono confere no gate 3 e no 4 (emenda de 2026-11-03)."""
    clips = [c for c in citations if c.clip]
    distinct = len({c.asset_id for c in citations})
    lines = [
        "",
        f"### Citações (`Citacao`): {len(citations) - len(clips)} quadros e {len(clips)} clipes, "
        f"{len(citations)} usos de {distinct} ativos",
        "",
    ]
    if citations:
        lines += [
            "| # | Tipo | Cena | Âncora | Ativo | Obra | Timecode | Origem | Tempo |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        lines += [
            f'| {i} | {"clipe" if c.clip else "quadro"} | {c.scene_id} | "{c.anchor}" | `{c.asset_id}` | '
            f"{c.work or '-'} | {c.timecode or '-'} | {c.origin or '-'} | {_seconds(c.ms)} |"
            for i, c in enumerate(citations, 1)
        ]
        if clips:
            lines += [
                "",
                f"Clipes: {_seconds(sum(c.ms for c in clips))} de tela no total. Sem teto numérico; "
                "o clipe sai mudo e só fica enquanto a narração comenta o trecho.",
            ]
    return lines
