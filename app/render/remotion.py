"""Adapter experimental do Remotion (etapa 8, branch `experimento-remotion`).

O template React em `video/` recebe como props a linha do tempo do `episode.json` (quadros por cena,
proporção das imagens, legendas da prévia) e o `--public-dir` aponta para a pasta do episódio. Mesmas
regras visuais do motor ffmpeg; sem cache por cena (cada render é completo).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.media.probe import dimensions, duration_ms
from app.pipeline.schemas import EpisodeManifest
from app.providers.base import ProviderInfo
from app.render.base import RenderResult, target_spec
from app.render.ffmpeg import FIT_MIN_ASPECT, cues_between, frame_bounds, parse_srt

PROJECT = Path(__file__).resolve().parents[2] / "video"


class RemotionError(RuntimeError):
    pass


class RemotionEngine:
    def __init__(
        self,
        *,
        project: Path = PROJECT,
        npx: str = "npx",
        crf: int = 20,
        zoom: float = 0.06,
        fade_s: float = 0.3,
        concurrency: int = 8,
        preset_final: str = "medium",
        preset_preview: str = "veryfast",
        burn_captions_preview: bool = True,
        burn_captions_final: bool = False,
    ) -> None:
        self.info = ProviderInfo("remotion", remote=False)
        self._project = project
        self._npx = npx
        self._crf = crf
        self._zoom = zoom
        self._fade_s = fade_s
        self._concurrency = concurrency
        self._presets = {True: preset_preview, False: preset_final}
        self._burn = {True: burn_captions_preview, False: burn_captions_final}

    def props(self, episode: EpisodeManifest, episode_dir: Path, *, preview: bool) -> dict[str, Any]:
        spec = target_spec(episode, preview=preview)
        fps = spec.fps
        cues = []
        if self._burn[preview] and episode.captions:
            cues = parse_srt((episode_dir / episode.captions).read_text())
        bounds = frame_bounds(episode, fps)
        scenes = []
        for i, scene in enumerate(episode.scenes):
            width, height = dimensions(episode_dir / scene.image)
            window = cues_between(cues, bounds[i] * 1000 // fps, bounds[i + 1] * 1000 // fps)
            scenes.append(
                {
                    "id": scene.id,
                    "startFrame": bounds[i],
                    "frames": bounds[i + 1] - bounds[i],
                    "image": scene.image,
                    "audio": scene.audio,
                    "aspect": width / height,
                    "cues": [
                        {
                            "from": round(c.start_ms * fps / 1000),
                            "to": round(c.end_ms * fps / 1000),
                            "text": c.text,
                        }
                        for c in window
                    ],
                }
            )
        return {
            "width": spec.width,
            "height": spec.height,
            "fps": fps,
            "totalFrames": bounds[-1],
            "zoom": self._zoom,
            "fadeFrames": round(self._fade_s * fps),
            "fitMinAspect": FIT_MIN_ASPECT,
            "burnCaptions": bool(cues),
            "scenes": scenes,
        }

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult:
        npx = shutil.which(self._npx)
        if npx is None or not (self._project / "node_modules").exists():
            raise RemotionError(f"Remotion não instalado (npm install em {self._project}; Node.js no PATH)")
        spec = target_spec(episode, preview=preview)
        out.parent.mkdir(parents=True, exist_ok=True)
        props_path = out.parent / f".{out.stem}-props.json"
        props_path.write_text(json.dumps(self.props(episode, episode_dir, preview=preview)))
        result = subprocess.run(
            [
                npx,
                "remotion",
                "render",
                "src/index.ts",
                "Episode",
                str(out.resolve()),
                f"--props={props_path.resolve()}",
                f"--public-dir={episode_dir.resolve()}",
                "--codec=h264",
                f"--crf={self._crf}",
                f"--x264-preset={self._presets[preview]}",
                "--pixel-format=yuv420p",
                "--color-space=bt709",
                "--jpeg-quality=90",  # faixa limitada (tv)
                "--audio-codec=aac",
                "--audio-bitrate=192k",
                f"--concurrency={self._concurrency}",
                "--log=error",
            ],
            cwd=self._project,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not out.exists():
            raise RemotionError(f"Remotion falhou: {(result.stderr or result.stdout).strip()[-800:]}")
        props_path.unlink()
        return RenderResult(path=out, width=spec.width, height=spec.height, duration_ms=duration_ms(out))
