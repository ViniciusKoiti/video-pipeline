from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, StringConstraints

Identifier = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=512)
]


Count = Annotated[int, Field(strict=True, ge=0, le=2**63 - 1)]


Metric = Literal["tokens_total", "cost_usd_micros"]


TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")
