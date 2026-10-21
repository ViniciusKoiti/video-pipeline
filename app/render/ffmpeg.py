"""Motor de montagem com ffmpeg puro — candidato zero da Fase 0 (§9, §13.3). Implementa `RenderEngine`.

Cada cena vira um segmento de vídeo em cache, com chave = hash da imagem, legendas e parâmetros. O vídeo
final concatena os segmentos sem recodificar e codifica a narração inteira uma vez, também pelo demuxer
concat (sem cliques nas emendas; buracos entre cenas viram silêncio). Trocar uma imagem refaz só aquele
segmento (§5). Saída em yuv420p com faixa de cor limitada (tv), como players e o YouTube esperam.

Enquadramento (§9, movimento leve sem cortar o assunto): imagem com proporção >= 1,45 é recortada para
16:9; mais estreita (4:3, vertical) aparece inteira sobre uma cópia desfocada de si mesma. Zoom lento de
1,00 a 1+zoom e fade curto na entrada e na saída de cada cena.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from app.media.loudness import TARGET_LUFS, integrated_lufs
from app.media.probe import dimensions, duration_ms, probe_streams
from app.pipeline.schemas import EpisodeManifest, EpisodeMusic, EpisodeScene, VideoSpec
from app.providers.base import ProviderInfo
from app.render.base import RenderResult, target_spec

ENGINE_VERSION = "2"  # mudar invalida o cache de segmentos (v2: matriz e marcação bt709)
FIT_MIN_ASPECT = 1.45
SRT_TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d\d\d)")


class RenderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str


@dataclass
class RunStats:
    rendered: list[str] = field(default_factory=list)
    reused: list[str] = field(default_factory=list)


def parse_srt(text: str) -> list[Cue]:
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        times = SRT_TIME.findall(lines[1]) if len(lines) >= 2 else []
        if len(times) == 2:
            start, end = (
                int(h) * 3_600_000 + int(m) * 60_000 + int(s) * 1000 + int(ms) for h, m, s, ms in times
            )
            cues.append(Cue(start, end, " ".join(lines[2:])))
    return cues


def _srt_time(ms: int) -> str:
    return f"{ms // 3_600_000:02}:{ms // 60_000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def frame_bounds(episode: EpisodeManifest, fps: int) -> list[int]:
    """Fronteiras em quadros: cada cena vai do seu início ao início da próxima (buracos viram imagem
    parada). A soma dos quadros bate com a duração total, sem acumular arredondamento."""
    starts = [0] + [round(scene.start_ms * fps / 1000) for scene in episode.scenes[1:]]
    return [*starts, round(episode.scenes[-1].end_ms * fps / 1000)]


def cues_between(cues: list[Cue], start_ms: int, end_ms: int, min_ms: int = 40) -> list[Cue]:
    """Legendas que caem no trecho, com tempos relativos ao início dele. Sobras menores que `min_ms`
    (arredondamento na fronteira entre cenas) são descartadas para não piscar por um quadro."""
    clipped = [
        Cue(max(c.start_ms, start_ms) - start_ms, min(c.end_ms, end_ms) - start_ms, c.text)
        for c in cues
        if c.end_ms > start_ms and c.start_ms < end_ms
    ]
    return [c for c in clipped if c.end_ms - c.start_ms >= min_ms]


def scene_image(scene: EpisodeScene) -> str:
    """Visual da cena: v1 (`image`) ou v2 com um único plano de foto. Vários planos: etapa #41/#48."""
    if scene.image is not None:
        return scene.image
    if len(scene.shots) == 1 and scene.shots[0].spec.kind == "photo" and scene.shots[0].media:
        return scene.shots[0].media
    raise RenderError(f"{scene.id}: o motor ffmpeg ainda não monta vários planos por cena (etapas #41 e #48)")


