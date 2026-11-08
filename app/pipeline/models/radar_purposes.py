from __future__ import annotations

from app.pipeline.models._radar_radar import _Radar
from app.pipeline.models.radar_guidance import RadarGuidance


class RadarPurposes(_Radar):
    """Que tipo de vídeo (notícia, explicação, opinião) anda mais no nicho, quando o radar fez essa leitura.
    Vem das palavras soltas das legendas, com o léxico do idioma de cada Reel: é palpite de vocabulário."""

    reader: str
    read: int  # quantos Reels tiveram a legenda lida
    main_purposes: dict[str, int] = {}  # tipo principal (ou "none") -> Reels
    guidance: list[RadarGuidance] = []  # `purpose_news`, `purpose_explain`, `purpose_opinion`
    no_basis: list[str] = []
