"""As conferências do Short (emenda de 2026-11-17 da ADR 062), as mesmas do longo, nas linhas da narração.

- `check_short_text`, antes da primeira voz (`vp short checar`): rótulo de opinião é erro; termo de fora sem
  entrada em `voice/glossary.json` (e sem `ipa`, com a voz do Azure) é ponto de atenção; dois-pontos sem
  `<short pause>` antes de pergunta é alerta.
- `voiced_lines`, depois da voz (`vp short conferir`): o WAV que vai ao vídeo de cada linha, pelo registro
  `<narração>.voz.json` que `vp short voz` escreveu. Se o texto mudou depois da voz, a conferência para:
  ouvir a fala velha contra o texto novo apontaria diferenças que não existem.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.errors import PipelineError
from app.media.pronunciation import Glossary
from app.pipeline.constants.short_speech_constants import ShortSpeechConstants as Constants
from app.pipeline.glossary_check import colon_pause_lines, glossary_lines
from app.pipeline.models.check_report import CheckReport
from app.pipeline.models.narration import Narration
from app.pipeline.opinion_labels import opinion_label_lines
from app.pipeline.short.voice import speech_lines
from app.pipeline.speech_review import Heard


class ShortSpeechError(PipelineError, ValueError):
    """Falta a voz do Short, ou a narração mudou depois dela."""


def spoken_lines(narration: Narration) -> list[tuple[str, str]]:
    """O id de cada fala (a cena, ou `fora-N`, como no nome do WAV) e o texto dela."""
    return [(line.id, line.text) for line in speech_lines(narration)]


def check_short_text(narration: Narration, glossary: Glossary, voice: str | None) -> CheckReport:
    """As regras de texto do `vp check` nas falas do Short; `voice` é a voz que vai gerar a fala."""
    spoken = spoken_lines(narration)
    report = CheckReport()
    report.errors += opinion_label_lines(spoken)
    report.warnings += colon_pause_lines(spoken)
    report.attention += glossary_lines([text for _, text in spoken], narration.language, glossary, voice)
    return report


def record_path(folder: Path, narration_path: Path) -> Path:
    return folder / f"{narration_path.stem}{Constants.RECORD_SUFFIX}"


def voiced_lines(folder: Path, narration: Narration, record: Path) -> list[Heard]:
    """Cada fala com o texto e o WAV do registro, conferidos contra a narração atual."""
    if not record.is_file():
        raise ShortSpeechError(f"falta {record.name}: rode `vp short voz` antes de conferir")
    data = json.loads(record.read_text(encoding="utf-8"))
    entries = data.get("lines") if isinstance(data, dict) else None
    spoken = spoken_lines(narration)
    if not isinstance(entries, list) or [entry.get("text") for entry in entries] != [t for _, t in spoken]:
        raise ShortSpeechError(
            f"{record.name} não bate com a narração (texto mudado depois da voz?): rode `vp short voz` antes"
        )
    lines: list[Heard] = []
    for (line_id, text), entry in zip(spoken, entries, strict=True):
        wav = folder / str(entry.get("wav", ""))
        if not wav.resolve().is_relative_to(folder.resolve()) or not wav.is_file():
            where = entry.get("wav")
            raise ShortSpeechError(f"{record.name}: a fala de {line_id} ({where}) não está na pasta")
        lines.append((line_id, text, wav))
    return lines
