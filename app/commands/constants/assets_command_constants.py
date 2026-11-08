"""Constantes do comando `vp assets`; dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from app.pipeline.models.intake_action import IntakeAction


class AssetsCommandConstants:
    # o que o `take` diz de cada resultado da entrada de um ativo
    LABELS: Final = MappingProxyType(
        {
            IntakeAction.DOWNLOADED: "baixado",
            IntakeAction.REPAIRED: "mídia refeita (a anterior não batia com o sha256)",
            IntakeAction.SCENE_ADDED: "já baixado; cena acrescentada",
            IntakeAction.UNCHANGED: "já baixado; nada a fazer",
            IntakeAction.APPROVED_UNTOUCHED: "aprovado; não alterado (use o asset_id no scenes.json)",
        }
    )
