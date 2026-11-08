"""Contratos de dados dos manifestos (CLAUDE.md §6, ADR 007).

Os modelos validam o que dá para garantir olhando um arquivo só. Regras que cruzam arquivos
(claim → sources.json, visual_need → ativo) ficam nas funções do fim do módulo.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_factual_shot import _FactualShot as _FactualShot
from app.pipeline.models._schemas_from_to import _FromTo as _FromTo
from app.pipeline.models._schemas_shot import _Shot as _Shot
from app.pipeline.models._schemas_step import _Step as _Step
from app.pipeline.models._schemas_types import AssetId as AssetId
from app.pipeline.models._schemas_types import Count as Count
from app.pipeline.models._schemas_types import Delivery as Delivery
from app.pipeline.models._schemas_types import EpisodeId as EpisodeId
from app.pipeline.models._schemas_types import ExcerptId as ExcerptId
from app.pipeline.models._schemas_types import FactId as FactId
from app.pipeline.models._schemas_types import FunnelStage as FunnelStage
from app.pipeline.models._schemas_types import HostCorner as HostCorner
from app.pipeline.models._schemas_types import HostVariant as HostVariant
from app.pipeline.models._schemas_types import HttpUrl as HttpUrl
from app.pipeline.models._schemas_types import Language as Language
from app.pipeline.models._schemas_types import Motion as Motion
from app.pipeline.models._schemas_types import MusicLevel as MusicLevel
from app.pipeline.models._schemas_types import MusicRole as MusicRole
from app.pipeline.models._schemas_types import NodeId as NodeId
from app.pipeline.models._schemas_types import NonEmpty as NonEmpty
from app.pipeline.models._schemas_types import ObjectiveKind as ObjectiveKind
from app.pipeline.models._schemas_types import Operator as Operator
from app.pipeline.models._schemas_types import Orientation as Orientation
from app.pipeline.models._schemas_types import Percent as Percent
from app.pipeline.models._schemas_types import Platform as Platform
from app.pipeline.models._schemas_types import PublicationFormat as PublicationFormat
from app.pipeline.models._schemas_types import RegionCode as RegionCode
from app.pipeline.models._schemas_types import RelPath as RelPath
from app.pipeline.models._schemas_types import RequestKind as RequestKind
from app.pipeline.models._schemas_types import SceneId as SceneId
from app.pipeline.models._schemas_types import Sha256 as Sha256
from app.pipeline.models._schemas_types import Slug as Slug
from app.pipeline.models._schemas_types import SourceId as SourceId
from app.pipeline.models._schemas_types import Window as Window
from app.pipeline.models._schemas_types import _fold as _fold
from app.pipeline.models._schemas_types import _later_steps_anchored as _later_steps_anchored
from app.pipeline.models._schemas_types import _relative_path as _relative_path
from app.pipeline.models._schemas_types import _unique as _unique
from app.pipeline.models._schemas_types import portrait_problems as portrait_problems
from app.pipeline.models._schemas_types import reels_shot_problems as reels_shot_problems
from app.pipeline.models._schemas_types import screen_parts as screen_parts
from app.pipeline.models._schemas_value_effective_shots import effective_shots as effective_shots
from app.pipeline.models._schemas_value_shot import Shot as Shot
from app.pipeline.models._schemas_value_step_anchors import step_anchors as step_anchors
from app.pipeline.models._schemas_value_step_positions import step_positions as step_positions
from app.pipeline.models.asset import Asset as Asset
from app.pipeline.models.audience_request import AudienceRequest as AudienceRequest
from app.pipeline.models.broll_shot import BrollShot as BrollShot
from app.pipeline.models.calculation_result import CalculationResult as CalculationResult
from app.pipeline.models.calculation_shot import CalculationShot as CalculationShot
from app.pipeline.models.calculation_term import CalculationTerm as CalculationTerm
from app.pipeline.models.chart_point import ChartPoint as ChartPoint
from app.pipeline.models.chart_shot import ChartShot as ChartShot
from app.pipeline.models.check_entry import CheckEntry as CheckEntry
from app.pipeline.models.check_log import CheckLog as CheckLog
from app.pipeline.models.check_verdict import CheckVerdict as CheckVerdict
from app.pipeline.models.claim import Claim as Claim
from app.pipeline.models.compare_shot import CompareShot as CompareShot
from app.pipeline.models.compare_side import CompareSide as CompareSide
from app.pipeline.models.crop import Crop as Crop
from app.pipeline.models.decision import Decision as Decision
from app.pipeline.models.document_header import DocumentHeader as DocumentHeader
from app.pipeline.models.end_card_shot import EndCardShot as EndCardShot
from app.pipeline.models.episode_format import EpisodeFormat as EpisodeFormat
from app.pipeline.models.episode_manifest import EpisodeManifest as EpisodeManifest
from app.pipeline.models.episode_music import EpisodeMusic as EpisodeMusic
from app.pipeline.models.episode_scene import EpisodeScene as EpisodeScene
from app.pipeline.models.episode_shot import EpisodeShot as EpisodeShot
from app.pipeline.models.evidence import Evidence as Evidence
from app.pipeline.models.fact import Fact as Fact
from app.pipeline.models.fact_kind import FactKind as FactKind
from app.pipeline.models.facts_manifest import FactsManifest as FactsManifest
from app.pipeline.models.family_tree_shot import FamilyTreeShot as FamilyTreeShot
from app.pipeline.models.funnel import Funnel as Funnel
from app.pipeline.models.generation import Generation as Generation
from app.pipeline.models.hook_shot import HookShot as HookShot
from app.pipeline.models.host_identity import HostIdentity as HostIdentity
from app.pipeline.models.host_spec import HostSpec as HostSpec
from app.pipeline.models.keyword_shot import KeywordShot as KeywordShot
from app.pipeline.models.lower_third_shot import LowerThirdShot as LowerThirdShot
from app.pipeline.models.map_shot import MapShot as MapShot
from app.pipeline.models.metrics_reading import MetricsReading as MetricsReading
from app.pipeline.models.model import Model as Model
from app.pipeline.models.music_anchor import MusicAnchor as MusicAnchor
from app.pipeline.models.music_catalog import MusicCatalog as MusicCatalog
from app.pipeline.models.music_cue import MusicCue as MusicCue
from app.pipeline.models.music_plan import MusicPlan as MusicPlan
from app.pipeline.models.music_track import MusicTrack as MusicTrack
from app.pipeline.models.network_edge import NetworkEdge as NetworkEdge
from app.pipeline.models.network_node import NetworkNode as NetworkNode
from app.pipeline.models.network_shot import NetworkShot as NetworkShot
from app.pipeline.models.network_step import NetworkStep as NetworkStep
from app.pipeline.models.number_shot import NumberShot as NumberShot
from app.pipeline.models.objective import Objective as Objective
from app.pipeline.models.person import Person as Person
from app.pipeline.models.photo_shot import PhotoShot as PhotoShot
from app.pipeline.models.place import Place as Place
from app.pipeline.models.provider import Provider as Provider
from app.pipeline.models.publication_metrics import PublicationMetrics as PublicationMetrics
from app.pipeline.models.quote_shot import QuoteShot as QuoteShot
from app.pipeline.models.receipt_item import ReceiptItem as ReceiptItem
from app.pipeline.models.receipt_shot import ReceiptShot as ReceiptShot
from app.pipeline.models.receipt_total import ReceiptTotal as ReceiptTotal
from app.pipeline.models.review_entry import ReviewEntry as ReviewEntry
from app.pipeline.models.review_log import ReviewLog as ReviewLog
from app.pipeline.models.route import Route as Route
from app.pipeline.models.scene import Scene as Scene
from app.pipeline.models.scenes_manifest import ScenesManifest as ScenesManifest
from app.pipeline.models.series import Series as Series
from app.pipeline.models.source import Source as Source
from app.pipeline.models.source_kind import SourceKind as SourceKind
from app.pipeline.models.sources_manifest import SourcesManifest as SourcesManifest
from app.pipeline.models.stamp_shot import StampShot as StampShot
from app.pipeline.models.status import Status as Status
from app.pipeline.models.step import Step as Step
from app.pipeline.models.timeline_event import TimelineEvent as TimelineEvent
from app.pipeline.models.timeline_shot import TimelineShot as TimelineShot
from app.pipeline.models.traffic_source import TrafficSource as TrafficSource
from app.pipeline.models.video_spec import VideoSpec as VideoSpec
from app.pipeline.models.visual_need import VisualNeed as VisualNeed

# --- Identificadores e tipos básicos -----------------------------------------------------------


# --- sources.json --------------------------------------------------------------------------------


# --- scenes.json ---------------------------------------------------------------------------------


# --- Planos (ADR 008) ----------------------------------------------------------------------------


# Ano ("1927") ou data ISO ("1927-03" ou "1927-03-12"): posição num eixo de tempo (ADR 011).
# Número como aparece na tela ("R$ 47,6 bi", "1.500", "78%"): prefixo, dígitos e sufixo (regra do `number`).
# Separador de milhar e de decimal de cada idioma: o mesmo texto vale outro número em outro idioma, então o
# valor da tela segue a convenção do idioma do episódio (ADR 011, emenda "número por idioma").


def screen_number(value: str, language: Language = "pt-BR") -> tuple[str, float, str] | None:
    """(prefixo, número, sufixo) de um valor escrito na convenção do idioma ("1.500,5" em pt-BR, "1,500.5" em
    en); None se não houver número reconhecível."""
    parts = screen_parts(value)
    if parts is None:
        return None
    group, decimal = SchemasConstants.NUMBER_SEPARATORS[language]
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
    group, decimal = SchemasConstants.NUMBER_SEPARATORS[language]
    group_re, decimal_re = re.escape(group), re.escape(decimal)
    if re.fullmatch(rf"(\d{{1,3}}({group_re}\d{{3}})+|\d+)({decimal_re}\d+)?", parts[1]):
        return None
    return f"{value!r} não segue a convenção de {language} (ex.: 1{group}500{decimal}5)"


# País (ISO 3166-1 alfa-3, "BRA") ou estado (ISO 3166-2, "BR-SP").


# --- Planos editoriais (ADR 011) -----------------------------------------------------------------


# --- Planos de Reels: conta, gancho, nota e cartão final (ADR 028) ---------------------------------


# Planos dos Reels (ADR 028): só no vertical até o vídeo-régua em 16:9.

# Desenhados por cima da foto ou do B-roll anterior da mesma cena; os outros gráficos ficam em tela cheia
# (ADR 011, decisão 5).


# Planos com layout em retrato; rede, mapa, linha do tempo, árvore e documento dependem de canvas largo.


# --- Apresentador em janela flutuante (ADR 013) --------------------------------------------------

# sentido horário


# Entrega da fala (ADR 022), do mais ao menos enfático: `hook` abertura e chamado; `turn` a virada ("mas…");
# `invite` a pergunta final; `neutral` explicação; `calm` a conta, pausada e clara.


# --- objetivo do vídeo (ADR 019) -----------------------------------------------------------------

# o que cada tipo exige a mais; um campo só existe quando o tipo dele está no vídeo


# --- estágio do funil (ADR 026) ------------------------------------------------------------------


# --- facts.json (ADR 009) ------------------------------------------------------------------------


# --- assets/<id>.json ----------------------------------------------------------------------------


# Lista fechada de licenças que podem chegar ao render (ADR 007). Qualquer outra — inclusive
# CC-BY-SA (compartilhamento pela mesma licença alcançaria o vídeo) e NC (canal monetizado) —
# mantém o ativo fora de approved; a decisão vira revisão humana.
# Banco de imagem: a licença do próprio banco, ou CC0-1.0 na parte do acervo que a tem.
# Quadro parado de obra citada para crítica, só de material oficial público (emenda de citação, ADR 007).
# Música da YouTube Audio Library sem atribuição exigida (emenda de música, ADR 007 e ADR 030): vale só em
# vídeo publicado no YouTube; a faixa CC dela entra com a licença CC-BY da própria faixa.


# --- review.json ---------------------------------------------------------------------------------


# --- Trilha sonora (ADR 030) ---------------------------------------------------------------------

# Ganho sobre o arquivo da faixa, antes do ducking: a voz fica sempre acima da trilha.

# --- episode.json (contrato do render) ----------------------------------------------------------


# --- Métricas de publicação (§12; contrato D6 de 2026-10-14, emenda da ADR 007 de 2026-10-23) ----


# --- Verificações entre arquivos -----------------------------------------------------------------


def unknown_source_refs(scenes: ScenesManifest, sources: SourcesManifest) -> list[str]:
    """§2.2: claims e trechos que citam fontes ausentes de sources.json."""
    known = {s.id for s in sources.sources}
    problems = []
    for scene in scenes.scenes:
        for claim in scene.claims + [c for shot in scene.shots for c in shot.claims]:
            refs = claim.source_ids + [SchemasConstants._EXCERPT_RE.sub(r"\1", e) for e in claim.excerpt_ids]
            problems += [f"{scene.id}: fonte {r} não está em sources.json" for r in refs if r not in known]
    return sorted(set(problems))


# §2.4: stock (os bancos de STOCK_LICENSES) e imagem gerada são ilustração, nunca registro do fato.


def citation_violations(planned: Sequence[tuple[str, Shot, float]], assets: dict[str, Asset]) -> list[str]:
    """Citações (licença Citacao) fora das regras da emenda: quadro parado só em foto, no máximo
    MAX_CITATION_FRAMES por vídeo e MAX_CITATION_MS na tela cada; clipe só em B-roll e sem teto numérico
    (emenda de 2026-11-03). `planned`: (cena, plano, duração em ms)."""
    problems, frames = [], 0
    for scene_id, shot, ms in planned:
        if not isinstance(shot, PhotoShot | BrollShot) or shot.asset_id is None:
            continue
        asset = assets.get(shot.asset_id)
        if asset is None or asset.license_id != SchemasConstants.CITATION_LICENSE:
            continue
        clip, motion = asset.media == "clip", isinstance(shot, BrollShot)
        if clip != motion:
            problems.append(
                f"{scene_id}: citação {shot.asset_id} é "
                + ("clipe e só vai em B-roll" if clip else "quadro parado e não vai em B-roll")
            )
        elif not clip:
            frames += 1
            if ms > SchemasConstants.MAX_CITATION_MS:
                problems.append(
                    f"{scene_id}: citação {shot.asset_id} com ~{ms / 1000:.1f} s na tela (máximo "
                    f"{SchemasConstants.MAX_CITATION_MS / 1000:.0f} s)"
                )
    if frames > SchemasConstants.MAX_CITATION_FRAMES:
        problems.append(f"{frames} quadros citados no vídeo (máximo {SchemasConstants.MAX_CITATION_FRAMES})")
    return problems


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
            elif (
                shot.visual_need is VisualNeed.HISTORICAL_EXACT
                and asset.provider in SchemasConstants._NOT_A_RECORD
            ):
                problems.append(f"{scene.id}: historical_exact não pode usar {asset.provider.value}")
    return problems
