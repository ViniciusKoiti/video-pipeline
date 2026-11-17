from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VoicePacing(BaseModel):
    """A cadência das pausas de um episódio (`voice/cadencia.json`): o silêncio, em segundos, entre o fim de
    uma frase e o começo da próxima, pelo papel da frase. Vale dentro da cena e na troca de cena."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    continuacao_s: float = Field(default=0.4, ge=0.1, le=3.0)  # a próxima começa por "E", "Mas", "Só que"...
    ponto_s: float = Field(default=0.65, ge=0.1, le=3.0)  # fim de frase comum
    conclusao_s: float = Field(default=0.9, ge=0.1, le=3.0)  # a próxima começa por "Então", "No fim"...
    pergunta_s: float = Field(default=1.0, ge=0.1, le=3.0)  # depois de uma pergunta
    virada_s: float = Field(default=1.15, ge=0.1, le=3.0)  # antes de cena com entrega `turn` ou `invite`
    final_s: float = Field(default=0.8, ge=0.1, le=3.0)  # depois da última fala do vídeo
    frase_longa_palavras: int = Field(default=25, ge=5)  # frase com isto ou mais palavras ganha um respiro
    frase_longa_extra_s: float = Field(default=0.1, ge=0.0, le=1.0)
    nota: str = ""
