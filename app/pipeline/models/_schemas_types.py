from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import AfterValidator, Field

if TYPE_CHECKING:
    from collections.abc import Sequence

    from app.pipeline.models._schemas_step import _Step


EpisodeId = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]


SourceId = Annotated[str, Field(pattern=r"^source-\d{2,}$")]


ExcerptId = Annotated[str, Field(pattern=r"^source-\d{2,}#E\d+$")]  # trecho numerado (§13.1)


SceneId = Annotated[str, Field(pattern=r"^S\d{2,}$")]


AssetId = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_.-]*$")]


Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


HttpUrl = Annotated[str, Field(pattern=r"^https?://\S+$")]  # string simples: sem normalização no ida-e-volta


NonEmpty = Annotated[str, Field(min_length=1)]


def _relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if "\\" in value or path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("caminho deve ser relativo à pasta do episódio, sem '..'")
    return value


RelPath = Annotated[str, AfterValidator(_relative_path)]


def _unique(ids: Sequence[str], what: str) -> None:
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"{what} duplicados: {', '.join(duplicates)}")


Language = Literal["en", "pt-BR"]


Motion = Literal["push_in", "pull_out", "pan_left", "pan_right", "pan_up", "pan_down", "still"]


_WHEN_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


_YEAR_RE = re.compile(r"(?<!\d)\d{4}(?!\d)")


_SCREEN_NUMBER_RE = re.compile(r"^(\D*?)([\d.,]*\d)(.*)$")


def screen_parts(value: str) -> tuple[str, str, str] | None:
    """(prefixo, dígitos, sufixo) como escritos, sem ler o número: a leitura depende do idioma."""
    match = _SCREEN_NUMBER_RE.match(value.strip())
    if match is None:
        return None
    return match.group(1).strip(), match.group(2), match.group(3).strip()


RegionCode = Annotated[str, Field(pattern=r"^([A-Z]{3}|[A-Z]{2}-[A-Z0-9]{1,3})$")]


NodeId = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]


KEYWORD_MAX_WORDS = 8


def _fold(text: str) -> str:
    """Comparação de texto na tela com a narração: sem diferença de maiúscula nem de espaços."""
    return " ".join(text.casefold().split())


Operator = Literal["+", "−", "×", "÷"]


def _later_steps_anchored(steps: list[_Step], what: str) -> None:
    missing = [i + 1 for i, step in enumerate(steps) if i > 0 and step.anchor is None]
    if missing:
        raise ValueError(f"{what} {', '.join(map(str, missing))} sem anchor: entra quando a narração o diz")


HOOK_MAX_WORDS = 14  # cabe em 3 linhas do HookCard no vertical


MEDIA_SHOT_KINDS = frozenset({"photo", "broll"})  # visual vem de um ativo


REELS_SHOT_KINDS = frozenset({"calculation", "receipt", "hook", "end_card"})


Orientation = Literal["landscape", "portrait"]  # 16:9 ou 9:16 (ADR 014)


PORTRAIT_SHOT_KINDS = frozenset(
    {"photo", "broll", "number", "keyword", "stamp", "lower_third", "compare", "chart"}
) | REELS_SHOT_KINDS


def reels_shot_problems(scenes: Sequence[tuple[str, Sequence[str]]], *, portrait: bool) -> list[str]:
    """Onde ficam os planos dos Reels (ADR 028): só no vertical; o gancho só no primeiro plano do vídeo e o
    cartão final só no último, um de cada. `scenes`: (id da cena, tipos dos planos), em ordem."""
    problems: list[str] = []
    flat = [(scene_id, kind) for scene_id, kinds in scenes for kind in kinds]
    for scene_id, kind in flat:
        if kind in REELS_SHOT_KINDS and not portrait:
            problems.append(f"{scene_id}: plano {kind} só no vertical por enquanto (ADR 028)")
    for kind, where, expected in (("hook", "primeiro", 0), ("end_card", "último", len(flat) - 1)):
        misplaced = [i for i, (_, k) in enumerate(flat) if k == kind and i != expected]
        if misplaced:
            problems.append(f"{flat[misplaced[0]][0]}: {kind} só no {where} plano do vídeo (ADR 028)")
    return problems


def portrait_problems(scene_id: str, kinds: list[str]) -> list[str]:
    """Planos de uma cena que não cabem no perfil vertical (ADR 014), um erro por plano."""
    allowed = ", ".join(sorted(PORTRAIT_SHOT_KINDS))
    return [
        f"{scene_id}: plano {kind} não cabe em retrato (9:16); use {allowed}"
        for kind in kinds
        if kind not in PORTRAIT_SHOT_KINDS
    ]


HostCorner = Literal["top-left", "top-right", "bottom-left", "bottom-right"]


HostVariant = Annotated[str, Field(pattern=r"^(variant\d{2}|hat)$")]  # nome de peça do Notionists (CC0)


Delivery = Literal["hook", "turn", "invite", "neutral", "calm"]


_STEP_NAMES = {"network": "passo", "calculation": "termo", "receipt": "linha"}


ObjectiveKind = Literal["noticiar", "explicar", "opinar"]


_OBJECTIVE_FIELDS: dict[str, tuple[str, ...]] = {
    "noticiar": ("event_date",),
    "explicar": ("question",),
    "opinar": ("thesis", "thesis_by"),
}


FunnelStage = Literal["topo", "meio", "fundo"]


FactId = Annotated[str, Field(pattern=r"^F\d{2,}$")]


PUBLIC_DOMAIN_LICENSES = frozenset({"PD-US", "PD-old"})


ATTRIBUTION_LICENSES = frozenset({"CC-BY-2.0", "CC-BY-2.5", "CC-BY-3.0", "CC-BY-3.0-BR", "CC-BY-4.0"})


CITATION_LICENSE = "Citacao"


AUDIO_LIBRARY_LICENSE = "YouTube-Audio-Library"


MusicRole = Literal["bed", "sting", "silence"]  # fundo, transição curta, silêncio proposital


MusicLevel = Literal["low", "mid"]


MAX_MUSIC_GAIN_DB = -10.0


Window = Literal["d7", "d28"]


WINDOW_DAYS: dict[Window, int] = {"d7": 7, "d28": 28}


READING_NUMBERS = (
    "views", "likes", "shares", "comments", "saves", "impressions", "ctr_percent",
    "avg_view_duration_s", "retention_30s_percent", "subscribers_gained",
)


Platform = Literal["youtube", "instagram", "tiktok"]


PublicationFormat = Literal["longo", "reel", "clipe", "story"]


RequestKind = Literal["planilha", "modelo", "duvida", "outro"]


Count = Annotated[int, Field(ge=0)]


Percent = Annotated[float, Field(ge=0, le=100)]


Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
