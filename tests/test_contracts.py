"""Testes de contrato: toda implementação de uma porta precisa passar aqui (ADR 006).

Adapter real novo = um `pytest.param` a mais na lista da porta, com uma fábrica que o prepara sem
rede (transporte HTTP falso, fixtures em data/cache/). Adapters locais pesados levam marca própria.
"""

from __future__ import annotations

import json
import os
import tempfile
import wave
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.pipeline.ports import EpisodeLocked, ImmutableManifest, ManifestNotFound, ManifestStore, ReviewGate
from app.pipeline.schemas import (
    APPROVED_STATES,
    Asset,
    Decision,
    EpisodeManifest,
    ReviewEntry,
    Status,
    VisualNeed,
)
from app.providers.alignment.base import SubtitleAligner
from app.providers.archives.base import ArchiveProvider, AssetQuery
from app.providers.archives.pexels import PexelsArchive
from app.providers.archives.pixabay import PixabayArchive
from app.providers.archives.unsplash import UnsplashArchive
from app.providers.errors import InvalidOutput
from app.providers.image_gen.base import ImageGenProvider, ImageRequest
from app.providers.text.base import TextProvider, TextRequest
from app.providers.text.ollama import OllamaText
from app.providers.tts.base import SpeechRequest, TTSProvider
from app.render.base import RenderEngine
from app.render.ffmpeg import FfmpegEngine
from app.render.remotion import PROJECT as REMOTION_PROJECT
from app.render.remotion import RemotionEngine
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import (
    FIXED_TIME,
    FakeAligner,
    FakeArchive,
    FakeHttp,
    FakeImageGen,
    FakeRender,
    FakeText,
    FakeTTS,
    InMemoryReviewGate,
    InMemoryStore,
    fake_ollama_post,
    write_silence,
)

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"  # entrada do experimento de motor


class Reply(BaseModel):
    text: str
    source_ids: list[str]


def make_ollama(responses: list[str]) -> TextProvider:
    return OllamaText("http://127.0.0.1:11434", "qwen3.5:4b", post=fake_ollama_post(responses)[0])


def make_pexels() -> ArchiveProvider:
    fixtures = Path(__file__).parent / "fixtures" / "archives" / "pexels"
    http = FakeHttp({"/v1/search": json.loads((fixtures / "photos-search.json").read_text())})
    return PexelsArchive("chave", get=http.get, get_file=http.get_file)


def make_pixabay() -> ArchiveProvider:
    fixtures = Path(__file__).parent / "fixtures" / "archives" / "pixabay"
    http = FakeHttp({"pixabay.com/api/?": json.loads((fixtures / "images-search.json").read_text())})
    return PixabayArchive("chave", get=http.get, get_file=http.get_file)


def make_unsplash() -> ArchiveProvider:
    fixtures = Path(__file__).parent / "fixtures" / "archives" / "unsplash"
    http = FakeHttp(
        {
            "/search/photos": json.loads((fixtures / "search-photos.json").read_text()),
            "/download": {"url": "https://image.unsplash.com/example"},
        }
    )
    return UnsplashArchive("chave", get=http.get, get_file=http.get_file)


def make_gemini_tts() -> TTSProvider:
    from app.providers.tts.gemini import GeminiTTS
    from tests.test_gemini_tts import FakePost, audio_response, wav_bytes

    return GeminiTTS(
        "chave", model="gemini-3.8-flash-tts", voices={"en": "Charon"}, styles={},
        requests_per_minute=3, post=FakePost(audio_response(wav_bytes())),
    )


def make_kokoro() -> TTSProvider:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # pesos já em cache: o teste não acessa a rede (§2.10)
    from app.providers.tts.kokoro import KokoroTTS

    return KokoroTTS({"en": "am_michael"})


def make_chatterbox() -> TTSProvider:
    from tests.test_chatterbox_tts import make_tts

    return make_tts()  # processo do modelo falso: sem rede e sem o modelo (§2.10)


NEEDS_TTS_EXTRA = pytest.mark.skipif(find_spec("kokoro") is None, reason="extra tts ausente")

