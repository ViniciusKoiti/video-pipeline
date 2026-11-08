"""Regime de fontes de um roteiro (ADR 056).

O roteirista declara em `scenes.json` se o vídeo é `documental`, `ensaio` ou `entretenimento`, e o código
obedece em vez de presumir: o schema exige claim no que vai à tela fora do `entretenimento`
(`ScenesManifest`), o rodapé de fonte só sai no `documental`, e o alerta de frase afirmativa sem claim
só vale no `documental`. A exceção de pessoa viva e empresa ativa (fato sobre elas sempre com ficha e
fonte) é regra do roteirista e do gate 2: o código não sabe quem está vivo, por isso só lembra dela
quando regime e objetivo não combinam.
"""

from __future__ import annotations

from app.pipeline.constants.sources_policy_constants import SourcesPolicyConstants as Constants
from app.pipeline.models._schemas_types import SourcesPolicy
from app.pipeline.molde import claimless_statements
from app.pipeline.ports import ManifestInvalid, ManifestNotFound, ManifestStore
from app.pipeline.schemas import ScenesManifest, SourcesManifest


def policy_summary(scenes: ScenesManifest) -> str:
    return f"regime de fontes: {scenes.sources_policy} ({Constants.DESCRIPTIONS[scenes.sources_policy]})"


def policy_warnings(scenes: ScenesManifest) -> list[str]:
    """Alertas que dependem do regime: frase afirmativa sem claim só no `documental`; `entretenimento` com
    objetivo `noticiar` lembra a exceção de pessoa viva e empresa ativa."""
    if scenes.sources_policy == "documental":
        return claimless_statements(scenes)
    objective = scenes.objective
    news = objective is not None and "noticiar" in objective.kinds
    if scenes.sources_policy == "entretenimento" and news:
        return [
            "regime entretenimento com objetivo noticiar: fato sobre pessoa viva ou empresa ativa exige "
            "ficha e fonte (ADR 056)"
        ]
    return []


def footer_sources(scenes: ScenesManifest, sources: SourcesManifest | None) -> SourcesManifest | None:
    """As fontes que vão ao rodapé dos planos (ADR 011): só no regime `documental`; nos outros, a fonte fica
    na descrição e o rodapé sai vazio."""
    return sources if scenes.sources_policy in Constants.FOOTER else None


def declared_policy(store: ManifestStore, episode_id: str) -> SourcesPolicy | None:
    """O regime declarado no `scenes.json` do episódio; nada quando o arquivo falta ou está fora do contrato
    (o `vp check` é quem acusa isso)."""
    try:
        return store.read(episode_id, "scenes.json", ScenesManifest).sources_policy
    except (ManifestNotFound, ManifestInvalid):
        return None
