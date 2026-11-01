from __future__ import annotations

from enum import StrEnum


class IntakeAction(StrEnum):
    DOWNLOADED = "downloaded"  # ativo novo: mídia baixada e JSON criado
    REPAIRED = "repaired"  # ativo não aprovado com a mídia ausente ou diferente do sha256: baixado de novo
    SCENE_ADDED = "scene_added"  # já baixado e íntegro: só a cena entrou em `used_in_scenes`
    UNCHANGED = "unchanged"  # já baixado e a cena já estava: nada foi escrito
    APPROVED_UNTOUCHED = "approved_untouched"  # aprovado: JSON e mídia ficam como estão (§2.6)
