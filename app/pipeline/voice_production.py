"""A voz de um episódio longo, cena por cena (RF7; era `generate_voice` de `montar_episodio.py`).

O WAV de cada cena é gerado só se faltar, em lote quando a voz oferece, e o antigo só sai depois do novo
pronto e medido (ADR 049). Falta de fala é `VoiceIncomplete`; as prontas ficam para a próxima rodada. O
relatório por cena fica no `manifest.json` (ADR 052) e o `vp status` o mostra. O glossário de pronúncia do
episódio (`voice/glossary.json`) troca a grafia só no texto enviado à voz.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.media.probe import duration_ms
from app.media.pronunciation import load_glossary, respell
from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.ports import ManifestStore
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state
from app.providers.tts.base import ReferencedTTS, TTSProvider, closing_tts


def produce_voice(
    tts: TTSProvider, scenes: ScenesManifest, store: ManifestStore, episode_id: str
) -> dict[str, Path]:
    """O WAV de cada cena, por id, com a voz `tts`."""
    voice_dir = store.path(episode_id, "voice")
    voice_dir.mkdir(parents=True, exist_ok=True)
    glossary = load_glossary(store.path(episode_id, ""))
    narrator = Narrator(
        tts,
        scenes.language,
        VoiceLibrary(voice_dir, Naming.LONG),
        lambda wav: duration_ms(wav) / 1000,
        lambda text: respell(text, glossary),  # a grafia que a voz lê; sem termo, o texto do roteiro
    )
    lines = [SpeechLine(scene.id, scene.narration, scene.delivery or "neutral") for scene in scenes.scenes]
    with closing_tts(tts):  # a voz clonada mantém um processo com o modelo carregado
        outcomes = produce_with_state(
            narrator, store, episode_id, lines, now=datetime.now().astimezone(),
            level=isinstance(tts, ReferencedTTS) and tts.scene_references,
        )
        return narrator.require(outcomes)
