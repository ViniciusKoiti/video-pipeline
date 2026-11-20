"""`vp imagens` (eram imagens_navegador.py e fila_imagens.py): plano, teto e rodada pelo contexto falso."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from app.cli import build_parser
from app.commands import imagens
from app.errors import PipelineError
from app.pipeline.visuals import image_queue as queue
from tests.fakes import FakeContext, FakeImageGen, InMemoryStore, make_settings


class Mapper(FakeImageGen):
    def __init__(self) -> None:
        super().__init__()
        self.closed = 0

    def map_page(self) -> list[str]:
        return [
            "url atual: https://gemini.google.com/app",
            "  prompt_box        1 elemento(s)  rich-textarea",
        ]

    def close(self) -> None:
        self.closed += 1


def context(tmp_path: Path, provider: FakeImageGen | None = None) -> FakeContext:
    built = FakeContext(settings=make_settings(tmp_path), store=InMemoryStore(tmp_path))
    built.image_gen = provider or FakeImageGen()
    return built


def orders(tmp_path: Path, count: int, scene: str | None = None) -> Path:
    items = [
        {"id": f"p{i}", "prompt": f"cena {i}", **({"cena": scene} if scene else {})} for i in range(count)
    ]
    path = tmp_path / "pedidos.json"
    path.write_text(json.dumps(items), encoding="utf-8")
    return path


def args(*argv: str) -> argparse.Namespace:
    return build_parser().parse_args(["imagens", *argv])


def test_plano_lists_pending_orders_and_the_ceiling(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = orders(tmp_path, 3, scene="S05")
    assert imagens.run(args("plano", str(path), "--saida", str(tmp_path / "saida")), context(tmp_path)) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "3 pedidos; 0 prontos; 3 pendentes"
    assert out[1] == "  p0  refs=0  cena 0"
    assert out[-1] == "acima do teto (§6): S05: 3 imagens; o teto é 2 por cena"


def test_gerar_makes_what_is_missing_and_is_idempotent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path, out = orders(tmp_path, 2), tmp_path / "saida"
    ctx = context(tmp_path)
    ctx.settings = ctx.settings.model_copy(
        update={"browser_image": ctx.settings.browser_image.model_copy(update={"interval_s": 0})}
    )
    assert imagens.run(args("gerar", str(path), "--saida", str(out)), ctx) == 0
    assert queue.ready(out) == {"p0", "p1"}
    assert imagens.run(args("gerar", str(path), "--saida", str(out)), ctx) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "nada pendente"


def test_gerar_refuses_above_the_ceiling_before_opening_the_generator(tmp_path: Path) -> None:
    path, out = orders(tmp_path, 13), tmp_path / "saida"
    with pytest.raises(
        queue.ImageQueueError, match="13 imagens .* o teto é 12 por episódio.*--acima-do-teto"
    ):
        imagens.run(args("gerar", str(path), "--saida", str(out)), context(tmp_path))
    assert not out.exists()


def test_acima_do_teto_goes_on_with_a_warning(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path, out = orders(tmp_path, 3, scene="S01"), tmp_path / "saida"
    ctx = context(tmp_path)
    ctx.settings = ctx.settings.model_copy(
        update={"browser_image": ctx.settings.browser_image.model_copy(update={"interval_s": 0})}
    )
    assert imagens.run(args("gerar", str(path), "--saida", str(out), "--acima-do-teto"), ctx) == 0
    assert "aviso: acima do teto (§6), por --acima-do-teto: S01: 3 imagens" in capsys.readouterr().err
    assert len(queue.ready(out)) == 3


def test_rodada_limits_the_batch_and_keeps_it_under_the_ceiling(tmp_path: Path) -> None:
    path, out = orders(tmp_path, 13), tmp_path / "saida"
    assert imagens.run(args("gerar", str(path), "--saida", str(out), "--rodada", "1"), context(tmp_path)) == 0
    assert queue.ready(out) == {"p0"}


def test_mapear_prints_the_page_and_closes_the_browser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mapper = Mapper()
    assert imagens.run(args("mapear"), context(tmp_path, mapper)) == 0
    assert capsys.readouterr().out.startswith("url atual: https://gemini.google.com/app\n")
    assert mapper.closed == 1


def test_mapear_needs_a_generator_with_a_page(tmp_path: Path) -> None:
    with pytest.raises(PipelineError, match="não tem página para mapear"):
        imagens.run(args("mapear"), context(tmp_path))