# Uma lista por porta. Etapas futuras acrescentam os adapters reais.
TEXT: list[Callable[[list[str]], TextProvider]] = [
    pytest.param(FakeText, id="fake"),
    pytest.param(make_ollama, id="ollama"),
]
TTS: list[Callable[[], TTSProvider]] = [
    pytest.param(FakeTTS, id="fake"),
    pytest.param(make_gemini_tts, id="gemini"),  # POST falso: sem rede (§2.10)
    pytest.param(make_kokoro, id="kokoro", marks=[pytest.mark.slow, NEEDS_TTS_EXTRA]),
    pytest.param(make_chatterbox, id="chatterbox"),
]
IMAGE_GEN: list[Callable[[], ImageGenProvider]] = [pytest.param(FakeImageGen, id="fake")]
ARCHIVES: list[Callable[[], ArchiveProvider]] = [
    pytest.param(FakeArchive, id="fake"),
    pytest.param(make_pexels, id="pexels"),
    pytest.param(make_pixabay, id="pixabay"),
    pytest.param(make_unsplash, id="unsplash"),
]
ALIGNERS: list[Callable[[], SubtitleAligner]] = [pytest.param(FakeAligner, id="fake")]
RENDERERS: list[Callable[[], RenderEngine]] = [
    pytest.param(FakeRender, id="fake"),
    pytest.param(FfmpegEngine, id="ffmpeg", marks=pytest.mark.slow),  # renderiza os 52 s da engine-test
    pytest.param(  # formato explainer (ADR 008); exige `npm ci` em video/
        RemotionEngine,
        id="remotion",
        marks=[
            pytest.mark.slow,
            pytest.mark.skipif(
                not (REMOTION_PROJECT / "node_modules").exists(), reason="Remotion não instalado"
            ),
        ],
    ),
]
STORES: list[Callable[[Path], ManifestStore]] = [
    pytest.param(InMemoryStore, id="in-memory"),
    pytest.param(JsonFileStore, id="json-files"),
]
def make_json_review_gate() -> ReviewGate:
    return JsonReviewGate(JsonFileStore(Path(tempfile.mkdtemp(prefix="vp-review-"))))


REVIEW_GATES: list[Callable[[], ReviewGate]] = [
    pytest.param(InMemoryReviewGate, id="in-memory"),
    pytest.param(make_json_review_gate, id="json-files"),
]


def episode() -> EpisodeManifest:
    return EpisodeManifest.model_validate_json((FIXTURE / "episode.json").read_text())


# --- Texto --------------------------------------------------------------------------------------


@pytest.mark.parametrize("make", TEXT)
def test_text_returns_validated_model(make: Callable[[list[str]], TextProvider]) -> None:
    provider = make([Reply(text="The ship left port.", source_ids=["source-01"]).model_dump_json()])
    result = provider.generate_json(TextRequest(prompt="Write one sentence.", output=Reply))
    assert isinstance(result.data, Reply)
    assert result.data.source_ids == ["source-01"]
    assert result.model
    assert min(result.usage.input_tokens, result.usage.output_tokens, result.usage.duration_ms) >= 0
    assert provider.info.name


@pytest.mark.parametrize("make", TEXT)
def test_text_rejects_output_outside_schema(make: Callable[[list[str]], TextProvider]) -> None:
    provider = make(['{"unexpected": true}'])
    with pytest.raises(InvalidOutput):
        provider.generate_json(TextRequest(prompt="Write one sentence.", output=Reply))


# --- Voz ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("make", TTS)
def test_tts_writes_wav_at_requested_path(make: Callable[[], TTSProvider], tmp_path: Path) -> None:
    out = tmp_path / "voice" / "S01.wav"
    result = make().synthesize_speech(SpeechRequest(text="The expedition left port.", out_path=out))
    assert result.path == out
    assert result.voice and result.model
    with wave.open(str(out), "rb") as wav:
        assert wav.getnframes() > 0


# --- Geração de imagem --------------------------------------------------------------------------


@pytest.mark.parametrize("make", IMAGE_GEN)
def test_image_gen_estimates_then_generates(make: Callable[[], ImageGenProvider], tmp_path: Path) -> None:
    provider = make()
    request = ImageRequest(prompt="Ship in pack ice, engraving style", out_path=tmp_path / "S03.png", seed=7)
    estimate = provider.estimate_cost(request)
    assert estimate.units > 0 and estimate.usd >= 0 and estimate.unit
    image = provider.generate_image(request)
    assert image.path == request.out_path and image.path.stat().st_size > 0
    assert (image.generation.prompt, image.generation.steps) == (request.prompt, request.steps)


# --- Acervos ------------------------------------------------------------------------------------