def _escape_filter_path(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


class FfmpegEngine:
    def __init__(
        self,
        *,
        crf: int = 20,
        preset_final: str = "medium",
        preset_preview: str = "veryfast",
        zoom: float = 0.06,
        fade_s: float = 0.3,
        burn_captions_preview: bool = True,
        burn_captions_final: bool = False,
        audio_bitrate: str = "192k",
        font: str = "DejaVu Sans",
    ) -> None:
        self.info = ProviderInfo("ffmpeg", remote=False)
        self._crf = crf
        self._presets = {True: preset_preview, False: preset_final}
        self._zoom = zoom
        self._fade_s = fade_s
        self._burn = {True: burn_captions_preview, False: burn_captions_final}
        self._audio_bitrate = audio_bitrate
        self._font = font
        self.last_run = RunStats()

    # --- porta RenderEngine ----------------------------------------------------------------------

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult:
        spec = target_spec(episode, preview=preview)
        cues = []
        if self._burn[preview] and episode.captions:
            cues = parse_srt((episode_dir / episode.captions).read_text())
        segments_dir = out.parent / f".segments-{'preview' if preview else 'final'}"
        segments_dir.mkdir(parents=True, exist_ok=True)
        self.last_run = RunStats()
        bounds = frame_bounds(episode, spec.fps)
        segments = []
        for i, scene in enumerate(episode.scenes):
            frames = bounds[i + 1] - bounds[i]
            start_ms, end_ms = bounds[i] * 1000 // spec.fps, bounds[i + 1] * 1000 // spec.fps
            image = episode_dir / scene_image(scene)
            scene_cues = cues_between(cues, start_ms, end_ms)
            key = self._segment_key(image, spec, frames, scene_cues, preview)
            segment = segments_dir / f"{scene.id}-{key}.mp4"
            if segment.exists():
                self.last_run.reused.append(scene.id)
            else:
                for stale in segments_dir.glob(f"{scene.id}-*.mp4"):
                    stale.unlink()
                self._render_segment(image, spec, frames, scene_cues, segment, preview)
                self.last_run.rendered.append(scene.id)
            segments.append(segment)
        self._assemble(episode, episode_dir, segments, spec, out)
        return RenderResult(path=out, width=spec.width, height=spec.height, duration_ms=duration_ms(out))

    # --- segmentos ------------------------------------------------------------------------------

    def _segment_key(self, image: Path, spec: VideoSpec, frames: int, cues: list[Cue], preview: bool) -> str:
        payload = {
            "engine": ENGINE_VERSION,
            "image": hashlib.sha256(image.read_bytes()).hexdigest(),
            "spec": [spec.width, spec.height, spec.fps],
            "frames": frames,
            "cues": [[c.start_ms, c.end_ms, c.text] for c in cues],
            "params": [
                self._crf,
                self._presets[preview],
                self._zoom,
                self._fade_s,
                self._font,
                FIT_MIN_ASPECT,
            ],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

    def video_filter(
        self, image_size: tuple[int, int], spec: VideoSpec, frames: int, srt: Path | None
    ) -> str:
        w, h, fps = spec.width, spec.height, spec.fps
        w2, h2 = 2 * w, 2 * h  # superamostragem: o zoompan não treme
        if image_size[0] / image_size[1] >= FIT_MIN_ASPECT:
            base = f"[0:v]scale={w2}:{h2}:force_original_aspect_ratio=increase,crop={w2}:{h2},setsar=1"
        else:
            bw, bh = w // 4, h // 4
            base = (
                f"[0:v]split=2[bg][fg];"
                f"[bg]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},gblur=sigma=8,"
                f"eq=brightness=-0.12,scale={w2}:{h2}[blur];"
                f"[fg]scale={w2}:{h2}:force_original_aspect_ratio=decrease[photo];"
                f"[blur][photo]overlay=(W-w)/2:(H-h)/2,setsar=1"
            )
        duration = frames / fps
        chain = [
            f"zoompan=z='1+{self._zoom}*on/{max(frames - 1, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={frames}:s={w}x{h}:fps={fps}",
            f"fade=t=in:st=0:d={self._fade_s}",
            f"fade=t=out:st={max(duration - self._fade_s, 0):.3f}:d={self._fade_s}",
        ]
        if srt is not None:
            style = f"FontName={self._font},FontSize=16,Outline=1.5,Shadow=0,MarginV=18"
            chain.append(f"subtitles=filename='{_escape_filter_path(srt)}':force_style='{style}'")
        # JPEG vem em faixa cheia: converte para bt709 limitado e marca os quadros (o encoder segue a marca)
        chain.append(
            "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
            "setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709"
        )
        return f"{base},{','.join(chain)}[v]"

    def _render_segment(
        self, image: Path, spec: VideoSpec, frames: int, cues: list[Cue], segment: Path, preview: bool
    ) -> None:
        srt = None
        if cues:
            srt = segment.with_suffix(".srt")
            srt.write_text(
                "".join(
                    f"{n}\n{_srt_time(c.start_ms)} --> {_srt_time(c.end_ms)}\n{c.text}\n\n"
                    for n, c in enumerate(cues, 1)
                )
            )
        tmp = segment.with_suffix(".tmp.mp4")
        graph = self.video_filter(dimensions(image), spec, frames, srt)
        _run(
            [
                "-i",
                str(image),
                "-filter_complex",
                graph,
                "-map",
                "[v]",
                "-frames:v",
                str(frames),
                "-r",
                str(spec.fps),
                "-c:v",
                "libx264",
                "-preset",
                self._presets[preview],
                "-crf",
                str(self._crf),
                "-profile:v",
                "high",
                "-pix_fmt",
                "yuv420p",
                "-color_range",
                "tv",
                "-colorspace",
                "bt709",
                "-color_primaries",
                "bt709",
                "-color_trc",
                "bt709",
                "-an",
                str(tmp),
            ]
        )
        tmp.replace(segment)
        if srt is not None:
            srt.unlink()

    # --- montagem final -------------------------------------------------------------------------

    def _assemble(
        self, episode: EpisodeManifest, episode_dir: Path, segments: list[Path], spec: VideoSpec, out: Path
    ) -> None:
        assemble(episode, episode_dir, segments, spec, out, audio_bitrate=self._audio_bitrate)


def assemble(
    episode: EpisodeManifest,
    episode_dir: Path,
    segments: list[Path],
    spec: VideoSpec,
    out: Path,
    *,
    audio_bitrate: str = "192k",
) -> None:
    """Junta segmentos de vídeo sem recodificar e codifica a narração inteira uma vez (demuxer concat).
    Usada por qualquer motor que renderize por cena. Com trilha (ADR 030), a música entra aqui, por baixo
    da voz: os segmentos de cada cena ficam como estavam, e trocar a faixa refaz só a junção (§5)."""
    video_list = out.parent / f".{out.stem}-video.txt"
    audio_list = out.parent / f".{out.stem}-audio.txt"
    video_list.write_text(_concat_list(segments))
    audio_list.write_text(_concat_list(_audio_parts(episode, episode_dir, out.parent)))
    concat = ["-f", "concat", "-safe", "0"]
    audio: list[str] = ["-map", "1:a"]
    music_inputs: list[str] = []
    if episode.music:
        voice_lufs = integrated_lufs(audio_list, input_args=concat)
        gain = TARGET_LUFS - voice_lufs
        music_inputs, graph = music_mix(episode.music, episode_dir, spec.audio_sample_rate, gain)
        audio = ["-filter_complex", graph, "-map", "[a]"]
    tmp = out.with_suffix(".tmp.mp4")
    _run(
        [
            *concat,
            "-i",
            str(video_list),
            *concat,
            "-i",
            str(audio_list),
            *music_inputs,
            "-map",
            "0:v",
            *audio,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-ar",
            str(spec.audio_sample_rate),
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(tmp),
        ]
    )
    tmp.replace(out)
    video_list.unlink()
    audio_list.unlink()


# Ducking (ADR 030): a trilha baixa enquanto a voz fala, com a própria voz como chave do compressor.
DUCKING = "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500"
LIMITER = "alimiter=limit=0.89:level=false"  # teto de ~-1 dBFS depois do ganho para o alvo de loudness


def music_mix(
    music: list[EpisodeMusic], episode_dir: Path, sample_rate: int, voice_gain_db: float
) -> tuple[list[str], str]:
    """Entradas do ffmpeg (a partir da 2: vídeo e voz vêm antes) e o grafo que põe cada trecho da trilha no
    lugar, com fade e ganho, e mistura com a voz levada ao alvo de loudness. Saída no rótulo `[a]`."""
    fmt = f"aformat=sample_rates={sample_rate}:channel_layouts=stereo"
    inputs: list[str] = []
    chains = []
    for i, cue in enumerate(music):
        inputs += [*(["-stream_loop", "-1"] if cue.loop else []), "-i", str(episode_dir / cue.media)]
        length = (cue.end_ms - cue.start_ms) / 1000
        steps = [
            f"atrim=start={cue.track_offset_ms / 1000:.3f}:duration={length:.3f}",
            "asetpts=PTS-STARTPTS",
            fmt,
            f"volume={cue.gain_db:.1f}dB",
        ]
        if cue.fade_in_ms:
            steps.append(f"afade=t=in:st=0:d={cue.fade_in_ms / 1000:.3f}")
        if cue.fade_out_ms:
            fade = cue.fade_out_ms / 1000
            steps.append(f"afade=t=out:st={length - fade:.3f}:d={fade:.3f}")
        steps.append(f"adelay={cue.start_ms}:all=1")
        chains.append(f"[{2 + i}:a]{','.join(steps)}[m{i}]")
    labels = "".join(f"[m{i}]" for i in range(len(music)))
    bus = f"{labels}amix=inputs={len(music)}:normalize=0[bus]" if len(music) > 1 else f"{labels}anull[bus]"
    graph = [
        *chains,
        bus,
        f"[1:a]{fmt},volume={voice_gain_db:.2f}dB,asplit=2[voice][key]",
        f"[bus][key]{DUCKING}[ducked]",
        f"[voice][ducked]amix=inputs=2:normalize=0:duration=first,{LIMITER}[a]",
    ]
    return inputs, ";".join(graph)


def _audio_parts(episode: EpisodeManifest, episode_dir: Path, work: Path) -> list[Path]:
    """WAVs das cenas na ordem, com silêncio no lugar de buracos. O demuxer exige o mesmo formato."""
    wavs = [episode_dir / scene.audio for scene in episode.scenes]
    formats = {_audio_format(wav) for wav in wavs}
    if len(formats) != 1:
        raise RenderError(f"WAVs com formatos diferentes: {sorted(formats)}")
    ((codec, rate, channels),) = formats
    parts, cursor = [], 0
    for scene, wav in zip(episode.scenes, wavs, strict=True):
        if scene.start_ms > cursor:
            silence = work / f".silence-{scene.id}.wav"
            _run(
                [
                    "-f",
                    "lavfi",
                    "-i",
                    f"anullsrc=r={rate}:cl={'mono' if channels == 1 else 'stereo'}",
                    "-t",
                    f"{(scene.start_ms - cursor) / 1000:.3f}",
                    "-c:a",
                    codec,
                    str(silence),
                ]
            )
            parts.append(silence)
        parts.append(wav)
        cursor = scene.end_ms
    return parts


def _audio_format(path: Path) -> tuple[str, int, int]:
    stream = next(s for s in probe_streams(path) if s.get("codec_type") == "audio")
    return str(stream["codec_name"]), int(str(stream["sample_rate"])), int(str(stream["channels"]))


def _concat_list(paths: list[Path]) -> str:
    return "".join("file '" + str(p.resolve()).replace("'", "'\\''") + "'\n" for p in paths)


def _run(args: list[str]) -> None:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RenderError(f"ffmpeg falhou: {result.stderr.strip()[-500:]}")
