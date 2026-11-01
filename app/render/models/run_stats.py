from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunStats:
    rendered: list[str] = field(default_factory=list)
    reused: list[str] = field(default_factory=list)
