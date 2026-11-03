"""Configuração: `config/providers.toml` + variáveis do CLAUDE.md §3 (ambiente > `.env` > toml).

Segredos só vêm do ambiente/`.env` (§2.7) e ficam em `SecretStr`, que não aparece em repr nem em logs.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.settings.constants.settings_constants import SettingsConstants
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

# Variável de ambiente -> caminho no dicionário de configuração.


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
    data: dict[str, Any] = tomllib.loads((root / SettingsConstants.CONFIG_FILE).read_text())
    if "secrets" in data:
        raise ValueError(f"{SettingsConstants.CONFIG_FILE} não pode ter segredos; use o .env (§2.7)")
    env = {**read_dotenv(root / ".env"), **(os.environ if environ is None else environ)}
    for var, keys in SettingsConstants.ENV_OVERRIDES.items():
        if env.get(var):
            target = data
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = env[var]
    data["secrets"] = {
        field: env[var] for var, field in SettingsConstants.SECRET_VARS.items() if env.get(var)
    }
    settings = Settings.model_validate(data)
    references = {
        language: {
            delivery: path.expanduser() if path.expanduser().is_absolute() else root / path
            for delivery, path in entries.items()
        }
        for language, entries in settings.chatterbox.references.items()
    }
    settings = settings.model_copy(
        update={"chatterbox": settings.chatterbox.model_copy(update={"references": references})}
    )
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
