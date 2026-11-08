from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from app.settings.models.settings import Settings

T_co = TypeVar("T_co", covariant=True)


Factory = Callable[[Settings], T_co]
