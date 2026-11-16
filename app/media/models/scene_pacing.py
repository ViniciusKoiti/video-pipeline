from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenePacing:
    """As pausas de uma cena: o silêncio de cada fim de frase interno, em ordem, e o da cauda (até a próxima
    cena)."""

    internal_s: tuple[float, ...]
    tail_s: float

    def policy(self) -> str:
        """O plano em texto, para a chave da cópia: muda o plano, muda o arquivo."""
        return ",".join(f"{value:.2f}" for value in (*self.internal_s, self.tail_s))
