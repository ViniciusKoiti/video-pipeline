"""Constantes de schemas; dados fixos sem I/O."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from app.pipeline.models.provider import Provider
from app.pipeline.models.status import Status

if TYPE_CHECKING:
    from app.pipeline.models._schemas_types import HostCorner, Language, Window


class SchemasConstants:
    _WHEN_RE: Final = re.compile("^\\d{4}(-\\d{2}(-\\d{2})?)?$")
    _YEAR_RE: Final = re.compile("(?<!\\d)\\d{4}(?!\\d)")
    _SCREEN_NUMBER_RE: Final = re.compile("^(\\D*?)([\\d.,]*\\d)(.*)$")
    KEYWORD_MAX_WORDS: Final[int] = 8
    # cabe em 3 linhas do HookCard no vertical
    HOOK_MAX_WORDS: Final[int] = 14
    # visual vem de um ativo
    MEDIA_SHOT_KINDS: Final = frozenset(("photo", "broll"))
    REELS_SHOT_KINDS: Final = frozenset(("calculation", "receipt", "hook", "end_card"))
    _STEP_NAMES: Final = MappingProxyType({"network": "passo", "calculation": "termo", "receipt": "linha"})
    _OBJECTIVE_FIELDS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
        {"noticiar": ("event_date",), "explicar": ("question",), "opinar": ("thesis", "thesis_by")}
    )
    PUBLIC_DOMAIN_LICENSES: Final = frozenset(("PD-US", "PD-old"))
    ATTRIBUTION_LICENSES: Final = frozenset(
        ("CC-BY-2.0", "CC-BY-2.5", "CC-BY-3.0", "CC-BY-3.0-BR", "CC-BY-4.0")
    )
    CITATION_LICENSE: Final[str] = "Citacao"
    AUDIO_LIBRARY_LICENSE: Final[str] = "YouTube-Audio-Library"
    MAX_MUSIC_GAIN_DB: Final = -10.0
    WINDOW_DAYS: Final[Mapping[Window, int]] = MappingProxyType({"d7": 7, "d28": 28})
    READING_NUMBERS: Final = (
        "views",
        "likes",
        "shares",
        "comments",
        "saves",
        "impressions",
        "ctr_percent",
        "avg_view_duration_s",
        "retention_30s_percent",
        "subscribers_gained",
    )
    APPROVED_STATES: Final = frozenset((Status.APPROVED, Status.COMPLETED))
    STOCK_LICENSES: Final = MappingProxyType(
        {
            Provider.PEXELS: "Pexels",
            Provider.PIXABAY: "Pixabay",
            Provider.UNSPLASH: "Unsplash",
            Provider.COVERR: "Coverr",
        }
    )
    NUMBER_SEPARATORS: Final[Mapping[Language, tuple[str, str]]] = MappingProxyType(
        {"pt-BR": (".", ","), "en": (",", ".")}
    )
    OVERLAY_SHOT_KINDS: Final = frozenset(("lower_third", "stamp", "number", "keyword"))
    HOST_CORNERS: Final[tuple[HostCorner, ...]] = ("top-left", "top-right", "bottom-right", "bottom-left")
    # quadros por vídeo
    MAX_CITATION_FRAMES: Final[int] = 10
    # na tela, só enquanto a narração comenta o quadro
    MAX_CITATION_MS: Final[int] = 8000
    MUSIC_GAIN_DB: Final[Mapping[str, float]] = MappingProxyType({"low": -24.0, "mid": -18.0})
    # em data/: catálogo, faixas e o ativo de cada uma
    MUSIC_DIR: Final[str] = "music"
    # em data/music/
    MUSIC_CATALOG_FILE: Final[str] = "catalog.json"
    # na pasta do episódio
    MUSIC_PLAN_FILE: Final[str] = "music.json"
    METRICS_FILE: Final[str] = "metrics.json"
    _EXCERPT_RE: Final = re.compile("^(source-\\d{2,})#E\\d+$")
    PORTRAIT_SHOT_KINDS: Final = (
        frozenset(("photo", "broll", "number", "keyword", "stamp", "lower_third", "compare", "chart"))
        | REELS_SHOT_KINDS
    )
    ACCEPTED_LICENSES: Final = (
        PUBLIC_DOMAIN_LICENSES
        | ATTRIBUTION_LICENSES
        | frozenset(STOCK_LICENSES.values())
        | frozenset(
            ("CC0-1.0", "Flickr-NKCR", "Generated", "Original", CITATION_LICENSE, AUDIO_LIBRARY_LICENSE)
        )
    )
    GRAPHIC_SHOT_KINDS: Final = (
        frozenset(
            (
                "number",
                "chart",
                "quote",
                "map",
                "stamp",
                "lower_third",
                "timeline",
                "family_tree",
                "compare",
                "network",
                "keyword",
            )
        )
        | REELS_SHOT_KINDS
    )
    _NOT_A_RECORD: Final = frozenset((*STOCK_LICENSES, Provider.WORKERS_AI))
