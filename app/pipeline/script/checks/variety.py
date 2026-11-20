"""Variedade dos planos (ADR 011, decisão 9): cartões sem imagem, carimbos, tipos repetidos. A revisão humana
decide."""

from __future__ import annotations

from app.pipeline.constants.check_constants import CheckConstants as Constants
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import ChartShot, Scene, effective_shots
from app.pipeline.script.models.checked_episode import CheckedEpisode


def variety_warnings(scenes: list[Scene]) -> list[str]:
    """Cartões demais sem imagem, carimbos demais, tarja sem imagem, o mesmo tipo em sequência, gráfico de
    barras que devia ser comparação, frase na tela repetida (ADR 011, decisão 9)."""
    warnings: list[str] = []
    run: list[str] = []  # cenas do trecho atual de planos gráficos sem mídia
    total = stamps = 0
    previous: tuple[str, str] | None = None  # (cena, tipo) do plano gráfico anterior

    def close_run() -> None:
        if len(run) > Constants.MAX_GRAPHIC_RUN:
            where = run[0] if run[0] == run[-1] else f"{run[0]}–{run[-1]}"
            warnings.append(f"{where}: {len(run)} planos gráficos seguidos sem foto nem B-roll")
        run.clear()

    for scene in scenes:
        media_before = False
        keywords = 0
        for shot in effective_shots(scene):
            total += 1
            stamps += shot.kind == "stamp"
            keywords += shot.kind == "keyword"
            if shot.kind in SchemasConstants.MEDIA_SHOT_KINDS:
                media_before = True
                previous = None
                close_run()
                continue
            if shot.kind == "lower_third" and not media_before:
                warnings.append(f"{scene.id}: tarja ({shot.anchor!r}) sem foto nem B-roll por baixo")
            bar = shot if isinstance(shot, ChartShot) and shot.type in ("bar", "bar_horizontal") else None
            if bar is not None and len(bar.points) == 2:
                warnings.append(f"{scene.id}: gráfico de barras com 2 pontos ({shot.anchor!r}); use compare")
            if previous is not None and previous[1] == shot.kind:
                where = scene.id if previous[0] == scene.id else f"{previous[0]}–{scene.id}"
                warnings.append(f"{where}: {shot.kind} duas vezes seguidas")
            previous = (scene.id, shot.kind)
            if shot.kind in SchemasConstants.OVERLAY_SHOT_KINDS and media_before:
                close_run()  # desenhado sobre a mídia da cena: ainda há imagem na tela
            else:
                run.append(scene.id)
        if keywords > 1:
            warnings.append(f"{scene.id}: {keywords} frases na tela na mesma cena; use uma")
        media_before = False
    close_run()
    if total >= Constants.MIN_SHOTS_FOR_SHARE and stamps / total > Constants.MAX_STAMP_SHARE:
        warnings.append(
            f"carimbos em {stamps} de {total} planos ({stamps / total:.0%}); o limite é "
            f"{Constants.MAX_STAMP_SHARE:.0%}"
        )
    return warnings


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is not None:
        report.warnings += variety_warnings(episode.scenes.scenes)
