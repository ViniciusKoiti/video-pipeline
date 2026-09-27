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
    local_path: RelPath  # texto extraído; um parágrafo = um trecho numerado (ADR 009)
    notes: str = ""
    interested: bool = False  # fonte interessada (a própria empresa ou família): nenhum fato só com ela
    authors: list[str] = []  # fontes que compartilham autor contam como uma só para independência (ADR 009)


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


# --- Planos (ADR 008) ----------------------------------------------------------------------------

Language = Literal["en", "pt-BR"]
Motion = Literal["push_in", "pull_out", "pan_left", "pan_right", "pan_up", "pan_down", "still"]


class Crop(Model):
    """Recorte normalizado (0–1) de uma foto: o detalhe que o plano mostra (um rosto, o nome no casco)."""

    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def _inside_image(self) -> Self:
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("recorte sai da imagem")
        return self


class _Shot(Model):
    anchor: NonEmpty  # trecho da narração coberto pelo plano; precisa aparecer na narração, em ordem
    claims: list[Claim] = []  # o que o plano afirma na tela também precisa de fonte (§2.2)


class _FactualShot(_Shot):
    claims: list[Claim] = Field(min_length=1)  # número, data, citação ou cargo na tela é afirmação


class PhotoShot(_Shot):
    kind: Literal["photo"] = "photo"
    visual_need: VisualNeed
    search_query: NonEmpty
    asset_id: AssetId | None = None
    crop: Crop | None = None
    motion: Motion = "push_in"


class BrollShot(_Shot):
    kind: Literal["broll"] = "broll"  # vídeo em movimento (banco de imagens ou filme de arquivo)
    visual_need: VisualNeed
    search_query: NonEmpty
    asset_id: AssetId | None = None


class NumberShot(_FactualShot):
    kind: Literal["number"] = "number"
    value: NonEmpty  # como aparece na tela: "1.500", "US$ 4,2 bi"
    label: NonEmpty


class ChartPoint(Model):
    label: NonEmpty
    value: float


class ChartShot(_FactualShot):
    kind: Literal["chart"] = "chart"
    title: NonEmpty
    unit: str = ""
    points: list[ChartPoint] = Field(min_length=2)


class QuoteShot(_FactualShot):
    kind: Literal["quote"] = "quote"  # citação ou manchete recriada como tipografia, nunca print (§8)
    text: NonEmpty
    attribution: NonEmpty
    style: Literal["quote", "headline"] = "quote"


class Place(Model):
    name: NonEmpty
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class MapShot(_Shot):
    kind: Literal["map"] = "map"
    places: list[Place] = Field(min_length=1)


class StampShot(_FactualShot):
    kind: Literal["stamp"] = "stamp"  # carimbo de data e lugar
    date: NonEmpty
    place: str = ""


class LowerThirdShot(_FactualShot):
    kind: Literal["lower_third"] = "lower_third"  # tarja de nome e cargo
    name: NonEmpty
    role: NonEmpty


class TimelineEvent(Model):
    date: NonEmpty
    label: NonEmpty


class TimelineShot(_FactualShot):
    kind: Literal["timeline"] = "timeline"
    events: list[TimelineEvent] = Field(min_length=2)


class Person(Model):
    id: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
    name: NonEmpty
    role: str = ""
    parent_ids: list[str] = []


class FamilyTreeShot(_FactualShot):
    kind: Literal["family_tree"] = "family_tree"
    people: list[Person] = Field(min_length=2)

    @model_validator(mode="after")
    def _parents_exist(self) -> Self:
        ids = {p.id for p in self.people}
        _unique([p.id for p in self.people], "pessoas")
        missing = sorted({pid for p in self.people for pid in p.parent_ids} - ids)
        if missing:
            raise ValueError(f"pais inexistentes na árvore: {', '.join(missing)}")
        return self


Shot = Annotated[
    PhotoShot
    | BrollShot
    | NumberShot
    | ChartShot
    | QuoteShot
    | MapShot
    | StampShot
    | LowerThirdShot
    | TimelineShot
    | FamilyTreeShot,
    Field(discriminator="kind"),
]
MEDIA_SHOT_KINDS = frozenset({"photo", "broll"})  # visual vem de um ativo
GRAPHIC_SHOT_KINDS = frozenset(
    {"number", "chart", "quote", "map", "stamp", "lower_third", "timeline", "family_tree"}
)


