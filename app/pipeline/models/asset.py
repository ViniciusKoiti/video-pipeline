from __future__ import annotations

from typing import Self

from pydantic import AwareDatetime, model_validator

from app.pipeline.models._schemas_types import (
    ATTRIBUTION_LICENSES,
    AUDIO_LIBRARY_LICENSE,
    CITATION_LICENSE,
    PUBLIC_DOMAIN_LICENSES,
    AssetId,
    HttpUrl,
    NonEmpty,
    SceneId,
    Sha256,
)
from app.pipeline.models._schemas_value_accepted_licenses import ACCEPTED_LICENSES
from app.pipeline.models._schemas_value_approved_states import APPROVED_STATES
from app.pipeline.models._schemas_value_stock_licenses import STOCK_LICENSES
from app.pipeline.models.generation import Generation
from app.pipeline.models.model import Model
from app.pipeline.models.provider import Provider
from app.pipeline.models.status import Status


class Asset(Model):
    id: AssetId
    provider: Provider
    provider_id: NonEmpty
    original_url: HttpUrl | None = None
    page_url: HttpUrl | None = None
    author: str | None = None
    license_id: str | None = None  # None = licença não identificada
    license_url: HttpUrl | None = None
    attribution_text: str = ""
    usage_notes: str = ""
    retrieved_at: AwareDatetime
    sha256: Sha256 | None = None  # preenchido ao baixar o arquivo final
    review_status: Status = Status.PENDING
    used_in_scenes: list[SceneId] = []  # plural: um mapa pode voltar em várias cenas (§9)
    generation: Generation | None = None  # obrigatório para imagem gerada
    work: str | None = None  # obra citada: título, estúdio e detentor conhecido (licença Citacao)

    @property
    def is_synthetic(self) -> bool:
        return self.generation is not None

    @model_validator(mode="after")
    def _generation_consistency(self) -> Self:
        generated = self.provider is Provider.WORKERS_AI
        if generated != (self.generation is not None):
            raise ValueError("imagem gerada exige 'generation', e só ela pode tê-lo")
        if generated and self.license_id not in (None, "Generated"):
            raise ValueError("imagem gerada usa license_id 'Generated'")
        return self

    @model_validator(mode="after")
    def _approval_requires_rights(self) -> Self:
        """§2.3: nenhum ativo sem licença registrada entra no render."""
        if self.review_status not in APPROVED_STATES:
            return self
        problems = []
        if self.license_id not in ACCEPTED_LICENSES:
            problems.append(f"licença {self.license_id!r} fora da lista aceita")
        if self.sha256 is None:
            problems.append("sha256 ausente (arquivo final não baixado)")
        if self.license_id in PUBLIC_DOMAIN_LICENSES and not self.usage_notes.strip():
            problems.append("domínio público exige o raciocínio em usage_notes (§8)")
        if self.license_id in ATTRIBUTION_LICENSES and not (self.author and self.attribution_text.strip()):
            problems.append("CC-BY exige author e attribution_text")
        if self.provider not in (Provider.WORKERS_AI, Provider.ORIGINAL) and not self.page_url:
            problems.append("ativo de acervo exige page_url")
        if (self.license_id == CITATION_LICENSE) != (self.provider is Provider.OFFICIAL):
            problems.append("citação só de material oficial público do detentor (provider official)")
        if self.license_id == CITATION_LICENSE:
            if not (self.work and self.work.strip()):
                problems.append("citação exige work (título, estúdio e detentor da obra)")
            if not self.attribution_text.strip():
                problems.append("citação exige attribution_text (crédito da obra na descrição)")
            if not self.usage_notes.strip():
                problems.append("citação exige usage_notes: o trecho que o quadro ilustra e por quê")
        library = self.provider is Provider.YOUTUBE_AUDIO_LIBRARY
        if self.license_id == AUDIO_LIBRARY_LICENSE and not library:
            problems.append("licença da Audio Library só com provider youtube_audio_library")
        if library:
            if self.license_id not in {AUDIO_LIBRARY_LICENSE} | ATTRIBUTION_LICENSES:
                problems.append("faixa da Audio Library usa YouTube-Audio-Library ou a CC-BY da faixa")
            if not self.usage_notes.strip():
                problems.append("faixa da Audio Library exige usage_notes (só YouTube, sem voz cantada)")
        own = STOCK_LICENSES.get(self.provider)
        if own is None and self.license_id in STOCK_LICENSES.values():
            problems.append(f"licença {self.license_id!r} só vale para ativos do próprio banco")
        if own is not None:
            if self.license_id not in (own, "CC0-1.0"):
                problems.append(f"ativo de {self.provider.value} usa a licença {own!r} ou CC0-1.0")
            if not (self.author and self.attribution_text.strip()):
                problems.append("banco de imagem exige author e attribution_text (crédito no credits.txt)")
            if not self.usage_notes.strip():
                problems.append("banco de imagem exige usage_notes (conferência de pessoas, marcas e texto)")
        if problems:
            raise ValueError("ativo não pode ser aprovado: " + "; ".join(problems))
        return self
