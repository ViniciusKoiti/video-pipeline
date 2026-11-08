from __future__ import annotations

from app.settings.models.delivery_params import DeliveryParams


def _default_delivery() -> dict[str, DeliveryParams]:
    return {
        "hook": DeliveryParams(exaggeration=0.8, cfg_weight=0.3),
        "turn": DeliveryParams(exaggeration=0.7, cfg_weight=0.4),
        "invite": DeliveryParams(exaggeration=0.6, cfg_weight=0.4),
        "neutral": DeliveryParams(),
        "calm": DeliveryParams(exaggeration=0.4, cfg_weight=0.6),
    }
