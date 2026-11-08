from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class Budget(_Model):
    max_api_spend_usd: float = Field(default=0, ge=0)
    allow_paid_api: bool = False
