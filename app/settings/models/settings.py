from __future__ import annotations

from pathlib import Path

from app.settings.models._settings_model import _Model
from app.settings.models.budget import Budget
from app.settings.models.chatterbox_modal_settings import ChatterboxModalSettings
from app.settings.models.chatterbox_settings import ChatterboxSettings
from app.settings.models.earshot_settings import EarshotSettings
from app.settings.models.ffmpeg_settings import FfmpegSettings
from app.settings.models.gemini_tts_settings import GeminiTTSSettings
from app.settings.models.groq_whisper_settings import GroqWhisperSettings
from app.settings.models.kokoro_settings import KokoroSettings
from app.settings.models.limits import Limits
from app.settings.models.ollama_settings import OllamaSettings
from app.settings.models.provider_choice import ProviderChoice
from app.settings.models.secrets import Secrets
from app.settings.models.voice_polish_settings import VoicePolishSettings
from app.settings.models.workers_ai_settings import WorkersAISettings


class Settings(_Model):
    providers: ProviderChoice
    ollama: OllamaSettings
    kokoro: KokoroSettings
    gemini_tts: GeminiTTSSettings = GeminiTTSSettings()
    chatterbox: ChatterboxSettings = ChatterboxSettings()
    chatterbox_modal: ChatterboxModalSettings = ChatterboxModalSettings()
    earshot: EarshotSettings = EarshotSettings()
    voice_polish: VoicePolishSettings = VoicePolishSettings()
    groq_whisper: GroqWhisperSettings = GroqWhisperSettings()
    workers_ai: WorkersAISettings
    ffmpeg: FfmpegSettings = FfmpegSettings()
    limits: Limits = Limits()
    budget: Budget = Budget()
    data_dir: Path = Path("data")
    secrets: Secrets = Secrets()
    postiz_api_url: str | None = None