@pytest.mark.parametrize("make", ARCHIVES)
def test_archive_candidates_respect_limit_and_never_come_approved(
    make: Callable[[], ArchiveProvider], tmp_path: Path
) -> None:
    provider = make()
    candidates = provider.search_assets(
        AssetQuery(text="expedition ship harbor", visual_need=VisualNeed.HISTORICAL_EXACT, limit=2)
    )
    assert 0 < len(candidates) <= 2
    for candidate in candidates:
        assert candidate.asset.review_status not in APPROVED_STATES  # aprovar é humano (§2.5)
        assert candidate.asset.provider.value == provider.info.name
    downloaded = provider.download_asset(candidates[0].asset, tmp_path / "assets" / "a.jpg")
    assert downloaded.stat().st_size > 0


# --- Alinhamento --------------------------------------------------------------------------------


@pytest.mark.parametrize("make", ALIGNERS)
def test_aligner_cues_are_ordered_and_keep_every_word(
    make: Callable[[], SubtitleAligner], tmp_path: Path
) -> None:
    text = "The expedition left port with one goal and twenty five men aboard the ship."
    audio = tmp_path / "S01.wav"
    write_silence(audio, 4_500)
    cues = make().align(text, audio)
    assert " ".join(c.text for c in cues).split() == text.split()
    assert all(c.start_ms < c.end_ms for c in cues)
    assert all(a.end_ms <= b.start_ms for a, b in zip(cues, cues[1:], strict=False))
    assert cues[-1].end_ms <= 4_500


# --- Motor de render ----------------------------------------------------------------------------


@pytest.mark.parametrize("make", RENDERERS)
@pytest.mark.parametrize(("preview", "size"), [(False, (1920, 1080)), (True, (1280, 720))])
def test_render_follows_episode_contract(
    make: Callable[[], RenderEngine], preview: bool, size: tuple[int, int], tmp_path: Path
) -> None:
    out = tmp_path / "renders" / "out.mp4"
    result = make().render(episode(), FIXTURE, out, preview=preview)
    assert result.path == out and out.stat().st_size > 0
    assert (result.width, result.height) == size
    assert abs(result.duration_ms - episode().duration_ms) <= 50  # arredondamento de quadro e AAC


# --- Portas internas ----------------------------------------------------------------------------


@pytest.mark.parametrize("make", STORES)
def test_store_round_trips_manifests(make: Callable[[Path], ManifestStore], tmp_path: Path) -> None:
    store = make(tmp_path)
    assert not store.exists("pilot-example", "episode.json")
    with pytest.raises(ManifestNotFound):
        store.read("pilot-example", "episode.json", EpisodeManifest)
    store.write("pilot-example", "episode.json", episode())
    assert store.read("pilot-example", "episode.json", EpisodeManifest) == episode()
    assert store.path("pilot-example", "episode.json").is_relative_to(tmp_path)


@pytest.mark.parametrize("make", STORES)
def test_store_lock_is_exclusive_per_episode(make: Callable[[Path], ManifestStore], tmp_path: Path) -> None:
    store = make(tmp_path)
    with store.lock("pilot-example"):
        with pytest.raises(EpisodeLocked), store.lock("pilot-example"):
            pass
        with store.lock("outro-episodio"):  # episódios diferentes não se bloqueiam
            pass
    with store.lock("pilot-example"):  # liberada ao sair
        pass


@pytest.mark.parametrize("make", STORES)
def test_store_never_overwrites_an_approved_manifest(
    make: Callable[[Path], ManifestStore], tmp_path: Path
) -> None:
    store = make(tmp_path)
    asset = Asset.model_validate_json((FIXTURE / "assets" / "commons-111-sc-91135.json").read_text())
    store.write(
        "engine-test", "assets/a.json", asset.model_copy(update={"review_status": Status.NEEDS_REVIEW})
    )
    store.write("engine-test", "assets/a.json", asset)  # pendente → aprovado: permitido
    with pytest.raises(ImmutableManifest):
        store.write("engine-test", "assets/a.json", asset.model_copy(update={"usage_notes": "outra coisa"}))
    assert store.read("engine-test", "assets/a.json", Asset) == asset


@pytest.mark.parametrize("make", REVIEW_GATES)
def test_review_gate_only_appends(make: Callable[[], ReviewGate]) -> None:
    gate = make()
    assert gate.log("pilot-example").entries == []
    first = ReviewEntry(step="script", decision="changes_requested", reviewer="v", at=FIXED_TIME)
    second = first.model_copy(update={"decision": Decision.APPROVED})
    gate.record("pilot-example", first)
    gate.record("pilot-example", second)
    assert gate.log("pilot-example").entries == [first, second]
