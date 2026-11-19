"""`vp short conferir <pasta> <narracao.json>`: a conferência da fala pronta do Short (ADR 062, emenda de
2026-11-17).

O mesmo do `vp voice --conferir`, nas linhas da narração: o reconhecedor local (`speech_check` no
`providers.toml`) ouve o WAV de cada fala que `vp short voz` registrou em `<narração>.voz.json`, sem o texto
esperado, e compara com o texto e o glossário da pasta. Grava `voice/conferencia-<narração>.json` e, se houver
diferenças, a folha de escuta `voice/conferencia-<narração>-escuta.wav`. Não gera fala: a nova tomada é
`vp short voz <pasta> <narracao.json> --refazer <falas>`.
"""

from __future__ import annotations

import argparse
import os

from app.commands.voice_check import report_speech
from app.media.pronunciation import load_glossary
from app.pipeline.constants.short_speech_constants import ShortSpeechConstants as Constants
from app.pipeline.motion_inputs import load_narration
from app.pipeline.ports import Context
from app.pipeline.short_speech import record_path, voiced_lines
from app.pipeline.short_voice import production_id
from app.pipeline.speech_review import review_lines


def run(args: argparse.Namespace, context: Context) -> int:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # o modelo vem do cache; a conferência não baixa nada
    narration = load_narration(args.narration)
    episode_id = production_id(context.store, args.folder)
    folder = context.store.path(episode_id, "")
    lines = voiced_lines(folder, narration, record_path(args.folder, args.narration))
    glossary = load_glossary(folder)
    review = review_lines(context.speech_checker, episode_id, narration.language, lines, glossary, folder)
    stem = args.narration.stem
    files = (Constants.REPORT_FILE.format(stem=stem), Constants.SHEET_FILE.format(stem=stem))
    paths = {line_id: wav for line_id, _, wav in lines}
    retake = f"vp short voz {args.folder} {args.narration} --refazer"
    return report_speech(review, paths, folder, files, retake)
