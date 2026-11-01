from typing import Self

from torch import Tensor

class ChatterboxMultilingualTTS:
    sr: int
    @classmethod
    def from_pretrained(cls, *, device: str, t3_model: str) -> Self: ...
    def generate(
        self, text: str, *, language_id: str, audio_prompt_path: str,
        exaggeration: float, cfg_weight: float
    ) -> Tensor: ...
