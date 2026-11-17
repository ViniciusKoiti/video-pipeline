from __future__ import annotations

from app.pipeline.models.heard_difference import HeardDifference
from app.pipeline.models.model import Model
from app.pipeline.models.scene_hearing import SceneHearing


class SpeechReview(Model):
    """A conferência da fala de um episódio (`voice/conferencia.json`, ADR 062). Não aprova nada: aponta o que
    ouvir. O reconhecedor também erra, principalmente nome estrangeiro; a escuta do dono decide."""

    episode_id: str
    recognizer: str
    scenes: list[SceneHearing] = []

    @property
    def differences(self) -> list[HeardDifference]:
        """Termos do glossário primeiro, depois as palavras, na ordem das cenas."""
        found = [d for scene in self.scenes for d in scene.differences]
        return [d for d in found if d.kind == "termo"] + [d for d in found if d.kind == "palavra"]
