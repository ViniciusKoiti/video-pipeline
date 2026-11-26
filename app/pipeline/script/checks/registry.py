"""A ordem das regras de episódio do `vp check` (ADR 064). Regra nova: um módulo em `checks/` com
`check(episode, report)` e uma linha nesta tupla; regra que olha uma cena ou um plano vai em `scenes.py`.

A ordem decide a ordem das linhas em cada nível do relatório (verificado, alerta, atenção, erro): as regras de
forma seguem objetivo → funil → opinião → frase sem claim → especulação → lacuna → relógio → glossário →
emoção, como no `script_form.py` que esta tupla substituiu.
"""

from __future__ import annotations

from collections.abc import Callable

from app.pipeline.models.check_report import CheckReport
from app.pipeline.script.checks import (
    citations,
    claimless,
    emotion_marks,
    facts,
    funnel,
    glossary,
    metrics_windows,
    molde_form,
    music_plan,
    narration_gaps,
    numbers_block,
    objective,
    opinion_labels,
    radar_form,
    retention_clock,
    scenes,
    speculation,
    variety,
)
from app.pipeline.script.models.checked_episode import CheckedEpisode

EpisodeRule = Callable[[CheckedEpisode, CheckReport], None]

EPISODE_RULES: tuple[EpisodeRule, ...] = (
    facts.check,
    scenes.check,
    variety.check,
    citations.check,
    objective.check,
    funnel.check,
    opinion_labels.check,
    claimless.check,
    speculation.check,
    narration_gaps.check,
    retention_clock.check,
    glossary.check,
    emotion_marks.check,
    radar_form.check,
    numbers_block.check,
    molde_form.check,
    music_plan.check,
    metrics_windows.check,
)
