"""`vp short sfx <pasta> <content.voz.json> <narracao.json> <sfx.json>`: confere o plano de efeitos.

Confere o `sfx.json` contra o SFX Kit (`data/sfx/kit/`), as cenas e as falas (ADR 035) e lista onde cada
som cai, sem misturar nada. O primeiro erro do plano para a execução; alerta não para.
"""

from __future__ import annotations

import argparse

from app.pipeline.motion_inputs import load_content
from app.pipeline.ports import Context
from app.pipeline.short_timing import resolve_effects, voiced


def run(args: argparse.Namespace, context: Context) -> int:
    content = load_content(args.content)
    wavs = voiced(args.folder, args.narration)
    data_dir = context.settings.data_dir
    placed, voice_lufs = resolve_effects(data_dir, content, args.narration, args.plan, wavs, print)
    print(f"voz medida: {voice_lufs:.1f} LUFS (o kit assume −16)" if voice_lufs is not None else "sem voz")
    for p in placed:
        under = " sob a fala" if p.under_speech else ""
        print(f"  {p.moment_s:6.2f} s  {p.sound:32} começa em {p.start_s:6.2f} s  {p.gain_db:+.1f} dB{under}")
    print(f"sfx: {len(placed)} efeito(s), sem erro")
    return 0
