"""Especulação declarada por cena (ADR 065, série "E se…?").

A cena `especulacao` é o que teria acontecido na linha alternativa: não pede `claims` (o erro do dado na
tela sem `claims` nem `estimate: true` mora no `ScenesManifest`). Aqui ficam os avisos de forma: a cena sem
marca de especulação na fala (alerta), a abertura que não avisa que a linha vai mudar antes da primeira cena
`especulacao` (alerta), o `estimate` numa cena `real` (alerta) e o ano de quatro dígitos na fala da
especulação, sinal de crônica (atenção para o gate 2).
"""

from __future__ import annotations

import re
import unicodedata

from app.media.narration import strip_pauses
from app.pipeline.constants.speculation_constants import SpeculationConstants as Constants
from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models.check_report import CheckReport
from app.pipeline.models.scene import Scene
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode


def _plain(text: str) -> str:
    """A fala sem marcas, em minúsculas e sem acento."""
    folded = unicodedata.normalize("NFD", strip_pauses(text).casefold())
    return "".join(char for char in folded if not unicodedata.combining(char))


def _says_any(text: str, phrases: tuple[str, ...]) -> bool:
    plain = _plain(text)
    return any(re.search(rf"\b{re.escape(phrase)}\b", plain) for phrase in phrases)


def _speculative(scenes: ScenesManifest) -> list[Scene]:
    return [scene for scene in scenes.scenes if scene.mode == "especulacao"]


def speculation_warnings(scenes: ScenesManifest) -> list[str]:
    """Cena `especulacao` sem marca na fala, abertura sem aviso e `estimate` fora da especulação."""
    marks = ", ".join(f'"{mark}"' for mark in Constants.MARKS[:7])
    warnings = [
        f"{scene.id}: cena especulacao sem marca de especulação na fala ({marks}…); sem ela a linha "
        "alternativa soa como crônica (ADR 065)"
        for scene in _speculative(scenes)
        if not _says_any(scene.narration, Constants.MARKS)
    ]
    first = next((i for i, scene in enumerate(scenes.scenes) if scene.mode == "especulacao"), None)
    before = scenes.scenes[:first] if first is not None else []
    if first is not None and not any(_says_any(s.narration, Constants.OPENING_MARKS) for s in before):
        opening = ", ".join(f'"{mark}"' for mark in Constants.OPENING_MARKS)
        warnings.append(
            f"{scenes.scenes[first].id}: primeira cena especulacao antes de a abertura avisar que a linha "
            f"vai mudar ({opening}): diga o que é real, o que é chute e como a tela mostra a diferença "
            "(ADR 065)"
        )
    warnings += [
        f"{scene.id}: plano {shot.kind} com estimate: true numa cena real; estimativa só na cena "
        "especulacao (ADR 065)"
        for scene in scenes.scenes
        if scene.mode == "real"
        for shot in scene.shots
        if isinstance(shot, _FactualShot) and shot.estimate
    ]
    return warnings


def speculation_attention(scenes: ScenesManifest) -> list[str]:
    """Uma linha por cena `especulacao` que diz um ano: a data no futuro alternativo é sinal de crônica."""
    lines: list[str] = []
    for scene in _speculative(scenes):
        years = Constants._YEAR.findall(strip_pauses(scene.narration))
        if years:
            lines.append(
                f"especulação: {scene.id}: ano na fala ({', '.join(dict.fromkeys(years))}); data no futuro "
                "alternativo narra a linha inventada como crônica (ADR 065)"
            )
    return lines


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is not None:
        report.warnings += speculation_warnings(episode.scenes)
        report.attention += speculation_attention(episode.scenes)
