from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_types import AssetId, NonEmpty
from app.pipeline.models.model import Model


class MusicTrack(Model):
    """Faixa do catálogo. Os direitos ficam no ativo `data/music/<asset_id>.json`, como qualquer ativo (§6); o
    episódio que a usa ganha uma cópia do ativo e do arquivo em `assets/`, aprovada no gate 3."""

    asset_id: AssetId
    title: NonEmpty
    artist: str | None = None
    file: NonEmpty  # nome do arquivo em data/music/
    duration_ms: int = Field(gt=0)
    moods: list[NonEmpty] = Field(min_length=1)  # clima, da fonte e da escuta do dono
    intensity: int = Field(ge=1, le=5)  # medida localmente pela loudness da faixa
    bpm: int | None = Field(default=None, gt=0)  # anotado à mão quando importa
    vocals: bool  # voz cantada: nunca sob a narração
    loops: bool = False  # o fim emenda no começo sem corte audível
