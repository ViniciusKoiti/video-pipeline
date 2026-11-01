from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PostText:
    """O texto do post lido do JSON do Postiz: o título (opcional) e a legenda."""

    title: str | None
    caption: str

    def render(self) -> str:
        """O `legenda-post.txt`: título, linha em branco e legenda; sem título, só a legenda."""
        return (f"{self.title}\n\n" if self.title else "") + self.caption + "\n"
