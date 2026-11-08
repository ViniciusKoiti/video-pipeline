"""Constantes do conteúdo do `motion-video` e da fala do Short; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class MotionConstants:
    # folga depois da fala, antes do corte da cena
    PAD_SEC: Final[float] = 0.3
    # cenas sem a janela do apresentador (motion-video)
    HOST_HIDDEN_TYPES: Final = ("hook", "end_card", "presenter")
    DEFAULT_FPS: Final[int] = 30
    # a duração de cena sobe para o décimo de segundo acima, descontado o erro de ponto flutuante
    FIT_GRID: Final[int] = 10
    FIT_EPSILON: Final[float] = 1e-9
    # o trecho falado de um WAV pode passar do fim medido por esse tanto (arredondamento do ffprobe)
    SPEECH_SLACK_S: Final[float] = 0.05
