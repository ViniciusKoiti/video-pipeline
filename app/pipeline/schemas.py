"""Contratos de dados dos manifestos (CLAUDE.md §6, ADR 007).

Os modelos validam o que dá para garantir olhando um arquivo só. Regras que cruzam arquivos
(claim → sources.json, visual_need → ativo) ficam nas funções do fim do módulo.
"""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


# --- Identificadores e tipos básicos -----------------------------------------------------------

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


def _unique(ids: list[str], what: str) -> None:
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"{what} duplicados: {', '.join(duplicates)}")


class Status(StrEnum):
    """Estados de etapa, cena e ativo (§5)."""

    PENDING = "pending"
    RUNNING = "running"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"


APPROVED_STATES = frozenset({Status.APPROVED, Status.COMPLETED})


class VisualNeed(StrEnum):
    HISTORICAL_EXACT = "historical_exact"
    CONTEXTUAL_STOCK = "contextual_stock"
    MAP_OR_GRAPHIC = "map_or_graphic"
    ILLUSTRATIVE_RECONSTRUCTION = "illustrative_reconstruction"


# --- sources.json --------------------------------------------------------------------------------


class SourceKind(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    NEWSPAPER = "newspaper"
    ARCHIVE = "archive"


class Source(Model):
    id: SourceId
    title: NonEmpty
    url: HttpUrl
    kind: SourceKind
    retrieved_at: AwareDatetime
    local_path: RelPath  # texto extraído
    notes: str = ""


class SourcesManifest(Model):
    """O mínimo de 2 fontes independentes fica para o gate 1: independência é julgamento humano."""

    episode_id: EpisodeId
    sources: list[Source]

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.sources], "ids de fonte")
        return self


# --- scenes.json ---------------------------------------------------------------------------------


class Claim(Model):
    text: NonEmpty
    source_ids: list[SourceId] = Field(min_length=1)  # §2.2: toda claim tem fonte
    excerpt_ids: list[ExcerptId] = []  # opcional até a ADR 002 (etapa 26)

    @model_validator(mode="after")
    def _excerpts_belong_to_sources(self) -> Self:
        foreign = [e for e in self.excerpt_ids if e.split("#")[0] not in self.source_ids]
        if foreign:
            raise ValueError(f"trechos de fontes fora de source_ids: {', '.join(foreign)}")
        return self


class Scene(Model):
    """Uma cena = um bloco de narração = um WAV = um visual (ADR 007)."""

    id: SceneId
    narration: NonEmpty
    claims: list[Claim] = []
    visual_need: VisualNeed
    search_query: NonEmpty
    chosen_asset_id: AssetId | None = None
    duration_ms: int | None = Field(default=None, gt=0)  # medido da voz real, nunca estimado (§9)
    review_status: Status = Status.PENDING  # reflexo de review.json, escrito pelo código (§5)


class ScenesManifest(Model):
    episode_id: EpisodeId
    language: Literal["en"]
    scenes: list[Scene] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        return self


# --- assets/<id>.json ----------------------------------------------------------------------------


class Provider(StrEnum):
    WIKIMEDIA_COMMONS = "wikimedia_commons"
    LIBRARY_OF_CONGRESS = "library_of_congress"
    FLICKR_COMMONS = "flickr_commons"
    PEXELS = "pexels"
    WORKERS_AI = "workers_ai"
    ORIGINAL = "original"  # mapa, cronologia ou tela gráfica feitos pelo projeto


# Lista fechada de licenças que podem chegar ao render (ADR 007). Qualquer outra — inclusive
# CC-BY-SA (compartilhamento pela mesma licença alcançaria o vídeo) e NC (canal monetizado) —
# mantém o ativo fora de approved; a decisão vira revisão humana.
PUBLIC_DOMAIN_LICENSES = frozenset({"PD-US", "PD-old"})
ATTRIBUTION_LICENSES = frozenset({"CC-BY-2.0", "CC-BY-2.5", "CC-BY-3.0", "CC-BY-4.0"})
ACCEPTED_LICENSES = (
    PUBLIC_DOMAIN_LICENSES
    | ATTRIBUTION_LICENSES
    | {"CC0-1.0", "Flickr-NKCR", "Pexels", "Generated", "Original"}
)


class Generation(Model):
    prompt: NonEmpty
    model: NonEmpty
    seed: int
    steps: int = Field(gt=0)


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
        if problems:
            raise ValueError("ativo não pode ser aprovado: " + "; ".join(problems))
        return self


# --- review.json ---------------------------------------------------------------------------------


class Step(StrEnum):
    FORMAT = "format"  # modalidade do vídeo, recomendada por app.pipeline.format_decision (ADR 001)
    SOURCES = "sources"
    SCRIPT = "script"
    SCENES = "scenes"
    ASSETS = "assets"
    VOICE = "voice"
    SUBS = "subs"
    PREVIEW = "preview"
    EXPORT = "export"


