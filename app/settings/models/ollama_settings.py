from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class OllamaSettings(_Model):
    base_url: str
    model: str
    num_thread: int = Field(default=8, gt=0)
