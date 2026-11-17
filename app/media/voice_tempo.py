"""Velocidade da fala por episódio (`voice/ritmo.json`; pedido do dono em 2026-11-15, `vazio-de-ter-tudo`).

A voz clonada sai rápida (~200 palavras por minuto) e mudar os parâmetros do Chatterbox não
desacelera de forma previsível: o modelo sorteia cada tomada. O que é estável é o `atempo` do
FFmpeg, que muda a velocidade sem mudar a altura. Ele entra na cópia nivelada (ADR 054), antes
do `loudnorm`, e o fator vai para a política do nivelamento: mudar a velocidade gera cópias novas
sem chamar o TTS de novo, e o WAV bruto fica como está. Sem o arquivo, a velocidade é a original
e a política (e o nome das cópias) não muda.
"""

from __future__ import annotations

from pathlib import Path

from app.media.constants.voice_tempo_constants import VoiceTempoConstants
from app.media.models.voice_tempo import VoiceTempo


def load_tempo(episode_dir: Path) -> float:
    """O fator de velocidade do episódio; sem `voice/ritmo.json`, 1,0 (a fala como saiu da voz)."""
    path = episode_dir / VoiceTempoConstants.FILE
    if not path.is_file():
        return VoiceTempoConstants.NEUTRAL
    return VoiceTempo.model_validate_json(path.read_text(encoding="utf-8")).tempo


def tempo_filter(tempo: float) -> str:
    """O trecho do filtro do FFmpeg para a velocidade, com a vírgula final; vazio na velocidade original."""
    if tempo == VoiceTempoConstants.NEUTRAL:
        return ""
    VoiceTempo(tempo=tempo)  # fora da faixa é erro antes de chegar ao FFmpeg
    return f"atempo={tempo:g},"


def tempo_policy(tempo: float) -> str:
    """O sufixo da política do nivelamento; vazio na velocidade original, para não mudar o nome das cópias."""
    return "" if tempo == VoiceTempoConstants.NEUTRAL else f":tempo-{tempo:g}"
