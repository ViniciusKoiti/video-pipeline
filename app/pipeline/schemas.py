"""Contratos de dados dos manifestos (CLAUDE.md §6, ADR 007).

Os modelos validam o que dá para garantir olhando um arquivo só. Regras que cruzam arquivos
(claim → sources.json, visual_need → ativo) ficam nas funções do fim do módulo.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.media.narration import narration_problems, strip_pauses


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


# Ano ("1927") ou data ISO ("1927-03" ou "1927-03-12"): posição num eixo de tempo (ADR 011).
_WHEN_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
_YEAR_RE = re.compile(r"(?<!\d)\d{4}(?!\d)")
# Número como aparece na tela ("R$ 47,6 bi", "1.500", "78%"): prefixo, dígitos e sufixo (regra do `number`).
_SCREEN_NUMBER_RE = re.compile(r"^(\D*?)([\d.,]*\d)(.*)$")
# Separador de milhar e de decimal de cada idioma: o mesmo texto vale outro número em outro idioma, então o
# valor da tela segue a convenção do idioma do episódio (ADR 011, emenda "número por idioma").
NUMBER_SEPARATORS: dict[Language, tuple[str, str]] = {"pt-BR": (".", ","), "en": (",", ".")}


def screen_parts(value: str) -> tuple[str, str, str] | None:
    """(prefixo, dígitos, sufixo) como escritos, sem ler o número: a leitura depende do idioma."""
    match = _SCREEN_NUMBER_RE.match(value.strip())
    if match is None:
        return None
    return match.group(1).strip(), match.group(2), match.group(3).strip()


def screen_number(value: str, language: Language = "pt-BR") -> tuple[str, float, str] | None:
    """(prefixo, número, sufixo) de um valor escrito na convenção do idioma ("1.500,5" em pt-BR, "1,500.5" em
    en); None se não houver número reconhecível."""
    parts = screen_parts(value)
    if parts is None:
        return None
    group, decimal = NUMBER_SEPARATORS[language]
    try:
        return parts[0], float(parts[1].replace(group, "").replace(decimal, ".")), parts[2]
    except ValueError:
        return None


def number_format_problem(value: str, language: Language = "pt-BR") -> str | None:
    """Por que o número de `value` não segue a convenção do idioma, ou None. Texto sem número passa. Só pega
    o que é inequívoco: "1,500" é 1.500 em inglês e 1,5 em português, e os dois são escritas válidas."""
    parts = screen_parts(value)
    if parts is None:
        return None
    group, decimal = NUMBER_SEPARATORS[language]
    group_re, decimal_re = re.escape(group), re.escape(decimal)
    if re.fullmatch(rf"(\d{{1,3}}({group_re}\d{{3}})+|\d+)({decimal_re}\d+)?", parts[1]):
        return None
    return f"{value!r} não segue a convenção de {language} (ex.: 1{group}500{decimal}5)"


class ChartShot(_FactualShot):
    kind: Literal["chart"] = "chart"
    title: NonEmpty
    unit: str = ""
    points: list[ChartPoint] = Field(min_length=2)
    type: Literal["bar", "bar_horizontal", "line", "share"] = "bar"  # ADR 011
    highlight: str | None = None  # rótulo do ponto em destaque; sem ele, nenhum destaque
    y_from_zero: bool = True  # só `line`: eixo a partir do zero, para não exagerar variação pequena
    rest: str | None = None  # só `share`: rótulo da fatia do que sobra (ex.: "outros")

    @model_validator(mode="after")
    def _consistent_type(self) -> Self:
        labels = [p.label for p in self.points]
        if self.highlight is not None and self.highlight not in labels:
            raise ValueError(f"destaque {self.highlight!r} não é um dos rótulos do gráfico")
        if self.type == "line" and not all(_WHEN_RE.match(label) for label in labels):
            raise ValueError("gráfico de linha: os rótulos precisam ser anos (1927) ou datas ISO")
        if self.type == "share" and any(p.value < 0 for p in self.points):
            raise ValueError("gráfico de participação sem valor negativo")
        if self.rest is not None and self.type != "share":
            raise ValueError("rest só vale no gráfico de participação (type share)")
        return self


class DocumentHeader(Model):
    """Cabeçalho da página recriada; o texto real da página é só o trecho citado (ADR 011)."""

    title: NonEmpty
    issuer: str = ""
    date: str = ""


class QuoteShot(_FactualShot):
    kind: Literal["quote"] = "quote"  # citação ou manchete recriada como tipografia, nunca print (§8)
    text: NonEmpty  # literal num dos trechos citados (`vp check`, ADR 011)
    attribution: NonEmpty
    style: Literal["quote", "headline", "document"] = "quote"
    document: DocumentHeader | None = None  # obrigatório em `document`; opcional em `headline`
    variant: Literal["report", "newspaper", "letter"] = "report"  # só `document`

    @model_validator(mode="after")
    def _document_header(self) -> Self:
        if self.style == "document" and self.document is None:
            raise ValueError("citação em página de documento precisa do cabeçalho (document)")
        if self.style == "quote" and self.document is not None:
            raise ValueError("document só vale nos estilos document e headline")
        return self


class Place(Model):
    name: NonEmpty
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class _FromTo(Model):
    """`from` é palavra reservada no Python: o campo se chama `from_` e o JSON continua com "from"."""

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, serialize_by_alias=True, validate_by_name=True
    )

    from_: NonEmpty = Field(alias="from")
    to: NonEmpty


class Route(_FromTo):
    """Rota entre dois lugares do mapa, pelos nomes em `places`."""


# País (ISO 3166-1 alfa-3, "BRA") ou estado (ISO 3166-2, "BR-SP").
RegionCode = Annotated[str, Field(pattern=r"^([A-Z]{3}|[A-Z]{2}-[A-Z0-9]{1,3})$")]


class MapShot(_Shot):
    kind: Literal["map"] = "map"
    places: list[Place] = Field(min_length=1)
    scope: Literal["region", "world"] = "region"  # ADR 011
    highlight: list[RegionCode] = []  # países ou estados acesos, em ordem
    routes: list[Route] = []

    @model_validator(mode="after")
    def _routes_and_claims(self) -> Self:
        names = {p.name for p in self.places}
        for route in self.routes:
            missing = sorted({route.from_, route.to} - names)
            if missing:
                raise ValueError(f"rota com lugar fora de places: {', '.join(missing)}")
        if (self.highlight or self.routes) and not self.claims:
            raise ValueError("mapa com países acesos ou rotas afirma algo: precisa de claims (§2.2)")
        return self


class StampShot(_FactualShot):
    kind: Literal["stamp"] = "stamp"  # carimbo de data e lugar
    date: NonEmpty
    place: str = ""


class LowerThirdShot(_FactualShot):
    kind: Literal["lower_third"] = "lower_third"  # tarja de nome e cargo
    name: NonEmpty
    role: NonEmpty


class TimelineEvent(Model):
    date: NonEmpty  # texto na tela ("7 jan. 1918", "anos 1920")
    label: NonEmpty
    when: str | None = None  # ano ou data ISO: posição na escala real (ADR 011)

    @field_validator("when", mode="before")
    @classmethod
    def _year_as_text(cls, value: object) -> object:
        return str(value) if isinstance(value, int) else value

    @model_validator(mode="after")
    def _when_matches_date(self) -> Self:
        if self.when is None:
            return self
        if not _WHEN_RE.match(self.when):
            raise ValueError(f"when {self.when!r}: use o ano (1927) ou uma data ISO (1927-03-12)")
        years = _YEAR_RE.findall(self.date)
        if years and self.when[:4] not in years:
            raise ValueError(f"when {self.when!r} não bate com o ano escrito em {self.date!r}")
        return self


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


# --- Planos editoriais (ADR 011) -----------------------------------------------------------------


class CompareSide(Model):
    value: NonEmpty  # como aparece na tela, como no `number`: "69 mil", "R$ 47,6 bi"
    label: NonEmpty


class CompareShot(_FactualShot):
    """Dois valores lado a lado; a tela não calcula razão nem variação (ADR 011, decisão 7). Um valor
    calculado pelo roteiro entra só como conta dita inteira, com insumos e regra em fichas (ADR 020)."""

    kind: Literal["compare"] = "compare"
    left: CompareSide
    right: CompareSide
    mode: Literal["side", "before_after", "scale"] = "side"
    emphasis: Literal["left", "right"] | None = None  # só o peso da fonte; o outro lado não apaga

    @model_validator(mode="after")
    def _scale_needs_same_unit(self) -> Self:
        if self.mode != "scale":
            return self
        # A unidade (prefixo e sufixo) não depende do idioma, então aqui o número não é lido: "US$ 1,234,567"
        # é número em inglês, e seria recusado se lido como pt-BR.
        left, right = screen_parts(self.left.value), screen_parts(self.right.value)
        if left is None or right is None:
            raise ValueError("comparação em escala precisa de dois números")
        if (left[0], left[2]) != (right[0], right[2]):
            raise ValueError(
                f"comparação em escala com unidades diferentes: {self.left.value!r} e {self.right.value!r}"
            )
        return self


NodeId = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]


class NetworkNode(Model):
    id: NodeId
    label: NonEmpty  # nome da pessoa ou instituição
    role: str = ""
    # O ícone sai do tipo, no template: o roteiro não escolhe ícone, cor nem logo.
    kind: Literal["person", "family", "company", "bank", "government", "other"]


class NetworkEdge(_FromTo):
    label: str = ""  # a relação ("controla", "empresta a")
    value: str = ""  # valor na seta, como aparece na tela
    style: Literal["solid", "dashed"] = "solid"  # tracejada: relação indireta
    flow: bool = False  # dinheiro correndo de `from` para `to`
    claims: list[Claim] = Field(min_length=1)  # cada relação é uma afirmação (§2.2)


class NetworkStep(Model):
    anchor: NonEmpty  # trecho da narração em que o passo entra, depois da âncora do plano
    nodes: list[NodeId] = []  # nós que entram
    highlight: list[NodeId] = []  # nós acesos (e as arestas entre eles); o resto esmaece

    @model_validator(mode="after")
    def _does_something(self) -> Self:
        if not self.nodes and not self.highlight:
            raise ValueError(f"passo {self.anchor!r} sem nós novos nem destaque")
        return self


class NetworkShot(_FactualShot):
    """Rede que cresce no ritmo da narração enquanto a câmera se afasta (ExpandingNetwork)."""

    kind: Literal["network"] = "network"
    root: NodeId
    nodes: list[NetworkNode] = Field(min_length=2)
    edges: list[NetworkEdge] = Field(min_length=1)
    steps: list[NetworkStep] = Field(min_length=1)
    layout: Literal["radial", "layered"] = "radial"

    @model_validator(mode="after")
    def _consistent_graph(self) -> Self:
        ids = [n.id for n in self.nodes]
        _unique(ids, "nós da rede")
        _unique([f"{e.from_}->{e.to}" for e in self.edges], "arestas da rede")
        known = set(ids)
        if self.root not in known:
            raise ValueError(f"raiz {self.root!r} não está entre os nós")
        referenced = {self.root} | {x for e in self.edges for x in (e.from_, e.to)}
        referenced |= {x for s in self.steps for x in s.nodes + s.highlight}
        unknown = sorted(referenced - known)
        if unknown:
            raise ValueError(f"nós inexistentes na rede: {', '.join(unknown)}")
        entering = [x for s in self.steps for x in s.nodes]
        _unique(entering, "nós que entram nos passos")
        if self.root in entering:
            raise ValueError("a raiz já abre o plano; não entra de novo num passo")
        never = sorted(known - set(entering) - {self.root})
        if never:
            raise ValueError(f"nós que nunca entram na rede: {', '.join(never)}")
        return self


KEYWORD_MAX_WORDS = 8


def _fold(text: str) -> str:
    """Comparação de texto na tela com a narração: sem diferença de maiúscula nem de espaços."""
    return " ".join(text.casefold().split())


class KeywordShot(_Shot):
    """Frase-chave da narração na tela (KineticHeadline). Cópia literal da narração da cena, que já tem
    as suas claims; por isso o plano não exige claims próprias (ADR 011)."""

    kind: Literal["keyword"] = "keyword"
    text: NonEmpty
    highlight: str = ""  # trecho do `text` em destaque

    @model_validator(mode="after")
    def _short_and_consistent(self) -> Self:
        if len(self.text.split()) > KEYWORD_MAX_WORDS:
            raise ValueError(f"frase na tela com mais de {KEYWORD_MAX_WORDS} palavras: {self.text!r}")
        if self.highlight and _fold(self.highlight) not in _fold(self.text):
            raise ValueError(f"destaque {self.highlight!r} fora da frase {self.text!r}")
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
    | FamilyTreeShot
    | CompareShot
    | NetworkShot
    | KeywordShot,
    Field(discriminator="kind"),
]
MEDIA_SHOT_KINDS = frozenset({"photo", "broll"})  # visual vem de um ativo
GRAPHIC_SHOT_KINDS = frozenset(
    {"number", "chart", "quote", "map", "stamp", "lower_third", "timeline", "family_tree", "compare",
     "network", "keyword"}
)
# Desenhados por cima da foto ou do B-roll anterior da mesma cena; os outros gráficos ficam em tela cheia
# (ADR 011, decisão 5).
OVERLAY_SHOT_KINDS = frozenset({"lower_third", "stamp", "number", "keyword"})

Orientation = Literal["landscape", "portrait"]  # 16:9 ou 9:16 (ADR 014)
# Planos com layout em retrato; rede, mapa, linha do tempo, árvore e documento dependem de canvas largo.
PORTRAIT_SHOT_KINDS = frozenset(
    {"photo", "broll", "number", "keyword", "stamp", "lower_third", "compare", "chart"}
)


def portrait_problems(scene_id: str, kinds: list[str]) -> list[str]:
    """Planos de uma cena que não cabem no perfil vertical (ADR 014), um erro por plano."""
    allowed = ", ".join(sorted(PORTRAIT_SHOT_KINDS))
    return [
        f"{scene_id}: plano {kind} não cabe em retrato (9:16); use {allowed}"
        for kind in kinds
        if kind not in PORTRAIT_SHOT_KINDS
    ]


# --- Apresentador em janela flutuante (ADR 013) --------------------------------------------------

HostCorner = Literal["top-left", "top-right", "bottom-left", "bottom-right"]
# sentido horário
HOST_CORNERS: tuple[HostCorner, ...] = ("top-left", "top-right", "bottom-right", "bottom-left")
HostVariant = Annotated[str, Field(pattern=r"^(variant\d{2}|hat)$")]  # nome de peça do Notionists (CC0)


class HostIdentity(Model):
    """Peças do personagem (estilo Notionists, DiceBear); sem peça, vale a do estilo (ou nenhuma)."""

    hair: HostVariant
    outfit: HostVariant
    eyes: HostVariant = "variant05"
    brows: HostVariant | None = None
    nose: HostVariant | None = None
    facial_hair: HostVariant | None = None
    glasses: HostVariant | None = None


class HostSpec(Model):
    """O apresentador do episódio: um personagem numa janela que muda de canto a cada cena (ADR 013).
    A boca segue o áudio de cada cena; o canto sai de uma regra sobre os planos (`app/media/host.py`).

    Pele `notionists`: personagem montado de peças (`identity`). Pele `dono` (ADR 017, parte A): o desenho
    do dono, em imagens na pasta do episódio (`app/media/host.py`), sem peças."""

    skin: Literal["notionists", "dono"] = "notionists"
    identity: HostIdentity | None = None

    @model_validator(mode="after")
    def _identity_matches_skin(self) -> Self:
        if self.skin == "notionists" and self.identity is None:
            raise ValueError("a pele notionists precisa de identity (as peças do personagem)")
        if self.skin != "notionists" and self.identity is not None:
            raise ValueError(f"a pele {self.skin} é um desenho pronto: não leva identity")
        return self
    width: float | None = Field(default=None, ge=0.1, le=0.5)  # fração do quadro; padrão por perfil

    def width_for(self, *, portrait: bool) -> float:
        """Largura da janela: a dada, ou o padrão do perfil (o quadro em pé é mais estreito)."""
        return self.width if self.width is not None else (0.28 if portrait else 0.16)


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
    host_corner: HostCorner | None = None  # ajuste do canto do apresentador nesta cena (ADR 013)
    review_status: Status = Status.PENDING  # reflexo de review.json, escrito pelo código (§5)

    @model_validator(mode="after")
    def _narration_marks(self) -> Self:
        problems = narration_problems(self.narration)
        if problems:
            raise ValueError(f"{self.id}: " + "; ".join(problems))
        return self

    @model_validator(mode="after")
    def _visual_plan(self) -> Self:
        if not self.shots:
            if self.visual_need is None or self.search_query is None:
                raise ValueError(f"{self.id}: cena sem planos precisa de visual_need e search_query")
            return self
        spoken = strip_pauses(self.narration)  # âncoras e frases da tela: texto sem as marcas de pausa
        cursor, positions = 0, []
        for shot in self.shots:
            position = spoken.find(shot.anchor, cursor)
            if position < 0:
                raise ValueError(
                    f"{self.id}: âncora {shot.anchor!r} não aparece na narração depois do plano anterior"
                )
            positions.append(position)
            cursor = position + 1
        ends = [*positions[1:], len(spoken)]
        for shot, start, end in zip(self.shots, positions, ends, strict=True):
            if isinstance(shot, KeywordShot) and _fold(shot.text) not in _fold(spoken):
                raise ValueError(f"{self.id}: frase na tela {shot.text!r} não está na narração")
            if isinstance(shot, NetworkShot):
                step_positions(spoken, shot, start, end, scene_id=self.id)
        return self


def step_positions(narration: str, shot: NetworkShot, start: int, end: int, *, scene_id: str) -> list[int]:
    """Posição, na narração, da âncora de cada passo da rede: em ordem, dentro do trecho do plano
    ([`start`, `end`), até a âncora do plano seguinte)."""
    cursor, positions = start, []
    for step in shot.steps:
        position = narration.find(step.anchor, cursor)
        if position < 0 or position >= end:
            raise ValueError(
                f"{scene_id}: passo {step.anchor!r} da rede não aparece na narração, em ordem, "
                "dentro do trecho do plano"
            )
        positions.append(position)
        cursor = position + 1
    return positions


def effective_shots(scene: Scene) -> list[Shot]:
    """Planos da cena; a forma v1 vira um único plano de foto sobre a narração inteira."""
    if scene.shots:
        return list(scene.shots)
    return [
        PhotoShot(
            anchor=strip_pauses(scene.narration),
            visual_need=scene.visual_need,  # type: ignore[arg-type]  # garantido pelo validador da cena
            search_query=scene.search_query,  # type: ignore[arg-type]
            asset_id=scene.chosen_asset_id,
        )
    ]


# --- objetivo do vídeo (ADR 019) -----------------------------------------------------------------

ObjectiveKind = Literal["noticiar", "explicar", "opinar"]
# o que cada tipo exige a mais; um campo só existe quando o tipo dele está no vídeo
_OBJECTIVE_FIELDS: dict[str, tuple[str, ...]] = {
    "noticiar": ("event_date",),
    "explicar": ("question",),
    "opinar": ("thesis", "thesis_by"),
}


class Objective(Model):
    """O que o vídeo se propõe a fazer, declarado antes do roteiro (ADR 019).

    `kinds` traz de um a três tipos, na ordem em que aparecem no vídeo; o primeiro é o principal e manda na
    estrutura. Um vídeo pode só explicar, ou noticiar, explicar e opinar no fim: depende da pauta.

    - `noticiar`: conta um fato novo; `event_date` diz quando ele aconteceu.
    - `explicar`: responde a uma pergunta; `question` é a pergunta, e o vídeo a responde.
    - `opinar`: defende uma tese, dita como opinião; `thesis` e de quem ela é (`thesis_by`). A tese vem do
      dono, nunca do agente; os fatos que a apoiam seguem com fonte (§2.2)."""

    kinds: list[ObjectiveKind] = Field(min_length=1, max_length=3)
    promise: NonEmpty  # uma frase: o que a pessoa sabe, entende ou pensa depois de assistir
    event_date: date | None = None
    question: NonEmpty | None = None
    thesis: NonEmpty | None = None
    thesis_by: NonEmpty | None = None

    @property
    def main(self) -> ObjectiveKind:
        return self.kinds[0]

    @model_validator(mode="after")
    def _fields_match_kinds(self) -> Self:
        _unique(self.kinds, "tipos de objetivo")
        for kind, names in _OBJECTIVE_FIELDS.items():
            given = [name for name in names if getattr(self, name) is not None]
            if kind in self.kinds and len(given) < len(names):
                missing = ", ".join(name for name in names if name not in given)
                raise ValueError(f"objetivo {kind} precisa de {missing}")
            if kind not in self.kinds and given:
                raise ValueError(f"{', '.join(given)} só existe com o objetivo {kind}")
        if self.question is not None and not self.question.rstrip().endswith("?"):
            raise ValueError("question é uma pergunta: termina com '?'")
        return self


class ScenesManifest(Model):
    episode_id: EpisodeId
    language: Language
    objective: Objective | None = None  # o que o vídeo se propõe a fazer (ADR 019); sem ele, alerta
    scenes: list[Scene] = Field(min_length=1)
    host: HostSpec | None = None  # apresentador em janela flutuante, só no formato explicativo (ADR 013)
    orientation: Orientation = "landscape"  # `portrait`: 9:16, só com PORTRAIT_SHOT_KINDS (ADR 014)

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        return self

    @model_validator(mode="after")
    def _portrait_shots(self) -> Self:
        if self.orientation == "portrait":
            problems = [
                p
                for scene in self.scenes
                for p in portrait_problems(scene.id, [shot.kind for shot in effective_shots(scene)])
            ]
            if problems:
                raise ValueError("; ".join(problems))
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
    def _sixteen_by_nine_either_way(self) -> Self:
        if self.width * 9 != self.height * 16 and self.width * 16 != self.height * 9:
            raise ValueError(f"{self.width}x{self.height} não é 16:9 nem 9:16")
        return self

    @property
    def portrait(self) -> bool:
        return self.height > self.width

    @classmethod
    def for_orientation(cls, orientation: Orientation) -> VideoSpec:
        """1920×1080 em paisagem e 1080×1920 em retrato (ADR 014)."""
        return cls(width=1080, height=1920) if orientation == "portrait" else cls()


class EpisodeShot(Model):
    """Plano com tempo resolvido, relativo ao início da cena (ADR 008)."""

    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    spec: Shot
    media: RelPath | None = None  # arquivo do ativo, para foto e B-roll
    source: str | None = None  # "Fonte: …" do rodapé, derivado das claims e do sources.json (ADR 011)
    source_flag: str | None = None  # ressalva ao lado da fonte ("fonte interessada")
    steps_ms: list[int] = []  # só `network`: entrada de cada passo, relativa ao início do plano

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms

    @model_validator(mode="after")
    def _media_when_needed(self) -> Self:
        if (self.spec.kind in MEDIA_SHOT_KINDS) != (self.media is not None):
            raise ValueError(f"plano {self.spec.kind}: media é obrigatório para foto/B-roll e só para eles")
        expected = len(self.spec.steps) if isinstance(self.spec, NetworkShot) else 0
        if len(self.steps_ms) != expected:
            raise ValueError(
                f"plano {self.spec.kind}: {len(self.steps_ms)} tempos de passo, esperado {expected}"
            )
        outside = any(not 0 <= ms < self.duration_ms for ms in self.steps_ms)
        if self.steps_ms != sorted(self.steps_ms) or outside:
            raise ValueError("tempos dos passos da rede fora de ordem ou fora do plano")
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
    host_corner: HostCorner | None = None  # ajuste do canto do apresentador (ADR 013)

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
    host: HostSpec | None = None  # apresentador em janela flutuante (ADR 013); só `explainer`

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
        if self.host is not None and self.format != EpisodeFormat.EXPLAINER:
            raise ValueError("host (apresentador) só existe no formato explainer (ADR 013)")
        if self.video.portrait:
            if self.format != EpisodeFormat.EXPLAINER:
                raise ValueError("o perfil vertical (9:16) só existe no formato explainer (ADR 014)")
            problems = [
                p
                for scene in self.scenes
                for p in portrait_problems(scene.id, [shot.spec.kind for shot in scene.shots])
            ]
            if problems:
                raise ValueError("; ".join(problems))
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
