from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CheckReport:
    """`attention`: o que o dono decide no gate 2 (poucas linhas, impressas por último antes dos erros);
    `warnings`: o informativo, que não pede decisão."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    attention: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors
