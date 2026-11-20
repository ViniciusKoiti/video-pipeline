"""Relógio de retenção do vídeo longo (ADR 061).

As curvas do canal mostram cerca de 60% saindo até os 2 min, e quem fica fica uns 3 min. Por isso a promessa
fecha até 0:30, um gancho de retomada (`rehook`) ou a virada para a parte prática (`turn`) entra entre 2:00 e
3:00, e depois de uma pausa para aviso (`pause`: CVV, saúde) vem logo um gancho ou a virada. O roteirista
marca o papel da cena em `beat`; aqui só se confere o relógio. O tempo vem da voz real quando todas as cenas
já têm WAV, ou da quantidade de texto antes disso. São pontos de atenção para o gate 2, não erro: a regra é um
teste do dono (2026-11-16).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.constants.retention_clock_constants import RetentionClockConstants as Constants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import Scene, ScenesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.voice.timeline import measured_seconds

Timed = tuple[Scene, float, float]  # a cena, onde começa e onde termina, em segundos


def mmss(seconds: float) -> str:
    whole = round(seconds)
    return f"{whole // 60}:{whole % 60:02d}"


def scene_clock(
    scenes: ScenesManifest, chars_per_second: float, measured: Mapping[str, float] | None = None
) -> tuple[list[Timed], str]:
    """Início e fim de cada cena, e de onde veio o tempo ("voz real" ou "estimado")."""
    timed: list[Timed] = []
    start = 0.0
    for scene in scenes.scenes:
        length = measured[scene.id] if measured else timeline_length(scene.narration) / chars_per_second
        timed.append((scene, start, start + length))
        start += length
    return timed, "voz real" if measured else "estimado"


def _is_long(timed: list[Timed]) -> bool:
    return bool(timed) and timed[-1][2] >= Constants.LONG_VIDEO_SECONDS


def retention_attention(timed: list[Timed], source: str) -> list[str]:
    if not _is_long(timed):
        return []
    if not any(scene.beat for scene, _, _ in timed):
        return [
            "relógio: roteiro longo sem `beat`; marque a cena que fecha a promessa (promise), o gancho de "
            "retomada (rehook) ou a virada (turn) e as pausas de aviso (pause) (ADR 061)"
        ]
    return _promise(timed, source) + _rehook(timed, source) + _after_pauses(timed, source)


def _promise(timed: list[Timed], source: str) -> list[str]:
    promise = next(((scene, end) for scene, _, end in timed if scene.beat == "promise"), None)
    if promise is None:
        return ["relógio: nenhuma cena marcada como `promise` (a que fecha a promessa)"]
    scene, end = promise
    if end > Constants.PROMISE_BY_SECONDS:
        limit = mmss(Constants.PROMISE_BY_SECONDS)
        return [f"relógio ({source}): a promessa fecha em ~{mmss(end)} ({scene.id}); o alvo é até {limit}"]
    return []


def _rehook(timed: list[Timed], source: str) -> list[str]:
    low, high = Constants.REHOOK_FROM_SECONDS, Constants.REHOOK_BY_SECONDS
    marked = [(scene, start, end) for scene, start, end in timed if scene.beat in Constants.REHOOK_BEATS]
    if any(start <= high and end >= low for _, start, end in marked):
        return []
    later = next((f"; o próximo é {s.id}, em ~{mmss(start)}" for s, start, _ in marked if start > high), "")
    return [
        f"relógio ({source}): nenhum gancho de retomada (rehook) nem virada (turn) entre {mmss(low)} e "
        f"{mmss(high)}{later}; é onde a audiência cai ({Constants.RESEARCH})"
    ]


def _after_pauses(timed: list[Timed], source: str) -> list[str]:
    lines = []
    for (scene, _, end), following in zip(timed, timed[1:], strict=False):
        after = following[0]
        if scene.beat != "pause" or after.beat == "pause":  # o aviso pode seguir na cena seguinte
            continue
        if after.beat not in Constants.REHOOK_BEATS:
            lines.append(
                f"relógio ({source}): depois da pausa em {scene.id} (~{mmss(end)}), {after.id} não é "
                "gancho de retomada (rehook) nem virada (turn)"
            )
    return lines


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", strip_pauses(text).lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def pause_hints(timed: list[Timed]) -> list[str]:
    """Cena de aviso (CVV, saúde) sem a marca de pausa, no vídeo longo."""
    if not _is_long(timed):
        return []
    return [
        f"{scene.id}: fala de aviso (CVV) sem `beat: pause`; marque para o relógio conferir o gancho depois"
        for scene, _, _ in timed
        if scene.beat != "pause" and any(re.search(p, _plain(scene.narration)) for p in Constants.PAUSE_HINTS)
    ]


def retention_summary(timed: list[Timed], source: str) -> str | None:
    if not _is_long(timed):
        return None
    marks = [f"{scene.id} {scene.beat} {mmss(start)}" for scene, start, _ in timed if scene.beat]
    return f"relógio ({source}): {mmss(timed[-1][2])}; " + (", ".join(marks) if marks else "sem marcas")


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    """Com `episode.measure` e a voz de todas as cenas pronta, o relógio usa a voz real (ADR 061)."""
    if episode.scenes is None:
        return
    ids = [scene.id for scene in episode.scenes.scenes]
    measure = episode.measure
    measured = measured_seconds(episode.store, episode.episode_id, ids, measure) if measure else None
    timed, source = scene_clock(episode.scenes, episode.chars_per_second, measured)
    if (summary := retention_summary(timed, source)) is not None:
        report.checked.append(summary)
    report.warnings += pause_hints(timed)
    report.attention += retention_attention(timed, source)
