from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class VoiceLevelReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    source: Path
    source_sha256: str
    wav_sha256: str
    policy: str
    target_lufs: float
    input_lufs: float
    output_lufs: float
    true_peak_dbtp: float