class Decision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ReviewEntry(Model):
    step: Step
    scene_id: SceneId | None = None  # alvo opcional: uma cena...
    asset_id: AssetId | None = None  # ...ou um ativo; nenhum = a etapa inteira
    decision: Decision
    reviewer: NonEmpty
    at: AwareDatetime
    input_hash: str | None = None  # hash do conteúdo revisado; mudou → a aprovação não vale (§5)
    choice: str | None = None  # valor escolhido pelo humano quando difere da recomendação (ex.: formato)
    notes: str = ""

    @model_validator(mode="after")
    def _single_target(self) -> Self:
        if self.scene_id is not None and self.asset_id is not None:
            raise ValueError("uma entrada revisa a etapa, uma cena ou um ativo, não ambos")
        return self


class ReviewLog(Model):
    """Fonte única das decisões humanas (§5, ADR 007). Só cresce: entradas nunca são editadas."""

    episode_id: EpisodeId
    entries: list[ReviewEntry] = []

    def latest(
        self, step: Step, *, scene_id: str | None = None, asset_id: str | None = None
    ) -> ReviewEntry | None:
        matches = [
            e for e in self.entries if (e.step, e.scene_id, e.asset_id) == (step, scene_id, asset_id)
        ]
        return max(matches, key=lambda e: e.at) if matches else None

    def is_approved(
        self,
        step: Step,
        *,
        scene_id: str | None = None,
        asset_id: str | None = None,
        input_hash: str | None = None,
    ) -> bool:
        entry = self.latest(step, scene_id=scene_id, asset_id=asset_id)
        if entry is None or entry.decision is not Decision.APPROVED:
            return False
        return input_hash is None or entry.input_hash == input_hash


# --- episode.json (contrato do render) ----------------------------------------------------------


class EpisodeFormat(StrEnum):
    """Formato do episódio: decide o motor de render pelo mapa de config/providers.toml (ADR 001)."""

    ARCHIVAL_DOCUMENTARY = "archival_documentary"  # fotos de arquivo + narração (motor ffmpeg)
    EXPLAINER = "explainer"  # visual gerado a partir de dados (Remotion + motion-kit; etapa 43)


class VideoSpec(Model):
    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)
    fps: int = Field(default=30, gt=0)
    audio_sample_rate: int = Field(default=48_000, gt=0)

    @model_validator(mode="after")
    def _sixteen_by_nine(self) -> Self:
        if self.width * 9 != self.height * 16:
            raise ValueError(f"{self.width}x{self.height} não é 16:9")
        return self


class EpisodeScene(Model):
    id: SceneId
    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    narration: NonEmpty
    asset_id: AssetId
    image: RelPath
    audio: RelPath

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms


class EpisodeManifest(Model):
    """Única entrada do motor de montagem (§6). Timing vem da duração real dos WAVs.
    Contrato congelado na versão 1 (ADR 001): mudar campos exige nova ADR e nova versão."""

    schema_version: Literal[1] = 1
    episode_id: EpisodeId
    title: NonEmpty
    language: Literal["en"]
    format: EpisodeFormat = EpisodeFormat.ARCHIVAL_DOCUMENTARY
    video: VideoSpec = Field(default_factory=VideoSpec)
    scenes: list[EpisodeScene] = Field(min_length=1)
    captions: RelPath | None = None  # captions.srt editável

    @property
    def duration_ms(self) -> int:
        return self.scenes[-1].end_ms

    @model_validator(mode="after")
    def _ordered_timeline(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        for previous, current in zip(self.scenes, self.scenes[1:], strict=False):
            if current.start_ms < previous.end_ms:
                raise ValueError(f"cena {current.id} começa antes do fim de {previous.id}")
        return self


# --- Verificações entre arquivos -----------------------------------------------------------------

_EXCERPT_RE = re.compile(r"^(source-\d{2,})#E\d+$")


def unknown_source_refs(scenes: ScenesManifest, sources: SourcesManifest) -> list[str]:
    """§2.2: claims e trechos que citam fontes ausentes de sources.json."""
    known = {s.id for s in sources.sources}
    problems = []
    for scene in scenes.scenes:
        for claim in scene.claims:
            refs = claim.source_ids + [_EXCERPT_RE.sub(r"\1", e) for e in claim.excerpt_ids]
            problems += [f"{scene.id}: fonte {r} não está em sources.json" for r in refs if r not in known]
    return sorted(set(problems))


# §2.4: stock e imagem gerada são ilustração, nunca registro do fato.
_NOT_A_RECORD = frozenset({Provider.PEXELS, Provider.WORKERS_AI})


def visual_need_violations(scenes: ScenesManifest, assets: dict[str, Asset]) -> list[str]:
    """Cenas cujo ativo escolhido não existe ou não serve ao visual_need."""
    problems = []
    for scene in scenes.scenes:
        if scene.chosen_asset_id is None:
            continue
        asset = assets.get(scene.chosen_asset_id)
        if asset is None:
            problems.append(f"{scene.id}: ativo {scene.chosen_asset_id} não encontrado")
        elif scene.visual_need is VisualNeed.HISTORICAL_EXACT and asset.provider in _NOT_A_RECORD:
            problems.append(f"{scene.id}: historical_exact não pode usar {asset.provider.value}")
    return problems
