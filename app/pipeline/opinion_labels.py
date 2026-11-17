"""Opinião dita sem rótulo (ADR 019, emenda de 2026-11-16).

A opinião do canal se diz de forma natural ("na minha leitura", "pelo menos é assim que eu enxergo", "eu
acho"), nunca com um rótulo que a anuncia: "e eu digo o que acho disso, como opinião" (S05 do
`vazio-de-ter-tudo`) cumpre a regra ao pé da letra e quebra o clima do ensaio. O `vp check` dá erro: a troca é
do roteirista, com a frase que o dono aprovar.
"""

from __future__ import annotations

import re
import unicodedata

from app.media.narration import strip_pauses
from app.pipeline.constants.opinion_labels_constants import OpinionLabelsConstants as Constants
from app.pipeline.schemas import ScenesManifest


def _plain(text: str) -> str:
    """Minúsculas e sem acento, letra por letra, para o trecho achado sair do texto original."""
    return "".join(unicodedata.normalize("NFD", char)[0] for char in text).lower()


def opinion_label_errors(scenes: ScenesManifest) -> list[str]:
    errors: list[str] = []
    for scene in scenes.scenes:
        text = strip_pauses(scene.narration)
        plain = _plain(text)
        found = next((m for p in Constants.PHRASES if (m := re.search(p, plain))), None)
        if found:
            said = text[found.start() : found.end()]
            errors.append(
                f"{scene.id}: rótulo de opinião ({said!r}); diga a opinião de forma natural, como "
                f"{Constants.INSTEAD} (ADR 019)"
            )
    return errors