class Scene(Model):
    """Uma cena = um bloco de narração = um WAV (ADR 007), com uma lista de planos (ADR 008).
    Sem planos, vale a forma v1: um único plano de foto com os campos visuais da própria cena."""

    id: SceneId
    narration: NonEmpty
    claims: list[Claim] = []
    visual_need: VisualNeed | None = None  # forma v1
    search_query: NonEmpty | None = None  # forma v1
    chosen_asset_id: AssetId | None = None  # forma v1
    shots: list[Shot] = []  # forma v2
    duration_ms: int | None = Field(default=None, gt=0)  # medido da voz real, nunca estimado (§9)
    review_status: Status = Status.PENDING  # reflexo de review.json, escrito pelo código (§5)

    @model_validator(mode="after")
    def _visual_plan(self) -> Self:
        if not self.shots:
            if self.visual_need is None or self.search_query is None:
                raise ValueError(f"{self.id}: cena sem planos precisa de visual_need e search_query")
            return self
        cursor = 0
        for shot in self.shots:
            position = self.narration.find(shot.anchor, cursor)
            if position < 0:
                raise ValueError(
                    f"{self.id}: âncora {shot.anchor!r} não aparece na narração depois do plano anterior"
                )
            cursor = position + 1
        return self


def effective_shots(scene: Scene) -> list[Shot]:
    """Planos da cena; a forma v1 vira um único plano de foto sobre a narração inteira."""
    if scene.shots:
        return list(scene.shots)
    return [
        PhotoShot(
            anchor=scene.narration,
            visual_need=scene.visual_need,  # type: ignore[arg-type]  # garantido pelo validador da cena
            search_query=scene.search_query,  # type: ignore[arg-type]
            asset_id=scene.chosen_asset_id,
        )
    ]


class ScenesManifest(Model):
    episode_id: EpisodeId
    language: Language
    scenes: list[Scene] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        return self


# --- facts.json (ADR 009) ------------------------------------------------------------------------

FactId = Annotated[str, Field(pattern=r"^F\d{2,}$")]


class FactKind(StrEnum):
    """O que o fato faz pela história. `context` explica; os outros prendem o público."""

    NUMBER = "number"  # valor, preço, quantidade, escala
    CONFLICT = "conflict"  # disputa, risco, quem perdeu
    TURNING_POINT = "turning_point"  # decisão ou evento que mudou o rumo
    MECHANISM = "mechanism"  # como o dinheiro ou o poder foi feito
    CURIOSITY = "curiosity"  # detalhe contraintuitivo ou humano
    IMPACT_TODAY = "impact_today"  # o que o público usa ou paga hoje por causa do personagem
    RULE = "rule"  # lei, tarifa, subsídio ou decisão de Estado que mudou o negócio
    CONTEXT = "context"  # pano de fundo necessário


class Evidence(Model):
    excerpt_id: ExcerptId
    quote: NonEmpty  # cópia literal do trecho ("..." marca corte); `vp check` confere no texto da fonte


class Fact(Model):
    id: FactId
    text: NonEmpty  # o fato com palavras próprias, no idioma do episódio
    kind: FactKind
    when: str | None = None  # como a fonte dá: "1918", "ago. 1925"
    people: list[str] = []
    why_it_matters: NonEmpty  # por que o público se importaria
    evidence: list[Evidence] = Field(min_length=1)

    @property
    def source_ids(self) -> list[str]:
        return sorted({e.excerpt_id.split("#")[0] for e in self.evidence})


class FactsManifest(Model):
    """Fichas de fatos: a única base do roteiro. Cada fato traz a citação literal que o sustenta."""

    episode_id: EpisodeId
    language: Language
    facts: list[Fact] = Field(min_length=1)
    open_questions: list[str] = []  # perguntas que prenderiam o público e que as fontes não respondem

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([f.id for f in self.facts], "ids de fato")
        return self


# --- assets/<id>.json ----------------------------------------------------------------------------


class Provider(StrEnum):
    WIKIMEDIA_COMMONS = "wikimedia_commons"
    LIBRARY_OF_CONGRESS = "library_of_congress"
    FLICKR_COMMONS = "flickr_commons"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    UNSPLASH = "unsplash"
    COVERR = "coverr"  # só clipes baixados à mão pelo site (ADR 007, emenda de bancos de imagem)
    WORKERS_AI = "workers_ai"
    ORIGINAL = "original"  # mapa, cronologia ou tela gráfica feitos pelo projeto


