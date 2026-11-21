"""Teto (§6) e rodada do `vp imagens gerar`, com geradores falsos (sem navegador)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.pipeline.models.image_order import ImageOrder
from app.pipeline.visuals import image_queue as queue
from app.pipeline.visuals.image_round import ceiling_problems, run_round
from app.providers.base import ProviderInfo
from app.providers.errors import AccessBlocked, InvalidOutput, PaidApiBlocked
from app.providers.image_gen.base import CostEstimate, GeneratedImage, ImageRequest
from tests.fakes import FakeImageGen

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class Scripted:
    """Gerador que responde na ordem dada: bytes viram imagem, exceção é levantada."""

    def __init__(self, *answers: bytes | Exception, usd: float = 0.0) -> None:
        self.info = ProviderInfo("gemini", remote=True)
        self.answers, self.usd, self.requests = list(answers), usd, []  # type: ignore[var-annotated]

    def estimate_cost(self, request: ImageRequest) -> CostEstimate:
        return CostEstimate(units=1.0, unit="imagem", usd=self.usd)

    def generate_image(self, request: ImageRequest) -> GeneratedImage:
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        path = request.out_path.with_suffix(".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(answer)
        return GeneratedImage(path=path, generator="gemini")

    def close(self) -> None:
        return None


def orders(*ids: str, scene: str | None = None) -> list[ImageOrder]:
    return [ImageOrder(ident, f"prompt {ident}", scene=scene) for ident in ids]


def run(provider: object, batch: list[ImageOrder], out: Path, sleeps: list[float] | None = None) -> int:
    pauses = [] if sleeps is None else sleeps
    return run_round(provider, batch, out, interval_s=45, report=lambda _: None, sleep=pauses.append)  # type: ignore[arg-type]


def test_ceiling_counts_ready_images_and_the_batch(tmp_path: Path) -> None:
    out = tmp_path / "saida"
    run(FakeImageGen(), orders(*[f"p{i}" for i in range(10)]), out)
    batch = orders("x1", "x2", "x3")
    assert ceiling_problems(batch, batch, out, per_episode=12, per_scene=2) == [
        "13 imagens na pasta com esta rodada; o teto é 12 por episódio"
    ]
    assert ceiling_problems(batch[:2], batch[:2], out, per_episode=12, per_scene=2) == []


def test_ceiling_per_scene_uses_the_orders_and_the_log(tmp_path: Path) -> None:
    out = tmp_path / "saida"
    run(FakeImageGen(), orders("a", scene="S03"), out)
    batch = orders("b", "c", scene="S03") + orders("d", scene="S04")
    assert ceiling_problems(batch, batch, out, per_episode=12, per_scene=2) == [
        "S03: 3 imagens; o teto é 2 por cena"
    ]


def test_round_pauses_between_orders_and_records_each_image(tmp_path: Path) -> None:
    sleeps: list[float] = []
    provider = Scripted(PNG, PNG)
    assert run(provider, orders("a", "b"), tmp_path, sleeps) == 2
    assert sleeps == [45] and queue.ready(tmp_path) == {"a", "b"}
    assert provider.requests[0].out_path == tmp_path / "a"


def test_order_without_image_is_recorded_and_the_round_goes_on(tmp_path: Path) -> None:
    provider = Scripted(InvalidOutput("gemini", "sem imagem nova em 180 s"), PNG)
    assert run(provider, orders("a", "b"), tmp_path) == 1
    assert [(line["id"], line["estado"]) for line in queue.read_log(tmp_path)] == [
        ("a", "falhou"),
        ("b", "gerada"),
    ]


def test_two_failures_in_a_row_stop_the_round(tmp_path: Path) -> None:
    provider = Scripted(InvalidOutput("gemini", "x"), InvalidOutput("gemini", "y"), PNG)
    with pytest.raises(queue.ImageQueueError, match="2 falhas seguidas; conferir seletores"):
        run(provider, orders("a", "b", "c"), tmp_path)
    assert len(provider.answers) == 1


def test_blocked_access_is_recorded_and_stops_at_once(tmp_path: Path) -> None:
    provider = Scripted(AccessBlocked("gemini", "o site mostrou 'atingiu o limite'; rodada parada"), PNG)
    with pytest.raises(AccessBlocked):
        run(provider, orders("a", "b"), tmp_path)
    [line] = queue.read_log(tmp_path)
    assert line["estado"] == "falhou" and "atingiu o limite" in line["motivo"]


def test_paid_generator_is_refused_before_generating(tmp_path: Path) -> None:
    provider = Scripted(PNG, usd=0.01)
    with pytest.raises(PaidApiBlocked):
        run(provider, orders("a"), tmp_path)
    assert provider.requests == []
