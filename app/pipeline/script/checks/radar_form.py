"""Forma do roteiro contra o resumo do reels-radar, se o episódio tiver um (ADR 018). Só alertas: o resumo é
observação de amostra pequena e nunca fonte de fato."""

from __future__ import annotations

from app.pipeline.constants.radar_constants import RadarConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.radar import RadarBrief, brief_summary, form_warnings, unmeasured_patterns
from app.pipeline.script.reading import read_optional


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    brief = read_optional(episode.store, episode.episode_id, RadarConstants.BRIEF_FILE, RadarBrief, report)
    if brief is None:
        return
    caption_path = episode.store.path(episode.episode_id, RadarConstants.CAPTION_FILE)
    caption = caption_path.read_text(encoding="utf-8") if caption_path.is_file() else None
    line = brief_summary(brief)
    unmeasured = unmeasured_patterns(episode.scenes, brief, episode.chars_per_second, caption)
    if unmeasured:
        line += f"; sem conferência no texto: {', '.join(unmeasured)}"
    report.checked.append(line)
    report.warnings += form_warnings(episode.scenes, brief, episode.chars_per_second, caption, episode.today)
