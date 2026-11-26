"""Emenda de 2026-11-26 da ADR 007: clipe gerado pelo dono (Google Flow) como ativo `Generated`.

O modelo aceita `media: clip` com a licença Generated quando o provider é original e há origin
(gerador, modelo e projeto) e usage_notes (prompt e conferência). Timecode continua só do clipe citado.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.pipeline.models.provider import Provider
from app.pipeline.models.status import Status
from app.pipeline.schemas import Asset

NOW = datetime(2026, 11, 26, 15, 0, tzinfo=UTC)
ORIGIN = "Google Flow (conta PRO do dono), Omni 1.2 Flash, projeto c821cb8e"
NOTES = "prompt em prompts-flow.md (clipe 1); sem pessoa real, marca nem texto (conferido nos quadros)"


def generated_clip(**kw: object) -> Asset:
    base = {
        "id": "flow-clipe-1",
        "provider": Provider.ORIGINAL,
        "provider_id": "clipe-1.mp4",
        "license_id": "Generated",
        "origin": ORIGIN,
        "usage_notes": NOTES,
        "media": "clip",
        "retrieved_at": NOW,
        "review_status": Status.NEEDS_REVIEW,
    }
    return Asset.model_validate({**base, **kw})


def approved(asset: Asset) -> dict[str, object]:
    return {**asset.model_dump(), "review_status": Status.APPROVED, "sha256": "b" * 64}


def test_a_generated_clip_with_origin_and_notes_can_be_approved() -> None:
    clip = Asset.model_validate(approved(generated_clip()))
    assert (clip.media, clip.license_id, clip.is_synthetic) == ("clip", "Generated", False)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"origin": None}, "origin"),
        ({"origin": "  "}, "origin"),
        ({"usage_notes": ""}, "usage_notes"),
        ({"timecode": "00:00:01-00:00:02"}, "timecode"),
        ({"provider": Provider.PEXELS, "page_url": "https://example.org/x"}, "provider original"),
    ],
)
def test_a_generated_clip_missing_its_proof_cannot_be_approved(
    change: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        Asset.model_validate(approved(generated_clip(**change)))


def test_a_generated_clip_waiting_for_review_does_not_need_the_proof_yet() -> None:
    assert generated_clip(origin=None, usage_notes="").review_status is Status.NEEDS_REVIEW


def test_a_generated_still_keeps_working_without_origin() -> None:
    still = Asset.model_validate(approved(generated_clip(media="still", origin=None)))
    assert still.media == "still"
