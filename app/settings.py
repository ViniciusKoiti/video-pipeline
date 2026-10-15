"""Configuração: `config/providers.toml` + variáveis do CLAUDE.md §3 (ambiente > `.env` > toml).

Segredos só vêm do ambiente/`.env` (§2.7) e ficam em `SecretStr`, que não aparece em repr nem em logs.
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.pipeline.schemas import EpisodeFormat

CONFIG_FILE = Path("config/providers.toml")


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderChoice(_Model):
    text: str
    tts: str  # voz dos rascunhos e das prévias de revisão
    tts_final: str | None = None  # voz do vídeo final e do vídeo-régua (ADR 012); None = a mesma de `tts`
    image_gen: str
    archives: list[str] = Field(min_length=1)  # ordem da cascata (§8)
    aligner: str
    word_aligner: str = "groq"  # palavras com tempo para a legenda palavra a palavra (ADR 023)
    render: dict[EpisodeFormat, str]  # motor por formato do episódio (ADR 001)
    store: str
    review: str

    @field_validator("render")
    @classmethod
    def _documentary_has_engine(cls, value: dict[EpisodeFormat, str]) -> dict[EpisodeFormat, str]:
        if EpisodeFormat.ARCHIVAL_DOCUMENTARY not in value:
            raise ValueError("render precisa de um motor para archival_documentary")
        return value


class OllamaSettings(_Model):
    base_url: str
    model: str
    num_thread: int = Field(default=8, gt=0)


class KokoroSettings(_Model):
    voices: dict[str, str] = Field(min_length=1)  # idioma -> voz (ADR 008)
    num_threads: int = Field(default=8, gt=0)
    chars_per_second: float = Field(default=15.0, gt=0)  # ritmo da voz, para estimar a cena antes do WAV
    pause_ms: int = Field(default=300, ge=0)  # silêncio no lugar de cada `<short pause>` (ADR 015)


class GeminiTTSSettings(_Model):
    """Gemini TTS na camada gratuita (ADR 012); a chave fica no `.env` (GEMINI_API_KEY)."""

    model: str = "gemini-3.8-flash-tts"
    voices: dict[str, str] = Field(default_factory=lambda: {"pt-BR": "Charon"})  # idioma -> voz
    styles: dict[str, str] = Field(default_factory=dict)  # idioma -> direção de fala (speech_metadata.style)
    requests_per_minute: int = Field(default=3, gt=0)  # limite da camada gratuita
    chars_per_second: float = Field(default=13.0, gt=0)


class GroqWhisperSettings(_Model):
    """Whisper da Groq na camada gratuita, só para o tempo das palavras da legenda (ADR 023)."""

    model: str = "whisper-large-v3-turbo"
    timeout_s: float = Field(default=120.0, gt=0)


class DeliveryParams(_Model):
    """Controles de expressividade do Chatterbox para uma entrega (ADR 022)."""

    exaggeration: float = Field(default=0.5, ge=0, le=2)  # ênfase; o modelo usa 0,5 por padrão
    cfg_weight: float = Field(default=0.5, ge=0, le=1)  # quanto menor, mais vivo e rápido


def _default_delivery() -> dict[str, DeliveryParams]:
    return {
        "hook": DeliveryParams(exaggeration=0.8, cfg_weight=0.3),
        "turn": DeliveryParams(exaggeration=0.7, cfg_weight=0.4),
        "invite": DeliveryParams(exaggeration=0.6, cfg_weight=0.4),
        "neutral": DeliveryParams(),
        "calm": DeliveryParams(exaggeration=0.4, cfg_weight=0.6),
    }


class ChatterboxSettings(_Model):
    """Voz clonada local (ADR 016, proposta). O ambiente do modelo e a gravação de referência vêm do .env."""

    python: Path | None = None  # CHATTERBOX_PYTHON: o Python do ambiente em que o modelo está instalado
    reference: Path | None = None  # CHATTERBOX_REFERENCE: gravação da voz a clonar (dado pessoal)
    model: str = "v3"
    language_ids: dict[str, str] = Field(default_factory=lambda: {"pt-BR": "pt", "en": "en"})
    num_threads: int = Field(default=12, gt=0)
    chars_per_second: float = Field(default=14.0, gt=0)
    pause_ms: int = Field(default=400, ge=0)  # silêncio no lugar de cada `<short pause>` (ADR 015)
    delivery: dict[str, DeliveryParams] = Field(default_factory=_default_delivery)  # por entrega (ADR 022)


class ChatterboxModalSettings(_Model):
    """A mesma voz clonada numa GPU do Modal (ADR 024). Modelo, idioma, pausa, entrega e gravação de
    referência vêm de `[chatterbox]`; aqui fica só o que é da nuvem."""

    python: Path = Path("~/.local/share/uv/tools/modal/bin/python")  # o Python da CLI do Modal
    app: str = "voz-dono"  # nome publicado por `modal deploy deploy/modal_chatterbox.py`
    reference_name: str = "referencia.wav"  # a gravação no volume privado `voz-dono-referencia`


class WorkersAISettings(_Model):
    model: str


class FfmpegSettings(_Model):
    crf: int = Field(default=20, ge=0, le=51)
    preset_final: str = "medium"
    preset_preview: str = "veryfast"
    zoom: float = Field(default=0.06, ge=0, le=0.3)
    fade_s: float = Field(default=0.3, ge=0)
    burn_captions_preview: bool = True
    burn_captions_final: bool = False  # captions.srt sobe separado no YouTube


class Limits(_Model):
    max_generated_images_per_episode: int = Field(default=12, ge=0)
    max_candidates_per_scene: int = Field(default=2, gt=0)
    max_cloud_requests_per_episode: int = Field(default=40, ge=0)


class Budget(_Model):
    max_api_spend_usd: float = Field(default=0, ge=0)
    allow_paid_api: bool = False


class Secrets(_Model):
    pexels_api_key: SecretStr | None = None
    pixabay_api_key: SecretStr | None = None
    unsplash_access_key: SecretStr | None = None
    cloudflare_account_id: SecretStr | None = None
    cloudflare_api_token: SecretStr | None = None
    groq_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    postiz_api_key: SecretStr | None = None


class Settings(_Model):
    providers: ProviderChoice
    ollama: OllamaSettings
    kokoro: KokoroSettings
    gemini_tts: GeminiTTSSettings = GeminiTTSSettings()
    chatterbox: ChatterboxSettings = ChatterboxSettings()
    chatterbox_modal: ChatterboxModalSettings = ChatterboxModalSettings()
    groq_whisper: GroqWhisperSettings = GroqWhisperSettings()
    workers_ai: WorkersAISettings
    ffmpeg: FfmpegSettings = FfmpegSettings()
    limits: Limits = Limits()
    budget: Budget = Budget()
    data_dir: Path = Path("data")
    secrets: Secrets = Secrets()
    postiz_api_url: str | None = None


# Variável de ambiente -> caminho no dicionário de configuração.
ENV_OVERRIDES: dict[str, tuple[str, ...]] = {
    "POSTIZ_API_URL": ("postiz_api_url",),
    "OLLAMA_BASE_URL": ("ollama", "base_url"),
    "OLLAMA_MODEL": ("ollama", "model"),
    "WORKERS_AI_MODEL": ("workers_ai", "model"),
    "CHATTERBOX_PYTHON": ("chatterbox", "python"),
    "CHATTERBOX_REFERENCE": ("chatterbox", "reference"),
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
