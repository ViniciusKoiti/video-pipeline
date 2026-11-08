from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.pipeline.constants.radar_constants import RadarConstants
from app.pipeline.models._radar_radar import _Radar
from app.pipeline.models.radar_guidance import RadarGuidance
from app.pipeline.models.radar_purposes import RadarPurposes


class RadarBrief(_Radar):
    schema_name: Literal["script_brief.v1"] = Field(alias="schema")
    niche: str
    generated_at: datetime
    analysed: int  # quantos Reels foram lidos
    measure: str | None = None  # taxa de todos os números (shares/views, likes/views); resumo antigo não tem
    guidance: list[RadarGuidance] = []
    themes: list[RadarGuidance] = []  # palavras soltas das legendas: pergunta para a pesquisa, nunca fato
    thresholds: dict[str, float | None] = {}  # None: o nicho não deu base para esse corte
    caveats: list[str] = []
    purposes: RadarPurposes | None = None  # resumos antigos não têm

    def patterns(self) -> list[RadarGuidance]:
        """Os padrões de forma e, quando o radar leu os tipos, os de tipo de vídeo."""
        about_kind = self.purposes.guidance if self.purposes else []
        return [g for g in [*self.guidance, *about_kind] if g.strength == "pattern"]

    def hints(self) -> list[RadarGuidance]:
        return [g for g in self.guidance if g.strength == "hint"]

    def threshold(self, key: str) -> float | None:
        """O corte de um `long_*` neste nicho, ou None quando o resumo não tem base para ele."""
        return self.thresholds.get(key)

    def measure_label(self) -> str:
        """A medida, como o alerta a chama: nunca 'compartilhamento' quando o resumo mediu outra coisa."""
        if self.measure is None:
            return "na medida do resumo, que não está informada"
        return RadarConstants.MEASURES.get(self.measure, self.measure)
