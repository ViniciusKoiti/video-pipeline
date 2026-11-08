"""Constantes de settings; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping


class SettingsConstants:
    CONFIG_FILE: Final = Path("config/providers.toml")
    ENV_OVERRIDES: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
        {
            "POSTIZ_API_URL": ("postiz_api_url",),
            "OLLAMA_BASE_URL": ("ollama", "base_url"),
            "OLLAMA_MODEL": ("ollama", "model"),
            "WORKERS_AI_MODEL": ("workers_ai", "model"),
            "CHATTERBOX_PYTHON": ("chatterbox", "python"),
            "CHATTERBOX_REFERENCE": ("chatterbox", "reference"),
            "EARSHOT_PYTHON": ("earshot", "python"),
            "DATA_DIR": ("data_dir",),
            "MAX_API_SPEND_USD": ("budget", "max_api_spend_usd"),
            "ALLOW_PAID_API": ("budget", "allow_paid_api"),
            "MAX_GENERATED_IMAGES_PER_EPISODE": ("limits", "max_generated_images_per_episode"),
            "MAX_CANDIDATES_PER_SCENE": ("limits", "max_candidates_per_scene"),
            "MAX_CLOUD_REQUESTS_PER_EPISODE": ("limits", "max_cloud_requests_per_episode"),
        }
    )
    SECRET_VARS: Final[Mapping[str, str]] = MappingProxyType(
        {
            "POSTIZ_API_KEY": "postiz_api_key",
            "PEXELS_API_KEY": "pexels_api_key",
            "PIXABAY_API_KEY": "pixabay_api_key",
            "UNSPLASH_ACCESS_KEY": "unsplash_access_key",
            "CLOUDFLARE_ACCOUNT_ID": "cloudflare_account_id",
            "CLOUDFLARE_API_TOKEN": "cloudflare_api_token",
            "GROQ_API_KEY": "groq_api_key",
            "GEMINI_API_KEY": "gemini_api_key",
        }
    )
