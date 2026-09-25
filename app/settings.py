"""Configuração: `config/providers.toml` + variáveis do CLAUDE.md §3 (ambiente > `.env` > toml).

Segredos só vêm do ambiente/`.env` (§2.7) e ficam em `SecretStr`, que não aparece em repr nem em logs.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr

CONFIG_FILE = Path("config/providers.toml")


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderChoice(_Model):
    text: str
    tts: str
    image_gen: str
    archives: list[str] = Field(min_length=1)  # ordem da cascata (§8)
    aligner: str
    render: str
    store: str
    review: str


class OllamaSettings(_Model):
    base_url: str
    model: str
    num_thread: int = Field(default=8, gt=0)


class KokoroSettings(_Model):
    voice: str
    num_threads: int = Field(default=8, gt=0)


class WorkersAISettings(_Model):
    model: str


class Limits(_Model):
    max_generated_images_per_episode: int = Field(default=12, ge=0)
    max_candidates_per_scene: int = Field(default=2, gt=0)
    max_cloud_requests_per_episode: int = Field(default=40, ge=0)


class Budget(_Model):
    max_api_spend_usd: float = Field(default=0, ge=0)
    allow_paid_api: bool = False


class Secrets(_Model):
    pexels_api_key: SecretStr | None = None
    cloudflare_account_id: SecretStr | None = None
    cloudflare_api_token: SecretStr | None = None
    groq_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None


class Settings(_Model):
    providers: ProviderChoice
    ollama: OllamaSettings
    kokoro: KokoroSettings
    workers_ai: WorkersAISettings
    limits: Limits = Limits()
    budget: Budget = Budget()
    data_dir: Path = Path("data")
    secrets: Secrets = Secrets()


# Variável de ambiente -> caminho no dicionário de configuração.
ENV_OVERRIDES: dict[str, tuple[str, ...]] = {
    "OLLAMA_BASE_URL": ("ollama", "base_url"),
    "OLLAMA_MODEL": ("ollama", "model"),
    "WORKERS_AI_MODEL": ("workers_ai", "model"),
    "DATA_DIR": ("data_dir",),
    "MAX_API_SPEND_USD": ("budget", "max_api_spend_usd"),
    "ALLOW_PAID_API": ("budget", "allow_paid_api"),
    "MAX_GENERATED_IMAGES_PER_EPISODE": ("limits", "max_generated_images_per_episode"),
    "MAX_CANDIDATES_PER_SCENE": ("limits", "max_candidates_per_scene"),
    "MAX_CLOUD_REQUESTS_PER_EPISODE": ("limits", "max_cloud_requests_per_episode"),
}
SECRET_VARS: dict[str, str] = {
    "PEXELS_API_KEY": "pexels_api_key",
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
