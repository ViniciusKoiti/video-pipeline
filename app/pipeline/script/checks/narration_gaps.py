"""Lacuna dita na fala (decisão do dono, 2026-11-14): "eu não encontrei", "não achei", "não sei" na
narração soam como pesquisa incompleta e deixam a resposta no vazio. O que as fichas não respondem sai da
fala ou vira "eu acho X, porque Y" (skill `roteiro-explicativo`). Aqui só se avisa: a troca é do
roteirista."""

from __future__ import annotations

import re
import unicodedata

from app.media.narration import strip_pauses
from app.pipeline.constants.narration_gaps_constants import NarrationGapsConstants as Constants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode


def _plain(text: str) -> str:
    """Minúsculas e sem acento, letra por letra, para o trecho achado sair do texto original."""
    return "".join(unicodedata.normalize("NFD", char)[0] for char in text).lower()


def gap_warnings(scenes: ScenesManifest) -> list[str]:
    warnings: list[str] = []
    for scene in scenes.scenes:
        text = strip_pauses(scene.narration)
        plain = _plain(text)
        found = next((m for p in Constants.PHRASES if (m := re.search(p, plain))), None)
        if found:
            said = text[found.start() : found.end()]
            warnings.append(
                f"{scene.id}: a fala diz que não achou ({said!r}); troque por \"eu acho X, porque Y\" "
                "ou corte (skill roteiro-explicativo)"
            )
    return warnings


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is not None:
        report.warnings += gap_warnings(episode.scenes)
