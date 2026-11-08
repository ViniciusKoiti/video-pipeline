from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    step: int  # etapa do roadmap (= issue #N) que implementa o comando
    takes_episode: bool = True
    add_arguments: Callable[[argparse.ArgumentParser], None] | None = None
