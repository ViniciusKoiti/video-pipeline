from collections.abc import Iterator
from typing import Literal

from torch import Tensor

class KPipeline:
    class Result:
        graphemes: str
        phonemes: str
        @property
        def audio(self) -> Tensor | None: ...
        def __getitem__(self, index: Literal[2]) -> Tensor | None: ...

    def __init__(self, lang_code: str, repo_id: str) -> None: ...
    def __call__(self, text: str, voice: str) -> Iterator[Result]: ...
