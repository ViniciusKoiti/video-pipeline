"""Voz e render de um episódio a partir do scenes.json (provisório até `vp voice` #16 e `vp render` #13).

Uso: `.venv/bin/python scripts/provisorio/montar_episodio.py <episode-id> [--no-render] [--preview]`

- Narração Kokoro por cena, na voz do idioma do episódio (config/providers.toml), com cache pelo texto:
  o WAV só é refeito quando a narração da cena muda.
- Duração real de cada WAV (ffprobe) → tempo dos planos (app/pipeline/shots.py) → episode.json v2.
- Render pelo motor do formato explicativo (Remotion), com cache por cena.
- A mídia de cada plano de foto ou B-roll é `assets/<asset_id>.<ext>` (jpg, png, webp, mp4, webm).
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media.probe import duration_ms  # noqa: E402
from app.pipeline.schemas import EpisodeFormat, EpisodeManifest, EpisodeScene, ScenesManifest  # noqa: E402
from app.pipeline.shots import episode_shots, pacing_warnings  # noqa: E402
from app.providers.tts.base import SpeechRequest  # noqa: E402
from app.providers.tts.kokoro import KokoroTTS  # noqa: E402
from app.render.remotion import RemotionEngine  # noqa: E402
from app.settings import load_settings  # noqa: E402

MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")


def media_path(episode_dir: Path, asset_id: str) -> str:
    for suffix in MEDIA_SUFFIXES:
        if (episode_dir / "assets" / f"{asset_id}{suffix}").is_file():
            return f"assets/{asset_id}{suffix}"
    raise SystemExit(f"ativo {asset_id} sem arquivo de mídia em assets/")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    settings = load_settings(ROOT)
    episode_dir = settings.data_dir / "episodes" / args[0]
    scenes = ScenesManifest.model_validate_json((episode_dir / "scenes.json").read_text())
    voice_name = settings.kokoro.voices[scenes.language]
    tts = KokoroTTS(settings.kokoro.voices)
    voice_dir = episode_dir / "voice"
    voice_dir.mkdir(exist_ok=True)

    started = time.monotonic()
    episode_scenes, cursor = [], 0
    for scene in scenes.scenes:
        key = hashlib.sha256(f"{voice_name}|{scene.narration}".encode()).hexdigest()[:10]
        wav = voice_dir / f"{scene.id}-{key}.wav"
        if not wav.exists():
            for stale in voice_dir.glob(f"{scene.id}-*.wav"):
                stale.unlink()
            tts.synthesize_speech(SpeechRequest(text=scene.narration, out_path=wav, language=scenes.language))
        ms = duration_ms(wav)
        shots = episode_shots(scene, ms, lambda shot: media_path(episode_dir, shot.asset_id))
        episode_scenes.append(
            EpisodeScene(
                id=scene.id, start_ms=cursor, duration_ms=ms, narration=scene.narration,
                audio=f"voice/{wav.name}", shots=shots,
            )
        )
        summary = ", ".join(f"{s.spec.kind} {s.duration_ms / 1000:.1f}" for s in shots)
        print(f"{scene.id}: {ms / 1000:5.2f} s | {summary}")
        cursor += ms
    print(f"voz: {time.monotonic() - started:.0f} s; total {cursor / 1000:.1f} s")

    episode = EpisodeManifest(
        schema_version=2, episode_id=scenes.episode_id, title=f"{scenes.episode_id} (rascunho)",
        language=scenes.language, format=EpisodeFormat.EXPLAINER, scenes=episode_scenes,
    )
    (episode_dir / "episode.json").write_text(episode.model_dump_json(indent=2))
    print("ritmo:", pacing_warnings(episode) or "ok")
    if "--no-render" in sys.argv:
        return
    preview = "--preview" in sys.argv
    started = time.monotonic()
    out = episode_dir / "renders" / ("preview.mp4" if preview else "final.mp4")
    result = RemotionEngine().render(episode, episode_dir, out, preview=preview)
    print(f"render: {time.monotonic() - started:.0f} s -> {result.path} ({result.duration_ms / 1000:.1f} s)")


if __name__ == "__main__":
    main()
