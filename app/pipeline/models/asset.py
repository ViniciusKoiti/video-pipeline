from __future__ import annotations

from typing import Literal, Self

from pydantic import AwareDatetime, model_validator

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_types import AssetId, HttpUrl, NonEmpty, SceneId, Sha256
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
    media: Literal["still", "clip"] = "still"  # clipe só na licença Citacao (emenda de 2026-11-03 da ADR 007)
    origin: str | None = None  # clipe: de onde veio (o dono escolhe e responde)
    timecode: str | None = None  # clipe: entrada e saída na obra, ex. "00:12:03-00:12:08"

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

    def _citation_problems(self) -> list[str]:
        """Emenda de citação (ADR 007): quadro parado oficial ou clipe de origem declarada."""
        problems: list[str] = []
        cited_providers = (Provider.OFFICIAL, Provider.OWNER_CAPTURE)
        if (self.license_id == SchemasConstants.CITATION_LICENSE) != (self.provider in cited_providers):
            problems.append("citação só de material oficial público do detentor (provider official)")
        if self.provider is Provider.OWNER_CAPTURE and self.media != "clip":
            problems.append("captura do dono só vale para clipe (quadro parado exige material oficial)")
        if self.media == "clip" and self.license_id != SchemasConstants.CITATION_LICENSE:
            problems.append("clipe só na licença Citacao")
        if self.media == "clip" and not (self.origin and self.origin.strip() and self.timecode):
            problems.append("clipe exige origin (de onde veio) e timecode (entrada e saída na obra)")
        if self.license_id == SchemasConstants.CITATION_LICENSE:
            if not (self.work and self.work.strip()):
                problems.append("citação exige work (título, estúdio e detentor da obra)")
            if not self.attribution_text.strip():
                problems.append("citação exige attribution_text (crédito da obra na descrição)")
            if not self.usage_notes.strip():
                problems.append("citação exige usage_notes: o trecho que o quadro ilustra e por quê")
        return problems

    @model_validator(mode="after")
    def _approval_requires_rights(self) -> Self:
        """§2.3: nenhum ativo sem licença registrada entra no render."""
        if self.review_status not in SchemasConstants.APPROVED_STATES:
            return self
        problems = []
        if self.license_id not in SchemasConstants.ACCEPTED_LICENSES:
            problems.append(f"licença {self.license_id!r} fora da lista aceita")
        if self.sha256 is None:
            problems.append("sha256 ausente (arquivo final não baixado)")
        if self.license_id in SchemasConstants.PUBLIC_DOMAIN_LICENSES and not self.usage_notes.strip():
            problems.append("domínio público exige o raciocínio em usage_notes (§8)")
        if self.license_id in SchemasConstants.ATTRIBUTION_LICENSES and not (
            self.author and self.attribution_text.strip()
        ):
            problems.append("CC-BY exige author e attribution_text")
        no_page = (Provider.WORKERS_AI, Provider.ORIGINAL, Provider.OWNER_CAPTURE)
        if self.provider not in no_page and not self.page_url:
            problems.append("ativo de acervo exige page_url")
        problems += self._citation_problems()
        library = self.provider is Provider.YOUTUBE_AUDIO_LIBRARY
        if self.license_id == SchemasConstants.AUDIO_LIBRARY_LICENSE and not library:
            problems.append("licença da Audio Library só com provider youtube_audio_library")
        if library:
            if (
                self.license_id
                not in {SchemasConstants.AUDIO_LIBRARY_LICENSE} | SchemasConstants.ATTRIBUTION_LICENSES
            ):
                problems.append("faixa da Audio Library usa YouTube-Audio-Library ou a CC-BY da faixa")
            if not self.usage_notes.strip():
                problems.append("faixa da Audio Library exige usage_notes (só YouTube, sem voz cantada)")
        own = SchemasConstants.STOCK_LICENSES.get(self.provider)
        if own is None and self.license_id in SchemasConstants.STOCK_LICENSES.values():
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
