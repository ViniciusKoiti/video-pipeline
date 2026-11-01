"""`vp render`: voz, tempo dos planos, legendas, `episode.json` e render de um episódio explicativo.

O que faz, na ordem: a narração por cena (`vp voice`; só gera o que falta); a duração real de cada WAV vira
o tempo dos planos (`app/pipeline/episode_build.py`); `captions.srt` por frase, editável e refeito só quando
a fala muda (`app/pipeline/caption_production.py`); a legenda palavra a palavra, se pedida; a trilha de
`music.json`, se houver; o `episode.json`; e o render pelo motor do formato (Remotion), com cache por cena.

- `--preview`: prévia em 720p (`renders/preview.mp4`); sem ela, o final (`renders/final.mp4`), que pede
  todos os ativos aprovados no gate 3. O gate 4 aprovado recusa render por cima do MP4, do `episode.json` e
  do `captions.srt` carimbados (`vp reopen --step preview`).
- `--no-render`: só confere a montagem e grava o `episode.json`.
- `--voz-final` e `--voz NOME`: a voz, como no `vp voice`.
- `--legenda-palavra`: legenda palavra a palavra. Manda o WAV de cada cena ainda não reconhecida ao Whisper
  da Groq (remoto, camada gratuita): só com pedido do dono na sessão.
- Depois do render com trilha, a loudness final é medida (alvo −14 LUFS).
"""

from __future__ import annotations

import argparse
import os
import time
from collections.abc import Callable
from pathlib import Path

from app.commands.voice import select_tts
from app.media.loudness import integrated_lufs, loudness_problem
from app.media.narration import strip_pauses
from app.media.word_captions import SceneSpeech
from app.pipeline.assembly import EpisodeRenderer
from app.pipeline.caption_production import write_captions, write_word_captions
from app.pipeline.episode_build import build_episode, build_scenes, music_segments, with_music
from app.pipeline.ports import Context
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import EpisodeManifest, EpisodeScene, ScenesManifest, SourcesManifest
from app.pipeline.shots import pacing_warnings
from app.pipeline.voice_production import produce_voice
from app.providers.alignment.base import TimedWord


def run(args: argparse.Namespace, context: Context) -> int:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # pesos já em cache: a voz local não acessa a rede
    store, episode_id = context.store, args.episode_id
    episode_dir = store.path(episode_id, "")
    scenes = store.read(episode_id, "scenes.json", ScenesManifest)
    sources = (
        store.read(episode_id, "sources.json", SourcesManifest)
        if store.exists(episode_id, "sources.json")
        else None
    )
    started = time.monotonic()
    wavs = produce_voice(select_tts(context, args.voz_final, args.voz), scenes, store, episode_id)
    episode_scenes = build_scenes(scenes, wavs, episode_dir, sources)
    total = sum(scene.duration_ms for scene in episode_scenes)
    for scene in episode_scenes:
        print(_scene_line(scene))
    print(f"voz: {time.monotonic() - started:.0f} s; total {total / 1000:.1f} s")

    guard = ReviewWriteGuard(store, context.review)
    _captions(
        episode_dir,
        episode_scenes,
        wavs,
        total,
        lambda text: guard.check(episode_id, "captions.srt", text.encode()),
    )
    _word_captions(context, episode_dir, episode_scenes, scenes.language, args.legenda_palavra)
    episode = build_episode(scenes, episode_scenes)
    episode = with_music(episode, music_segments(context.settings.data_dir, episode_dir, episode))
    if episode.music:
        print(f"trilha: {len(episode.music)} trecho(s), {len({m.asset_id for m in episode.music})} faixa(s)")
    print("ritmo:", pacing_warnings(episode) or "ok")
    return _render(args, context, EpisodeRenderer(store, guard, context.renderer), scenes, episode)


def _scene_line(scene: EpisodeScene) -> str:
    summary = ", ".join(f"{s.spec.kind} {s.duration_ms / 1000:.1f}" for s in scene.shots)
    return f"{scene.id}: {scene.duration_ms / 1000:5.2f} s | {summary}"


def _captions(
    episode_dir: Path,
    scenes: list[EpisodeScene],
    wavs: dict[str, Path],
    total_ms: int,
    before_change: Callable[[str], None],
) -> None:
    report = write_captions(episode_dir, scenes, wavs, total_ms, before_change)
    proportional = f"{report.approximate} fronteira(s) no tempo proporcional"
    print(f"legenda: {report.note}; {report.blocks} blocos, {proportional}")
    for number, hint in report.hints:
        print(f"  revisar bloco {number}: {hint}")


def _word_captions(
    context: Context, episode_dir: Path, scenes: list[EpisodeScene], language: str, requested: bool
) -> None:
    recognize = None
    if requested:
        aligner = context.word_aligner  # remoto: só construído quando o dono pediu

        def recognize(scene: SceneSpeech) -> list[TimedWord]:
            return aligner.recognize_words(
                episode_dir / scene.audio, language, prompt=strip_pauses(scene.narration)
            )

    settings = context.settings
    name = f"{settings.providers.word_aligner}/{settings.groq_whisper.model}"
    report = write_word_captions(episode_dir, scenes, recognize, name)
    if report is None:
        return
    print(
        f"legenda palavra a palavra: {len(report.with_words)} cena(s), {report.unmatched} palavra(s) com "
        "tempo dividido entre as vizinhas"
    )
    if report.without:
        print(
            f"  sem reconhecimento (ficam na legenda por frase): {', '.join(report.without)}; "
            "rode com --legenda-palavra"
        )


def _render(
    args: argparse.Namespace,
    context: Context,
    renderer: EpisodeRenderer,
    scenes: ScenesManifest,
    episode: EpisodeManifest,
) -> int:
    if args.no_render:
        renderer.assemble(args.episode_id, scenes, episode)
        return 0
    started = time.monotonic()
    result = renderer.render(args.episode_id, scenes, episode, preview=args.preview)
    print(f"render: {time.monotonic() - started:.0f} s -> {result.path} ({result.duration_ms / 1000:.1f} s)")
    if episode.music:
        lufs = integrated_lufs(result.path)
        problem = loudness_problem(lufs)
        print(f"volume: {lufs:.1f} LUFS", f"— alerta: {problem}" if problem else "ok")
    return 0
