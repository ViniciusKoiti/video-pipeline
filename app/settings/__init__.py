"""Configuração: `config/providers.toml` + variáveis do CLAUDE.md §3 (ambiente > `.env` > toml).

Segredos só vêm do ambiente/`.env` (§2.7) e ficam em `SecretStr`, que não aparece em repr nem em logs.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.settings.models._settings_model import _Model as _Model
from app.settings.models._settings_value_default_delivery import _default_delivery as _default_delivery
from app.settings.models.budget import Budget as Budget
from app.settings.models.chatterbox_modal_settings import ChatterboxModalSettings as ChatterboxModalSettings
from app.settings.models.chatterbox_settings import ChatterboxSettings as ChatterboxSettings
from app.settings.models.delivery_params import DeliveryParams as DeliveryParams
from app.settings.models.earshot_settings import EarshotSettings as EarshotSettings
from app.settings.models.ffmpeg_settings import FfmpegSettings as FfmpegSettings
from app.settings.models.gemini_tts_settings import GeminiTTSSettings as GeminiTTSSettings
from app.settings.models.groq_whisper_settings import GroqWhisperSettings as GroqWhisperSettings
from app.settings.models.kokoro_settings import KokoroSettings as KokoroSettings
from app.settings.models.limits import Limits as Limits
from app.settings.models.ollama_settings import OllamaSettings as OllamaSettings
from app.settings.models.provider_choice import ProviderChoice as ProviderChoice
from app.settings.models.secrets import Secrets as Secrets
from app.settings.models.settings import Settings as Settings
from app.settings.models.workers_ai_settings import WorkersAISettings as WorkersAISettings

CONFIG_FILE = Path("config/providers.toml")


# Variável de ambiente -> caminho no dicionário de configuração.
ENV_OVERRIDES: dict[str, tuple[str, ...]] = {
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
SECRET_VARS: dict[str, str] = {
    "POSTIZ_API_KEY": "postiz_api_key",
    "PEXELS_API_KEY": "pexels_api_key",
    "PIXABAY_API_KEY": "pixabay_api_key",
    "UNSPLASH_ACCESS_KEY": "unsplash_access_key",
    "CLOUDFLARE_ACCOUNT_ID": "cloudflare_account_id",
    "CLOUDFLARE_API_TOKEN": "cloudflare_api_token",
    "GROQ_API_KEY": "groq_api_key",
    "GEMINI_API_KEY": "gemini_api_key",
}


def read_dotenv(path: Path) -> dict[str, str]:
    """Lê KEY=VALUE sem executar nada; ignora comentários e linhas vazias."""
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return values


def load_settings(root: Path, environ: Mapping[str, str] | None = None) -> Settings:
    data: dict[str, Any] = tomllib.loads((root / CONFIG_FILE).read_text())
    if "secrets" in data:
        raise ValueError(f"{CONFIG_FILE} não pode ter segredos; use o .env (§2.7)")
    env = {**read_dotenv(root / ".env"), **(os.environ if environ is None else environ)}
    for var, keys in ENV_OVERRIDES.items():
        if env.get(var):
            target = data
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = env[var]
    data["secrets"] = {field: env[var] for var, field in SECRET_VARS.items() if env.get(var)}
    settings = Settings.model_validate(data)
    if not settings.data_dir.is_absolute():
        settings = settings.model_copy(update={"data_dir": root / settings.data_dir})
    return settings


def speech_chars_per_second(settings: Settings) -> float:
    """Ritmo da voz final: estima a duração das cenas antes da voz real (§9); é o tempo do vídeo publicado."""
    rates = {
        "kokoro": settings.kokoro.chars_per_second,
        "gemini": settings.gemini_tts.chars_per_second,
        "chatterbox": settings.chatterbox.chars_per_second,
        "chatterbox_modal": settings.chatterbox.chars_per_second,  # a mesma voz (ADR 024)
    }
    voice = settings.providers.tts_final or settings.providers.tts
    return rates.get(voice, settings.kokoro.chars_per_second)
