"""A voz de um Short, uma fala por linha da narração (RF7; eram `generate_voice` e `cmd_voz` de
`shorts_tec.py`).

Cada linha vira um WAV `voice/<cena>-<provedor>-<hash>.wav` da pasta de produção (a cena, ou `fora-N` para a
fala de um plano fora do JSON do `motion-video`). Só as que faltam são geradas e a antiga só sai depois da
nova pronta e medida (ADR 049); falta de fala é `VoiceIncomplete`. O relatório por cena fica no
`manifest.json` da pasta (ADR 052). O registro `<narração>.voz.json` guarda, por linha, o WAV, a duração e
o trecho falado: é o que `tempos`, `juntar` e `boca` leem (`app/pipeline/motion_inputs.py`).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from app.errors import PipelineError
from app.media.probe import duration_ms
from app.media.pronunciation import load_glossary, respell
from app.pipeline.models.naming import Naming
from app.pipeline.models.narration import Narration
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.ports import ManifestStore
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state
from app.providers.tts.base import TTSProvider, closing_tts

Bounds = Callable[[Path], tuple[float, float]]


class ShortFolderError(PipelineError, ValueError):
    """A pasta de produção não é uma pasta de episódio do projeto."""


def production_id(store: ManifestStore, folder: Path) -> str:
    """O id da pasta de produção (o nome dela), que tem de ser uma pasta de episódios do `store`: é ali que
    ficam o estado da voz (`manifest.json`), o `review.json` e o glossário."""
    episode_id = folder.name
    where = store.path(episode_id, "")
    if where.resolve() != folder.resolve():
        raise ShortFolderError(
            f"{folder}: a pasta de produção do Short fica na pasta de episódios ({where.parent}), "
            "como data/episodes/<id>"
        )
    return episode_id


def speech_lines(narration: Narration) -> list[SpeechLine]:
    """As falas a gerar, na ordem; a sem cena leva o número da linha (`fora-1`)."""
    return [
        SpeechLine(line.scene or f"fora-{index}", line.text, line.delivery or "neutral")
        for index, line in enumerate(narration.lines)
    ]


def produce_short_voice(
    tts: TTSProvider, narration: Narration, store: ManifestStore, episode_id: str
) -> list[Path]:
    """O WAV de cada linha da narração, na ordem, com a voz `tts`. A pasta é o "episódio" do estado."""
    folder = store.path(episode_id, "")
    voice_dir = folder / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    glossary = load_glossary(folder)
    narrator = Narrator(
        tts,
        narration.language,
        VoiceLibrary(voice_dir, Naming.SHORT),
        lambda wav: duration_ms(wav) / 1000,
        lambda text: respell(text, glossary),
    )
    speech = speech_lines(narration)
    with closing_tts(tts):  # a voz clonada mantém um processo com o modelo carregado
        outcomes = produce_with_state(narrator, store, episode_id, speech, now=datetime.now().astimezone())
        wavs = narrator.require(outcomes)
    return [wavs[item.id] for item in speech]


def voice_entries(narration: Narration, wavs: list[Path], bounds: Bounds) -> list[dict[str, Any]]:
    """O registro de cada fala: o WAV, a duração e o trecho falado dentro dele (`bounds`)."""
    entries = []
    for line, wav in zip(narration.lines, wavs, strict=True):
        begin, end = bounds(wav)
        entries.append(
            {
                "scene": line.scene,
                "text": line.text,
                "delivery": line.delivery or "neutral",
                "wav": f"voice/{wav.name}",
                "seconds": duration_ms(wav) / 1000,
                "speech": [round(begin, 3), round(end, 3)],
            }
        )
    return entries


def write_voice_record(path: Path, language: str, provider: str, entries: list[dict[str, Any]]) -> None:
    body = {"language": language, "provider": provider, "lines": entries}
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
