"""`vp short voz <pasta> <narracao.json> [--voz NOME]`: a fala de cada linha da narração do Short.

Uma fala por linha, em `<pasta>/voice/<cena>-<provedor>-<hash>.wav`. A voz padrão é a do vídeo final
(`tts_final`, a clonada do dono no Modal, ADR 024); `--voz kokoro` dá um rascunho local. O hash cobre o
texto, o provedor, o modelo, a gravação de referência e a entrega: a fala só é gerada de novo quando um deles
muda. Com um `<pasta>/voice/glossary.json` (§9), a voz lê a grafia do glossário ("JSON" → "jêison") e o hash
cobre esse texto; a tela e a legenda ficam com a grafia da narração.

Escreve `<narracao>.voz.json` (WAV, duração e trecho falado de cada linha) para `tempos`, `juntar` e `boca`.

Antes de gerar, imprime o que `vp short checar` apontaria no texto, sem parar (a porta do texto é o
`checar`). `--refazer gancho fora-2` guarda a fala atual dessas linhas, nesta voz, em
`voice/tomadas-recusadas/<data>/` e gera outra (ADR 062, emenda de 2026-11-17); a fala de uma linha sem cena
é `fora-N`, com N a posição dela na narração, a contar de zero.
"""

from __future__ import annotations

import argparse
import os
import time
from datetime import datetime

from app.commands.short_checar import print_report
from app.media.pronunciation import load_glossary
from app.media.speech_bounds import speech_bounds
from app.pipeline.constants.voice_retake_constants import VoiceRetakeConstants as RetakeConstants
from app.pipeline.motion_inputs import load_narration
from app.pipeline.ports import Context
from app.pipeline.short.speech import check_short_text
from app.pipeline.short.voice import (
    produce_short_voice,
    production_id,
    speech_lines,
    voice_entries,
    write_voice_record,
)
from app.pipeline.voice_retake import set_aside


def run(args: argparse.Namespace, context: Context) -> int:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # pesos já em cache: a voz local não acessa a rede
    settings = context.settings
    narration = load_narration(args.narration)
    if args.voz:
        provider, tts = args.voz, context.tts_named(args.voz)
    else:
        provider, tts = settings.providers.tts_final or settings.providers.tts, context.tts_final
    started = time.monotonic()
    episode_id = production_id(context.store, args.folder)  # a pasta é o "episódio" do estado
    print_report(check_short_text(narration, load_glossary(args.folder), provider))  # avisa, não para
    if args.refazer:
        known = [line.id for line in speech_lines(narration)]
        voice_dir = args.folder / "voice"
        moved = set_aside(voice_dir, args.refazer, known, tts.identity, datetime.now().astimezone())
        print(f"tomada anterior guardada: {len(moved)} arquivo(s) em voice/{RetakeConstants.REJECTED_DIR}/")
    wavs = produce_short_voice(
        tts, narration, context.store, episode_id, polish=settings.voice_polish.active()
    )
    entries = voice_entries(narration, wavs, speech_bounds, tts, args.folder)
    for entry in entries:
        begin, end = entry["speech"]
        name = entry["wav"].removeprefix("voice/")
        print(
            f"{entry['scene'] or 'fora':16s} {entry['seconds']:5.2f} s (fala {begin:.2f}–{end:.2f})  {name}"
        )
        if reference := entry.get("reference"):
            print(f"  referência: {reference['file']} ({reference['sha256'][:12]})")
        if level := entry.get("level"):
            print(f"  volume: {level['input_lufs']:.1f} → {level['output_lufs']:.1f} LUFS")
    out = args.folder / f"{args.narration.stem}.voz.json"
    write_voice_record(out, narration.language, provider, entries)
    spoken = sum(entry["speech"][1] - entry["speech"][0] for entry in entries)
    print(
        f"voz: {len(entries)} fala(s), {spoken:.1f} s de fala, {time.monotonic() - started:.0f} s; "
        f"registro em {out.name}"
    )
    return 0
