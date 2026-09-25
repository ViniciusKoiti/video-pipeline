import pytest

from app.pipeline.failures import for_each_scene
from app.pipeline.schemas import Status
from app.providers.errors import ModelUnavailable, QuotaExhausted


def test_provider_error_stops_only_that_scene() -> None:
    def action(scene_id: str) -> str:
        if scene_id == "S02":
            raise QuotaExhausted("workers_ai", "cota diária esgotada")
        if scene_id == "S03":
            raise ModelUnavailable("workers_ai", "modelo aposentado")
        return f"{scene_id}.png"

    outcomes = for_each_scene(["S01", "S02", "S03", "S04"], action)
    assert [(o.scene_id, o.status, o.reason) for o in outcomes] == [
        ("S01", Status.COMPLETED, ""),
        ("S02", Status.NEEDS_REVIEW, "quota_exhausted"),
        ("S03", Status.NEEDS_REVIEW, "model_unavailable"),
        ("S04", Status.COMPLETED, ""),
    ]
    assert outcomes[0].value == "S01.png"
    assert outcomes[1].detail == "workers_ai: cota diária esgotada"


def test_bugs_are_not_swallowed() -> None:
    def action(scene_id: str) -> str:
        raise KeyError(scene_id)

    with pytest.raises(KeyError):
        for_each_scene(["S01"], action)
