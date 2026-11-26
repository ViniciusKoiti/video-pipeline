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
    # clipe: Citacao (2026-11-03), Original (2026-11-09) ou Generated (2026-11-26)
    media: Literal["still", "clip"] = "still"
    # citado: de onde veio; Original: composição e código; Generated: gerador, modelo e projeto
    origin: str | None = None
    timecode: str | None = None  # clipe citado: entrada e saída na obra, ex. "00:12:03-00:12:08"

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
        if self.media == "clip" and self.license_id not in SchemasConstants.CLIP_LICENSES:
            problems.append("clipe só na licença Citacao, Original (do projeto) ou Generated (do dono)")
        cited_clip = self.media == "clip" and self.license_id == SchemasConstants.CITATION_LICENSE
        if cited_clip and not (self.origin and self.origin.strip() and self.timecode):
            problems.append("clipe exige origin (de onde veio) e timecode (entrada e saída na obra)")
        if self.media == "clip" and self.license_id == SchemasConstants.ORIGINAL_LICENSE:
            problems += self._original_clip_problems()
        if self.media == "clip" and self.license_id == SchemasConstants.GENERATED_LICENSE:
            problems += self._generated_clip_problems()
        if self.license_id == SchemasConstants.CITATION_LICENSE:
            if not (self.work and self.work.strip()):
                problems.append("citação exige work (título, estúdio e detentor da obra)")
            if not self.attribution_text.strip():
                problems.append("citação exige attribution_text (crédito da obra na descrição)")
            if not self.usage_notes.strip():
                problems.append("citação exige usage_notes: o trecho que o quadro ilustra e por quê")
        return problems

    def _original_clip_problems(self) -> list[str]:
        """Emenda de 2026-11-09 (ADR 001, item 5, e ADR 007): clipe animado do projeto (ativo Original)."""
        problems: list[str] = []
        if self.provider is not Provider.ORIGINAL:
            problems.append("clipe Original só com provider original")
        if not (self.origin and self.origin.strip()):
            problems.append("clipe Original exige origin: a composição e o arquivo de código que o geram")
        if not self.usage_notes.strip():
            problems.append("clipe Original exige usage_notes: props, duração e conferência do clipe")
        if self.timecode:
            problems.append("timecode é só de clipe citado (Citacao)")
        return problems

    def _generated_clip_problems(self) -> list[str]:
        """Emenda de 2026-11-26 (ADR 007): clipe gerado pelo dono num gerador com termos registrados."""
        problems: list[str] = []
        if self.provider is not Provider.ORIGINAL:
            problems.append("clipe Generated só com provider original")
        if not (self.origin and self.origin.strip()):
            problems.append("clipe Generated exige origin: o gerador, o modelo e o projeto de onde saiu")
        if not self.usage_notes.strip():
            problems.append("clipe Generated exige usage_notes: o prompt e a conferência do clipe")
        if self.timecode:
            problems.append("timecode é só de clipe citado (Citacao)")
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
