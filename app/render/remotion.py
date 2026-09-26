"""Adapter experimental do Remotion + motion-kit (etapa 8, branch `experimento-remotion`).

Cada cena é uma composição "Scene" do template em `video/` (CameraRig, ImageBackground e FilmGrain do
@viniciusk/motion-kit), renderizada muda por `video/render-scenes.mjs`. Segmentos ficam em cache com
chave = hash do template + imagem + props; a junção e a narração são do `assemble` do motor ffmpeg.
Trocar uma imagem refaz só aquela cena (§5).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.media.probe import dimensions, duration_ms
from app.pipeline.schemas import EpisodeManifest
from app.providers.base import ProviderInfo
from app.render.base import RenderResult, target_spec
from app.render.ffmpeg import FIT_MIN_ASPECT, RunStats, assemble, cues_between, frame_bounds, parse_srt

PROJECT = Path(__file__).resolve().parents[2] / "video"
TEMPLATE_GLOBS = ("src/*.ts", "src/*.tsx", "render-scenes.mjs", "package-lock.json")


class RemotionError(RuntimeError):
    pass


def template_hash(project: Path) -> str:
    digest = hashlib.sha256()
    for pattern in TEMPLATE_GLOBS:
        for path in sorted(project.glob(pattern)):
            digest.update(path.name.encode() + path.read_bytes())
    return digest.hexdigest()


class RemotionEngine:
    def __init__(
        self,
        *,
        project: Path = PROJECT,
        node: str = "node",
        crf: int = 20,
        zoom: float = 0.06,
        fade_s: float = 0.3,
        drift_px: tuple[int, int] = (22, 14),  # deriva do CameraRig em 1080p; escala com a altura
        grain: float = 0.06,  # opacidade do FilmGrain (0 desliga)
        vignette: bool = True,
        concurrency: int = 8,
        jpeg_quality: int = 90,
        preset_final: str = "medium",
        preset_preview: str = "veryfast",
        burn_captions_preview: bool = True,
        burn_captions_final: bool = False,
        audio_bitrate: str = "192k",
    ) -> None:
        self.info = ProviderInfo("remotion", remote=False)
        self._project = project
        self._node = node
        self._crf = crf
        self._zoom = zoom
        self._fade_s = fade_s
        self._drift_px = drift_px
        self._grain = grain
        self._vignette = vignette
        self._concurrency = concurrency
        self._jpeg_quality = jpeg_quality
        self._presets = {True: preset_preview, False: preset_final}
        self._burn = {True: burn_captions_preview, False: burn_captions_final}
        self._audio_bitrate = audio_bitrate
        self.last_run = RunStats()

    def scene_props(
        self, episode: EpisodeManifest, episode_dir: Path, *, preview: bool
    ) -> list[dict[str, Any]]:
        spec = target_spec(episode, preview=preview)
        fps, scale = spec.fps, spec.height / 1080
        cues = []
        if self._burn[preview] and episode.captions:
            cues = parse_srt((episode_dir / episode.captions).read_text())
        bounds = frame_bounds(episode, fps)
        props = []
        for i, scene in enumerate(episode.scenes):
            width, height = dimensions(episode_dir / scene.image)
            window = cues_between(cues, bounds[i] * 1000 // fps, bounds[i + 1] * 1000 // fps)
            props.append(
                {
                    "width": spec.width,
                    "height": spec.height,
                    "fps": fps,
                    "frames": bounds[i + 1] - bounds[i],
                    "image": scene.image,
                    "aspect": width / height,
                    "fitMinAspect": FIT_MIN_ASPECT,
                    "fadeFrames": round(self._fade_s * fps),
                    "cues": [
                        {
                            "from": round(c.start_ms * fps / 1000),
                            "to": round(c.end_ms * fps / 1000),
                            "text": c.text,
                        }
                        for c in window
                    ],
                    "look": {
                        "zoom": self._zoom,
                        "driftX": round(self._drift_px[0] * scale),
                        "driftY": round(self._drift_px[1] * scale),
                        "phase": i * 37,  # dessincroniza a deriva entre cenas (variação visual, §12)
                        "grain": self._grain,
                        "vignette": self._vignette,
                    },
                }
            )
        return props

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult:
        node = shutil.which(self._node)
        if node is None or not (self._project / "node_modules").exists():
            raise RemotionError(f"Remotion não instalado (npm ci em {self._project}; Node.js no PATH)")
        spec = target_spec(episode, preview=preview)
        segments_dir = out.parent / f".segments-remotion-{'preview' if preview else 'final'}"
        segments_dir.mkdir(parents=True, exist_ok=True)
        template = template_hash(self._project)
        self.last_run = RunStats()
        segments, jobs = [], []
        for scene, props in zip(
            episode.scenes, self.scene_props(episode, episode_dir, preview=preview), strict=True
        ):
            payload = {
                "template": template,
                "image": hashlib.sha256((episode_dir / scene.image).read_bytes()).hexdigest(),
                "props": props,
                "encode": [self._crf, self._presets[preview], self._jpeg_quality],
            }
            key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
            segment = segments_dir / f"{scene.id}-{key}.mp4"
            if segment.exists():
                self.last_run.reused.append(scene.id)
            else:
                for stale in segments_dir.glob(f"{scene.id}-*.mp4"):
                    stale.unlink()
                jobs.append({"out": str(segment.resolve()), "props": props})
                self.last_run.rendered.append(scene.id)
            segments.append(segment)
        if jobs:
            self._render_scenes(node, episode_dir, jobs, preview, segments_dir)
        assemble(episode, episode_dir, segments, spec, out, audio_bitrate=self._audio_bitrate)
        return RenderResult(path=out, width=spec.width, height=spec.height, duration_ms=duration_ms(out))

    def _render_scenes(
        self, node: str, episode_dir: Path, jobs: list[dict[str, Any]], preview: bool, work: Path
    ) -> None:
        request = work / "request.json"
        request.write_text(
            json.dumps(
                {
                    "publicDir": str(episode_dir.resolve()),
                    "crf": self._crf,
                    "x264Preset": self._presets[preview],
                    "jpegQuality": self._jpeg_quality,
                    "concurrency": self._concurrency,
                    "jobs": jobs,
                }
            )
        )
        result = subprocess.run(
            [node, "render-scenes.mjs", str(request.resolve())],
            cwd=self._project,
            capture_output=True,
            text=True,
            check=False,
        )
        missing = [job["out"] for job in jobs if not Path(job["out"]).exists()]
        if result.returncode != 0 or missing:
            raise RemotionError(f"Remotion falhou: {(result.stderr or result.stdout).strip()[-800:]}")
        request.unlink()
