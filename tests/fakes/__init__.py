"""Implementações em memória de cada porta (ADR 006). Determinísticas, sem rede, sem dependências.

Servem para testar etapas do pipeline e como referência nos testes de contrato.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import wave
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.pipeline.ports import ManifestNotFound
from app.pipeline.schemas import Asset, EpisodeManifest, Generation, Provider, ReviewEntry, ReviewLog, Status
from app.providers.alignment.base import Cue
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput
from app.providers.http import JsonPost
from app.providers.image_gen.base import CostEstimate, GeneratedImage, ImageRequest
from app.providers.text.base import TextRequest, TextResult, Usage
from app.providers.tts.base import SpeechRequest, SpeechResult
from app.render.base import RenderResult, target_spec
from app.settings import CONFIG_FILE, Settings, load_settings

T = TypeVar("T", bound=BaseModel)
M = TypeVar("M", bound=BaseModel)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)
SAMPLE_RATE = 24_000
MS_PER_WORD = 300
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def make_root(tmp_path: Path, config: str | None = None) -> Path:
    """Pasta de projeto isolada com config/providers.toml (o real, ou `config`) e sem .env."""
    target = tmp_path / CONFIG_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    if config is None:
        shutil.copy(REPO_ROOT / CONFIG_FILE, target)
    else:
        target.write_text(config)
    return tmp_path


def make_settings(tmp_path: Path) -> Settings:
    return load_settings(make_root(tmp_path), environ={})


def write_silence(path: Path, duration_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(b"\x00\x00" * (SAMPLE_RATE * duration_ms // 1000))


def wav_duration_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() * 1000 // wav.getframerate()


class FakeText:
    """Devolve respostas JSON pré-definidas, em ordem, e as valida como um adapter real faria."""

    def __init__(self, responses: Sequence[str] = (), name: str = "fake-text", usd_per_call: float = 0.0):
        self.info = ProviderInfo(name, remote=False, usd_per_call=usd_per_call)
        self._responses = list(responses)
        self.requests: list[TextRequest[Any]] = []

    def generate_json(self, request: TextRequest[T]) -> TextResult[T]:
        self.requests.append(request)
        raw = self._responses.pop(0)
        try:
            data = request.output.model_validate_json(raw)
        except ValidationError as error:
            raise InvalidOutput(self.info.name, str(error)) from error
        usage = Usage(input_tokens=len(request.prompt.split()), output_tokens=len(raw.split()), duration_ms=1)
        return TextResult(data=data, model=request.model or "fake", usage=usage)


class FakeTTS:
    """WAV de silêncio com 300 ms por palavra."""

    def __init__(self) -> None:
        self.info = ProviderInfo("fake-tts", remote=False)

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        write_silence(request.out_path, MS_PER_WORD * max(1, len(request.text.split())))
        return SpeechResult(path=request.out_path, model="fake", voice=request.voice or "fake-voice")


class FakeImageGen:
    def __init__(self, usd_per_image: float = 0.0) -> None:
        self.info = ProviderInfo("fake-image-gen", remote=False, usd_per_call=usd_per_image)

    def estimate_cost(self, request: ImageRequest) -> CostEstimate:
        return CostEstimate(units=float(request.steps), unit="steps", usd=self.info.usd_per_call)

    def generate_image(self, request: ImageRequest) -> GeneratedImage:
        request.out_path.parent.mkdir(parents=True, exist_ok=True)
        request.out_path.write_bytes(PNG_SIGNATURE + request.prompt.encode())
        generation = Generation(
            prompt=request.prompt, model="fake-image", seed=request.seed or 0, steps=request.steps
        )
        return GeneratedImage(path=request.out_path, generation=generation)


class FakeArchive:
    """Candidatos determinísticos por consulta, sempre sem licença identificada (vão para revisão)."""

    def __init__(self, provider: Provider = Provider.WIKIMEDIA_COMMONS, available: int = 3) -> None:
        self.info = ProviderInfo(provider.value, remote=False)
        self._provider = provider
        self._available = available

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]:
        slug = hashlib.sha256(query.text.encode()).hexdigest()[:8]
        return [
            AssetCandidate(
                Asset(
                    id=f"{self._provider.value}-{slug}-{n}",
                    provider=self._provider,
                    provider_id=f"{slug}-{n}",
                    page_url=f"https://example.org/{self._provider.value}/{slug}/{n}",
                    retrieved_at=FIXED_TIME,
                    review_status=Status.NEEDS_REVIEW,
                )
            )
            for n in range(1, min(query.limit, self._available) + 1)
        ]

    def download_asset(self, asset: Asset, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(asset.id.encode())
        return dest


class FakeAligner:
    """Distribui as palavras pela duração do WAV, 7 por legenda."""

    words_per_cue = 7

    def __init__(self) -> None:
        self.info = ProviderInfo("fake-aligner", remote=False)

    def align(self, text: str, audio: Path) -> list[Cue]:
        words, total = text.split(), wav_duration_ms(audio)
        cues, start = [], 0
        for i in range(0, len(words), self.words_per_cue):
            chunk = words[i : i + self.words_per_cue]
            end = total * (i + len(chunk)) // len(words)
            cues.append(Cue(start_ms=start, end_ms=end, text=" ".join(chunk)))
            start = end
        return cues


class FakeRender:
    def __init__(self, name: str = "fake-render") -> None:
        self.info = ProviderInfo(name, remote=False)

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult:
        spec = target_spec(episode, preview=preview)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"episode": episode.episode_id, "engine": self.info.name}))
        return RenderResult(path=out, width=spec.width, height=spec.height, duration_ms=episode.duration_ms)


class InMemoryStore:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._data: dict[tuple[str, str], str] = {}

    def path(self, episode_id: str, name: str) -> Path:
        return self._root / episode_id / name

    def exists(self, episode_id: str, name: str) -> bool:
        return (episode_id, name) in self._data

    def read(self, episode_id: str, name: str, model: type[M]) -> M:
        try:
            return model.model_validate_json(self._data[(episode_id, name)])
        except KeyError:
            raise ManifestNotFound(f"{episode_id}/{name}") from None

    def write(self, episode_id: str, name: str, manifest: BaseModel) -> None:
        self._data[(episode_id, name)] = manifest.model_dump_json()


class InMemoryReviewGate:
    def __init__(self) -> None:
        self._entries: dict[str, list[ReviewEntry]] = {}

    def record(self, episode_id: str, entry: ReviewEntry) -> None:
        self._entries.setdefault(episode_id, []).append(entry)

    def log(self, episode_id: str) -> ReviewLog:
        return ReviewLog(episode_id=episode_id, entries=list(self._entries.get(episode_id, [])))


@dataclass
class FakeContext:
    """Satisfaz `app.pipeline.ports.Context` com fakes; troque campos para cada teste."""

    settings: Settings
    store: InMemoryStore
    review: InMemoryReviewGate = field(default_factory=InMemoryReviewGate)
    text: FakeText = field(default_factory=FakeText)
    tts: FakeTTS = field(default_factory=FakeTTS)
    image_gen: FakeImageGen = field(default_factory=FakeImageGen)
    archives: tuple[FakeArchive, ...] = (FakeArchive(),)
    aligner: FakeAligner = field(default_factory=FakeAligner)
    renderers: dict[str, FakeRender] = field(default_factory=dict)

    def renderer(self, episode_format: str) -> FakeRender:
        return self.renderers.setdefault(episode_format, FakeRender())


def fake_ollama_post(contents: list[str], **overrides: Any) -> tuple[JsonPost, list[dict[str, Any]]]:
    """Transporte falso no formato de resposta do /api/chat do Ollama (tempos em ns)."""
    calls: list[dict[str, Any]] = []

    def post(url: str, payload: Mapping[str, Any], timeout: float) -> dict[str, Any]:
        calls.append({"url": url, "payload": dict(payload), "timeout": timeout})
        return {
            "model": payload["model"],
            "message": {"role": "assistant", "content": contents.pop(0)},
            "done": True,
            "done_reason": "stop",
            "total_duration": 3_000_000_000,
            "load_duration": 1_000_000_000,
            "prompt_eval_count": 120,
            "prompt_eval_cached_count": 0,
            "prompt_eval_duration": 1_500_000_000,
            "eval_count": 30,
            "eval_duration": 500_000_000,
            **overrides,
        }

    return post, calls
