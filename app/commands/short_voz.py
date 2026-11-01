"""`vp short voz <pasta> <narracao.json> [--voz NOME]`: a fala de cada linha da narração do Short.

Uma fala por linha, em `<pasta>/voice/<cena>-<provedor>-<hash>.wav`. A voz padrão é a do vídeo final
(`tts_final`, a clonada do dono no Modal, ADR 024); `--voz kokoro` dá um rascunho local. O hash cobre o
texto, o provedor, o modelo, a gravação de referência e a entrega: a fala só é gerada de novo quando um deles
muda. Com um `<pasta>/voice/glossary.json` (§9), a voz lê a grafia do glossário ("JSON" → "jêison") e o hash
cobre esse texto; a tela e a legenda ficam com a grafia da narração.

Escreve `<narracao>.voz.json` (WAV, duração e trecho falado de cada linha) para `tempos`, `juntar` e `boca`.
"""

from __future__ import annotations

import argparse
import os
import time

from app.media.speech_bounds import speech_bounds
from app.pipeline.motion_inputs import load_narration
from app.pipeline.ports import Context
from app.pipeline.short_voice import produce_short_voice, production_id, voice_entries, write_voice_record


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
    wavs = produce_short_voice(tts, narration, context.store, episode_id)
    entries = voice_entries(narration, wavs, speech_bounds)
    for entry in entries:
        begin, end = entry["speech"]
        name = entry["wav"].removeprefix("voice/")
        print(
            f"{entry['scene'] or 'fora':16s} {entry['seconds']:5.2f} s (fala {begin:.2f}–{end:.2f})  {name}"
        )
    out = args.folder / f"{args.narration.stem}.voz.json"
    write_voice_record(out, narration.language, provider, entries)
    spoken = sum(entry["speech"][1] - entry["speech"][0] for entry in entries)
    print(
        f"voz: {len(entries)} fala(s), {spoken:.1f} s de fala, {time.monotonic() - started:.0f} s; "
        f"registro em {out.name}"
    )
    return 0
