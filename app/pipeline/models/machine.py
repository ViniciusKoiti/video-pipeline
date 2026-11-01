from __future__ import annotations

from pydantic import BaseModel


class Machine(BaseModel):
    cpu_model: str
    cpus: int
    mem_total_mb: int
    mem_available_mb: int
    load_1m: float
    python: str
    cpu_probe_s: float = 0.0  # tempo da sonda de CPU (sha256 de 64 MB)
    busy: bool
