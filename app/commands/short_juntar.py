"""`vp short juntar <pasta> <video.mp4> <content.voz.json> <narracao.json> --saida MP4 [--sfx sfx.json]`.

Põe cada fala no começo da cena dela, sobre o MP4 silencioso do `motion-video render`, em estéreo e com o
volume no alvo do projeto (−14 LUFS, medido como o YouTube mede). Um render com som dentro (um vídeo tocando
na montagem) entra na mistura. Com `--sfx`, mistura também os efeitos do plano (ADR 035,
`app/pipeline/sfx.py`): cada um no momento da cena menos o `sync.at` do kit, abaixado onde cai sobre a fala.
A saída é um arquivo novo; o MP4 de entrada não muda.
"""

from __future__ import annotations

import argparse

from app.media.loudness import integrated_lufs, loudness_problem
from app.media.probe import duration_ms
from app.media.short_mix import has_audio, mix_audio
from app.pipeline.motion_inputs import load_content
from app.pipeline.ports import Context
from app.pipeline.short_join import join_command, ordered_speech
from app.pipeline.short_timing import resolve_effects, voiced


def run(args: argparse.Namespace, context: Context) -> int:
    content = load_content(args.content)
    wavs = voiced(args.folder, args.narration)
    ordered = ordered_speech(content, wavs)
    effects = []
    if args.sfx:
        data_dir = context.settings.data_dir
        effects = resolve_effects(data_dir, content, args.narration, args.sfx, wavs, print)[0]
    video_audio = has_audio(args.video)  # sem áudio no render, só as falas
    command = join_command(
        args.video, args.saida, content, wavs, ordered, effects, duration_ms(args.video) / 1000, video_audio
    )
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    mix_audio(command)
    lufs = integrated_lufs(args.saida)
    problem = loudness_problem(lufs)
    print(
        f"juntar: {args.saida} ({duration_ms(args.saida) / 1000:.1f} s), {len(ordered)} fala(s)"
        f"{' + o áudio do render' if video_audio else ''}"
        f"{f' + {len(effects)} efeito(s)' if effects else ''}; volume {lufs:.1f} LUFS",
        f"— alerta: {problem}" if problem else "ok",
    )
    return 0
