from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class Limits(_Model):
    max_generated_images_per_episode: int = Field(default=12, ge=0)
    max_candidates_per_scene: int = Field(default=2, gt=0)
    max_cloud_requests_per_episode: int = Field(default=40, ge=0)
