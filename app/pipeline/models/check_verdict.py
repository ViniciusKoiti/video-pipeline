from __future__ import annotations

from enum import StrEnum


class CheckVerdict(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
