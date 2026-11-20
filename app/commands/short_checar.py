"""`vp short checar <pasta> <narracao.json>`: a porta do texto do Short antes da primeira voz (ADR 062,
emenda de 2026-11-17).

As regras de texto do `vp check` nas linhas da narração (`app/pipeline/short/speech.py`): rótulo de opinião é
erro (saída 1); termo de fora sem entrada em `<pasta>/voice/glossary.json`, ou sem `ipa` com a voz do Azure,
é ponto de atenção; dois-pontos sem `<short pause>` antes de pergunta é alerta. A voz considerada é a do vídeo
final (`tts_final`), a mesma que `vp short voz` usa sem `--voz`. Cada fala refeita custa uma chamada à voz:
o texto se acerta antes.
"""

from __future__ import annotations

import argparse

from app.media.pronunciation import load_glossary
from app.pipeline.models.check_report import CheckReport
from app.pipeline.motion_inputs import load_narration
from app.pipeline.ports import Context
from app.pipeline.short.speech import check_short_text


def print_report(report: CheckReport) -> None:
    for line in report.warnings:
        print(f"alerta  {line}")
    for line in report.attention:
        print(f"atenção {line}")
    for line in report.errors:
        print(f"erro    {line}")


def run(args: argparse.Namespace, context: Context) -> int:
    narration = load_narration(args.narration)
    providers = context.settings.providers
    report = check_short_text(narration, load_glossary(args.folder), providers.tts_final or providers.tts)
    print_report(report)
    attention = f"; {len(report.attention)} ponto(s) de atenção" if report.attention else ""
    errors = "sem erros" if report.ok else f"{len(report.errors)} erro(s)"
    print(f"texto do Short: {len(narration.lines)} fala(s), {errors}{attention}")
    return 0 if report.ok else 1
