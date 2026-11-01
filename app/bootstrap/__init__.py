"""Raiz de composição: único módulo que conhece os adapters concretos (ADR 006).

O registro é explícito (sem descoberta de plugins). Cada fábrica importa seu adapter dentro da
função, então `vp status` não carrega Kokoro/PyTorch. Um adapter ainda não implementado aparece com
a etapa do roadmap que vai entregá-lo.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from pydantic import SecretStr

from app.bootstrap.registry import ConfigurationError, Registration, Registry, ensure_free, unknown_choices
from app.pipeline.ports import ManifestStore, ReviewGate
from app.pipeline.schemas import EpisodeFormat
from app.pipeline.usage import UsageLedger
from app.providers.alignment.base import SubtitleAligner, WordAligner
from app.providers.archives.base import ArchiveProvider
from app.providers.base import ProviderInfo
from app.providers.image_gen.base import ImageGenProvider
from app.providers.text.base import TextProvider
from app.providers.tts.base import TTSProvider
from app.render.base import RenderEngine
from app.settings import Settings, load_settings

if TYPE_CHECKING:
    from app.providers.postiz import PostizClient

T = TypeVar("T")
__all__ = ["ConfigurationError", "Registration", "Registry", "ensure_free"]


def _ollama(settings: Settings) -> TextProvider:
    from app.providers.text.ollama import OllamaText

    return OllamaText(settings.ollama.base_url, settings.ollama.model, num_thread=settings.ollama.num_thread)


def _ffmpeg(settings: Settings) -> RenderEngine:
    from app.render.ffmpeg import FfmpegEngine

    return FfmpegEngine(**settings.ffmpeg.model_dump())


def _json_store(settings: Settings) -> ManifestStore:
    from app.storage.json_files import JsonFileStore

    return JsonFileStore(settings.data_dir / "episodes")


def _remotion(settings: Settings) -> RenderEngine:
    from app.render.remotion import RemotionEngine

    ff = settings.ffmpeg  # mesmos parâmetros de codificação do motor ffmpeg
    return RemotionEngine(
        crf=ff.crf, fade_s=ff.fade_s, preset_final=ff.preset_final, preset_preview=ff.preset_preview
    )


def _secret(settings: Settings, env_name: str) -> str:
    secret = getattr(settings.secrets, env_name.lower())
    if not isinstance(secret, SecretStr):
        raise ConfigurationError(f"{env_name} ausente no .env")
    return secret.get_secret_value()


def build_postiz(settings: Settings) -> PostizClient:
    from app.providers.postiz import PostizClient

    if not settings.postiz_api_url:
        raise ConfigurationError("POSTIZ_API_URL ausente no .env")
    return PostizClient(settings.postiz_api_url, _secret(settings, "POSTIZ_API_KEY"))


def build_usage(settings: Settings) -> UsageLedger:
    from app.storage.usage_sqlite import SQLiteUsageLedger

    return SQLiteUsageLedger(settings.data_dir / "telemetry" / "usage.sqlite3")


def _archive_cache(settings: Settings) -> Path:
    return settings.data_dir / "cache" / "archives"


def _pexels(settings: Settings) -> ArchiveProvider:
    from app.providers.archives.pexels import PexelsArchive

    return PexelsArchive(_secret(settings, "PEXELS_API_KEY"), cache_dir=_archive_cache(settings))


def _pixabay(settings: Settings) -> ArchiveProvider:
    from app.providers.archives.pixabay import PixabayArchive

    return PixabayArchive(_secret(settings, "PIXABAY_API_KEY"), cache_dir=_archive_cache(settings))


def _unsplash(settings: Settings) -> ArchiveProvider:
    from app.providers.archives.unsplash import UnsplashArchive

    return UnsplashArchive(_secret(settings, "UNSPLASH_ACCESS_KEY"), cache_dir=_archive_cache(settings))


def _json_review(settings: Settings) -> ReviewGate:
    from app.storage.json_files import JsonFileStore, JsonReviewGate

    return JsonReviewGate(JsonFileStore(settings.data_dir / "episodes"))


def _kokoro(settings: Settings) -> TTSProvider:
    from app.providers.tts.kokoro import KokoroTTS

    return KokoroTTS(
        settings.kokoro.voices, num_threads=settings.kokoro.num_threads, pause_ms=settings.kokoro.pause_ms
    )


def _gemini_tts(settings: Settings) -> TTSProvider:
    from app.providers.tts.gemini import GeminiTTS

    gemini = settings.gemini_tts
    return GeminiTTS(
        _secret(settings, "GEMINI_API_KEY"), model=gemini.model, voices=gemini.voices, styles=gemini.styles,
        requests_per_minute=gemini.requests_per_minute,
    )


def _chatterbox(settings: Settings) -> TTSProvider:
    from app.providers.tts.chatterbox import ChatterboxTTS

    box = settings.chatterbox
    return ChatterboxTTS(
        box.python and box.python.expanduser(), box.reference and box.reference.expanduser(), model=box.model,
        language_ids=box.language_ids, num_threads=box.num_threads, pause_ms=box.pause_ms,
        delivery={name: params.model_dump() for name, params in box.delivery.items()},
    )


def _chatterbox_modal(settings: Settings) -> TTSProvider:
    from app.providers.tts.chatterbox import ChatterboxTTS, modal_starter

    box, cloud = settings.chatterbox, settings.chatterbox_modal
    return ChatterboxTTS(
        cloud.python.expanduser(), box.reference and box.reference.expanduser(), model=box.model,
        language_ids=box.language_ids, pause_ms=box.pause_ms,
        delivery={name: params.model_dump() for name, params in box.delivery.items()},
        start=modal_starter(cloud.app, cloud.reference_name), provider="chatterbox_modal", remote=True,
    )


def _groq_words(settings: Settings) -> WordAligner:
    from app.providers.alignment.groq import GroqWordAligner

    whisper = settings.groq_whisper
    key = _secret(settings, "GROQ_API_KEY")
    return GroqWordAligner(key, model=whisper.model, timeout_s=whisper.timeout_s)


DEFAULT_REGISTRY: Registry = {
    "text": {"ollama": Registration(5, _ollama), "groq": Registration(29), "gemini": Registration(29)},
    "tts": {
        "kokoro": Registration(5, _kokoro),
        "gemini": Registration(15, _gemini_tts),  # ADR 012
        "chatterbox": Registration(15, _chatterbox),  # voz clonada local (ADR 016, proposta)
        "chatterbox_modal": Registration(15, _chatterbox_modal),  # a mesma voz numa GPU do Modal (ADR 024)
    },
    "image_gen": {"workers_ai": Registration(24)},
    "archives": {
        "wikimedia_commons": Registration(20),
        "library_of_congress": Registration(20),
        "flickr_commons": Registration(20),
        "pexels": Registration(21, _pexels),  # antecipado pela #48 (abertura v2)
        "pixabay": Registration(21, _pixabay),  # emenda de bancos de imagem da ADR 007
        "unsplash": Registration(21, _unsplash),  # idem; Coverr fica só manual
    },
    "aligner": {"ffprobe": Registration(17)},
    "word_aligner": {"groq": Registration(17, _groq_words)},
    "render": {
        "ffmpeg": Registration(7, _ffmpeg),
        "moneyprinterturbo": Registration(8),
        "remotion": Registration(48, _remotion),  # formato explainer (etapa #48 antecipou a #43)
    },
    "store": {"json_files": Registration(10, _json_store)},
    "review": {"json_files": Registration(12, _json_review)},
}


class LazyContext:
    """Implementa `app.pipeline.ports.Context`; cada porta é montada no primeiro uso."""

    def __init__(self, settings: Settings, registry: Registry = DEFAULT_REGISTRY) -> None:
        self._settings = settings
        self._registry = registry
        self._renderers: dict[EpisodeFormat, RenderEngine] = {}

    @property
    def settings(self) -> Settings:
        return self._settings

    @cached_property
    def store(self) -> ManifestStore:
        return self._build("store", self._settings.providers.store, self._registry["store"])

    @cached_property
    def review(self) -> ReviewGate:
        return self._build("review", self._settings.providers.review, self._registry["review"])

    @cached_property
    def text(self) -> TextProvider:
        return self._build("text", self._settings.providers.text, self._registry["text"])

    @cached_property
    def tts(self) -> TTSProvider:
        return self._build("tts", self._settings.providers.tts, self._registry["tts"])

    @cached_property
    def tts_final(self) -> TTSProvider:
        """Voz do vídeo final (ADR 012); sem `tts_final` na configuração, a mesma dos rascunhos."""
        name = self._settings.providers.tts_final
        return self.tts if name is None else self._build("tts", name, self._registry["tts"])

    def tts_named(self, name: str) -> TTSProvider:
        """Uma voz registrada pelo nome, fora da escolha do `providers.toml` (ex.: teste da voz clonada)."""
        if name not in self._registry["tts"]:
            options = ", ".join(sorted(self._registry["tts"]))
            raise ConfigurationError(f"tts = {name!r} não existe (opções: {options})")
        return self._build("tts", name, self._registry["tts"])

    @cached_property
    def image_gen(self) -> ImageGenProvider:
        return self._build("image_gen", self._settings.providers.image_gen, self._registry["image_gen"])

    @cached_property
    def archives(self) -> tuple[ArchiveProvider, ...]:
        return tuple(
            self._build("archives", name, self._registry["archives"])
            for name in self._settings.providers.archives
        )

    @cached_property
    def aligner(self) -> SubtitleAligner:
        return self._build("aligner", self._settings.providers.aligner, self._registry["aligner"])

    @cached_property
    def word_aligner(self) -> WordAligner:
        return self._build(
            "word_aligner", self._settings.providers.word_aligner, self._registry["word_aligner"]
        )

    def renderer(self, episode_format: EpisodeFormat) -> RenderEngine:
        if episode_format not in self._renderers:
            name = self._settings.providers.render.get(episode_format)
            if name is None:
                raise ConfigurationError(f"nenhum motor de render para o formato {episode_format}")
            self._renderers[episode_format] = self._build("render", name, self._registry["render"])
        return self._renderers[episode_format]

    def _build(self, port: str, name: str, options: Mapping[str, Registration[T]]) -> T:
        registration = options[name]  # nomes já conferidos em build_context
        if registration.factory is None:
            raise ConfigurationError(f"{port} = {name!r} ainda não implementado (etapa #{registration.step})")
        provider = registration.factory(self._settings)
        info = getattr(provider, "info", None)
        if isinstance(info, ProviderInfo):
            ensure_free(info, self._settings.budget)
        return provider


def build_context(
    root: Path, environ: Mapping[str, str] | None = None, registry: Registry = DEFAULT_REGISTRY
) -> LazyContext:
    settings = load_settings(root, environ)
    problems = unknown_choices(settings, registry)
    if problems:
        raise ConfigurationError("config/providers.toml: " + "; ".join(problems))
    return LazyContext(settings, registry)
