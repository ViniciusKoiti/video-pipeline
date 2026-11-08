from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.constants.sources_policy_constants import SourcesPolicyConstants
from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import (
    EpisodeId,
    Language,
    Orientation,
    SourcesPolicy,
    _unique,
    portrait_problems,
    reels_shot_problems,
)
from app.pipeline.models._schemas_value_effective_shots import effective_shots
from app.pipeline.models.end_card_shot import EndCardShot
from app.pipeline.models.funnel import Funnel
from app.pipeline.models.host_spec import HostSpec
from app.pipeline.models.model import Model
from app.pipeline.models.objective import Objective
from app.pipeline.models.scene import Scene
from app.pipeline.models.series import Series


class ScenesManifest(Model):
    episode_id: EpisodeId
    language: Language
    objective: Objective | None = None  # o que o vídeo se propõe a fazer (ADR 019); sem ele, alerta
    # título provisório da pauta (ADR 031, emenda de 2026-10-23): o `vp check` compara o tamanho com o molde e
    # avisa quando a fala demora a dizer o assunto do título; o título publicado é decisão do gate 4
    title: str | None = Field(default=None, min_length=1, max_length=100)
    funnel: Funnel | None = None  # estágio do funil e a chamada final (ADR 026); sem ele, alerta
    series: Series | None = None  # série do vídeo, no selo do cartão final (ADR 028)
    scenes: list[Scene] = Field(min_length=1)
    host: HostSpec | None = None  # apresentador em janela flutuante, só no formato explicativo (ADR 013)
    orientation: Orientation = "landscape"  # `portrait`: 9:16, só com PORTRAIT_SHOT_KINDS (ADR 014)
    # regime de fontes do vídeo, decisão do roteirista (ADR 056): `documental` (fichas, claims e rodapé),
    # `ensaio` (fichas; claim no que vai à tela; fonte só na descrição) ou `entretenimento` (sem claim)
    sources_policy: SourcesPolicy = "documental"

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        return self

    @model_validator(mode="after")
    def _screen_facts_have_claims(self) -> Self:
        """Número, data, citação, cargo ou gráfico na tela é afirmação: fora do regime `entretenimento`, o
        plano precisa de claim (ADR 008 e 056)."""
        if self.sources_policy not in SourcesPolicyConstants.CLAIMS_ON_SCREEN:
            return self
        missing = [
            f"{scene.id}: {shot.kind} ({shot.anchor!r}) na tela sem claim"
            for scene in self.scenes
            for shot in effective_shots(scene)
            if isinstance(shot, _FactualShot) and not shot.claims
        ]
        if missing:
            raise ValueError("; ".join(missing) + f" (regime {self.sources_policy}, ADR 056)")
        return self

    @model_validator(mode="after")
    def _reels_shots(self) -> Self:
        kinds = [(scene.id, [shot.kind for shot in effective_shots(scene)]) for scene in self.scenes]
        problems = reels_shot_problems(kinds, portrait=self.orientation == "portrait")
        end_cards = [shot for scene in self.scenes for shot in scene.shots if isinstance(shot, EndCardShot)]
        if end_cards and self.funnel is not None and self.funnel.stage == "fundo":
            problems.append("cartão final ainda sem a chamada do fundo do funil (ADR 028, decisão 4)")
        series = self.series
        last_part = series is None or series.part == series.total
        if any(card.variant == "next" for card in end_cards) and last_part:
            problems.append("cartão final next pede a série com uma parte depois desta (series)")
        if problems:
            raise ValueError("; ".join(problems))
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
