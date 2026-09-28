"""Motor do formato `explainer`: Remotion + @viniciusk/motion-kit (ADR 001, ADR 008, etapa #48).

Cada cena é uma composição "Scene" do template em `video/` (identidade "negócios moderno"), com os planos
da cena em sequência; renderizada muda por `video/render-scenes.mjs`. Segmentos ficam em cache com
chave = hash do template + mídias + props; a junção e a narração usam o `assemble` do motor ffmpeg.
Episódio v1 (um visual por cena) vira um plano de foto por cena.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.media.probe import dimensions, duration_ms
from app.pipeline.schemas import Asset, EpisodeManifest, EpisodeScene, EpisodeShot
from app.providers.base import ProviderInfo
from app.render.base import RenderResult, target_spec
from app.render.ffmpeg import RunStats, assemble, cues_between, frame_bounds, parse_srt

PROJECT = Path(__file__).resolve().parents[2] / "video"
TEMPLATE_GLOBS = (
    "src/*.ts", "src/*.tsx", "src/fonts/*", "src/geo/*.json", "render-scenes.mjs", "package-lock.json"
)


class RemotionError(RuntimeError):
    pass


def template_hash(project: Path) -> str:
    digest = hashlib.sha256()
    for pattern in TEMPLATE_GLOBS:
        for path in sorted(project.glob(pattern)):
            digest.update(path.name.encode() + path.read_bytes())
    return digest.hexdigest()


def _credit(episode_dir: Path, asset_id: str | None) -> str | None:
    """Crédito exibido sob a foto, do JSON do ativo (§6); sem JSON, sem crédito."""
    path = episode_dir / "assets" / f"{asset_id}.json"
    if asset_id is None or not path.is_file():
        return None
    asset = Asset.model_validate_json(path.read_text())
    return asset.attribution_text or asset.author


def _editorial(shot: EpisodeShot, fps: int) -> dict[str, Any]:
    """Campos da ADR 011 para o template: fonte do rodapé e quadro de entrada de cada passo da rede."""
    extra: dict[str, Any] = {}
    if shot.source is not None:
        extra["source"] = shot.source
    if shot.source_flag is not None:
        extra["sourceFlag"] = shot.source_flag
    if shot.steps_ms:
        extra["stepFrames"] = [round(ms * fps / 1000) for ms in shot.steps_ms]
    return extra


class RemotionEngine:
    def __init__(
        self,
        *,
        project: Path = PROJECT,
        node: str = "node",
        crf: int = 20,
        fade_s: float = 0.3,
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
        self._fade_s = fade_s
        self._concurrency = concurrency
        self._jpeg_quality = jpeg_quality
        self._presets = {True: preset_preview, False: preset_final}
        self._burn = {True: burn_captions_preview, False: burn_captions_final}
        self._audio_bitrate = audio_bitrate
        self.last_run = RunStats()

    # --- props --------------------------------------------------------------------------------

    def _shots(self, scene: EpisodeScene, frames: int, fps: int, episode_dir: Path) -> list[dict[str, Any]]:
        if not scene.shots:  # v1: um plano de foto sobre a cena inteira
            spec = {"kind": "photo", "anchor": scene.narration, "motion": "push_in"}
            raw: list[tuple[int, dict[str, Any], str | None, str | None, dict[str, Any]]] = [
                (0, spec, scene.image, scene.asset_id, {})
            ]
        else:
            raw = [
                (
                    round(shot.start_ms * fps / 1000),
                    shot.spec.model_dump(mode="json"),
                    shot.media,
                    getattr(shot.spec, "asset_id", None),
                    _editorial(shot, fps),
                )
                for shot in scene.shots
            ]
        starts = [start for start, *_ in raw]
        ends = [*starts[1:], frames]
        shots = []
        for (start, spec, media, asset_id, extra), end in zip(raw, ends, strict=True):
            shot: dict[str, Any] = {"from": start, "frames": end - start, "spec": spec, "media": media}
            shot.update(extra)
            if media is not None:
                width, height = dimensions(episode_dir / media)
                shot["aspect"] = width / height
                shot["credit"] = _credit(episode_dir, asset_id)
            shots.append(shot)
        return shots

    def scene_props(
        self, episode: EpisodeManifest, episode_dir: Path, *, preview: bool
    ) -> list[dict[str, Any]]:
        spec = target_spec(episode, preview=preview)
        fps = spec.fps
        cues = []
        if self._burn[preview] and episode.captions:
            cues = parse_srt((episode_dir / episode.captions).read_text())
        bounds = frame_bounds(episode, fps)
        props = []
        for i, scene in enumerate(episode.scenes):
            frames = bounds[i + 1] - bounds[i]
            window = cues_between(cues, bounds[i] * 1000 // fps, bounds[i + 1] * 1000 // fps)
            props.append(
                {
                    "width": spec.width,
                    "height": spec.height,
                    "fps": fps,
                    "frames": frames,
                    "fadeFrames": round(self._fade_s * fps),
                    "shots": self._shots(scene, frames, fps, episode_dir),
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
        return props

    # --- render -------------------------------------------------------------------------------

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
        all_props = self.scene_props(episode, episode_dir, preview=preview)
        for scene, props in zip(episode.scenes, all_props, strict=True):
            media_hashes = sorted(
                hashlib.sha256((episode_dir / shot["media"]).read_bytes()).hexdigest()
                for shot in props["shots"]
                if shot["media"]
            )
            payload = {
                "template": template,
                "media": media_hashes,
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