# Lista fechada de licenças que podem chegar ao render (ADR 007). Qualquer outra — inclusive
# CC-BY-SA (compartilhamento pela mesma licença alcançaria o vídeo) e NC (canal monetizado) —
# mantém o ativo fora de approved; a decisão vira revisão humana.
PUBLIC_DOMAIN_LICENSES = frozenset({"PD-US", "PD-old"})
ATTRIBUTION_LICENSES = frozenset({"CC-BY-2.0", "CC-BY-2.5", "CC-BY-3.0", "CC-BY-3.0-BR", "CC-BY-4.0"})
# Banco de imagem: a licença do próprio banco, ou CC0-1.0 na parte do acervo que a tem.
STOCK_LICENSES = {
    Provider.PEXELS: "Pexels",
    Provider.PIXABAY: "Pixabay",
    Provider.UNSPLASH: "Unsplash",
    Provider.COVERR: "Coverr",
}
ACCEPTED_LICENSES = (
    PUBLIC_DOMAIN_LICENSES
    | ATTRIBUTION_LICENSES
    | set(STOCK_LICENSES.values())
    | {"CC0-1.0", "Flickr-NKCR", "Generated", "Original"}
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
        matches = [e for e in self.entries if (e.step, e.scene_id, e.asset_id) == (step, scene_id, asset_id)]
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


class EpisodeShot(Model):
    """Plano com tempo resolvido, relativo ao início da cena (ADR 008)."""

    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    spec: Shot
    media: RelPath | None = None  # arquivo do ativo, para foto e B-roll

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms

    @model_validator(mode="after")
    def _media_when_needed(self) -> Self:
        if (self.spec.kind in MEDIA_SHOT_KINDS) != (self.media is not None):
            raise ValueError(f"plano {self.spec.kind}: media é obrigatório para foto/B-roll e só para eles")
        return self


class EpisodeScene(Model):
    id: SceneId
    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    narration: NonEmpty
    audio: RelPath
    asset_id: AssetId | None = None  # v1: um visual por cena
    image: RelPath | None = None  # v1
    shots: list[EpisodeShot] = []  # v2: planos cobrindo a cena inteira

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms

    @model_validator(mode="after")
    def _one_visual_form(self) -> Self:
        if self.shots:
            if self.image is not None or self.asset_id is not None:
                raise ValueError(f"{self.id}: use image/asset_id (v1) ou shots (v2), não os dois")
            cursor = 0
            for shot in self.shots:
                if shot.start_ms != cursor:
                    raise ValueError(f"{self.id}: planos com buraco ou sobreposição em {shot.start_ms} ms")
                cursor = shot.end_ms
            if cursor != self.duration_ms:
                raise ValueError(f"{self.id}: planos somam {cursor} ms, a cena tem {self.duration_ms} ms")
        elif self.image is None or self.asset_id is None:
            raise ValueError(f"{self.id}: cena sem planos precisa de image e asset_id (v1)")
        return self


class EpisodeManifest(Model):
    """Única entrada do motor de montagem (§6). Timing vem da duração real dos WAVs.
    Versões: 1 (ADR 001, um visual por cena) e 2 (ADR 008, lista de planos). Mudar exige nova ADR."""

    schema_version: Literal[1, 2] = 1
    episode_id: EpisodeId
    title: NonEmpty
    language: Language
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
        with_shots = [bool(s.shots) for s in self.scenes]
        if self.schema_version == 1 and any(with_shots):
            raise ValueError("schema_version 1 não tem planos; use 2 (ADR 008)")
        if self.schema_version == 2 and not all(with_shots):
            raise ValueError("schema_version 2 exige planos em todas as cenas")
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
        for claim in scene.claims + [c for shot in scene.shots for c in shot.claims]:
            refs = claim.source_ids + [_EXCERPT_RE.sub(r"\1", e) for e in claim.excerpt_ids]
            problems += [f"{scene.id}: fonte {r} não está em sources.json" for r in refs if r not in known]
    return sorted(set(problems))


# §2.4: stock (os bancos de STOCK_LICENSES) e imagem gerada são ilustração, nunca registro do fato.
_NOT_A_RECORD = frozenset({*STOCK_LICENSES, Provider.WORKERS_AI})


def visual_need_violations(scenes: ScenesManifest, assets: dict[str, Asset]) -> list[str]:
    """Planos de foto/B-roll cujo ativo escolhido não existe ou não serve ao visual_need."""
    problems = []
    for scene in scenes.scenes:
        for shot in effective_shots(scene):
            if not isinstance(shot, PhotoShot | BrollShot) or shot.asset_id is None:
                continue
            asset = assets.get(shot.asset_id)
            if asset is None:
                problems.append(f"{scene.id}: ativo {shot.asset_id} não encontrado")
            elif shot.visual_need is VisualNeed.HISTORICAL_EXACT and asset.provider in _NOT_A_RECORD:
                problems.append(f"{scene.id}: historical_exact não pode usar {asset.provider.value}")
    return problems
