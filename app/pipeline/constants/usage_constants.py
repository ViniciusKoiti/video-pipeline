"""Constantes de usage; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class UsageConstants:
    TOKEN_FIELDS: Final = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")
