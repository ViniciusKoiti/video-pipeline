from pathlib import Path

from torch import Tensor

def save(
    uri: str | Path, src: Tensor, sample_rate: int, *, encoding: str, bits_per_sample: int
) -> None: ...
