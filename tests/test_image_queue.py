"""Fila do `vp imagens` (era scripts/provisorio/fila_imagens.py): pedidos, registro e o que falta."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.pipeline.file_hash import sha256_file
from app.pipeline.models.image_order import ImageOrder
from app.pipeline.visuals import image_queue as queue
from app.providers.image_gen.base import GeneratedImage
from app.providers.image_gen.image_bytes import write_image

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPG = b"\xff\xd8\xff\xe0" + b"1" * 32


def orders_file(tmp_path: Path, items: list[dict[str, object]]) -> Path:
    path = tmp_path / "pedidos.json"
    path.write_text(json.dumps(items), encoding="utf-8")
    return path


def save(out: Path, order: ImageOrder, data: bytes, origin: str = "") -> Path:
    """O que o gerador faz (grava com a extensão dos bytes) seguido do registro da fila."""
    path = write_image("gemini", queue.target(out, order), data)
    queue.record_generated(out, order, GeneratedImage(path=path, generator="gemini", origin=origin))
    return path


def test_reads_orders_and_resolves_refs_from_the_file_folder(tmp_path: Path) -> None:
    (tmp_path / "folha.png").write_bytes(PNG)
    path = orders_file(
        tmp_path, [{"id": "s01-loja", "prompt": " uma loja ", "refs": ["folha.png"], "cena": "S01"}]
    )
    [order] = queue.read_orders(path)
    assert order == ImageOrder("s01-loja", "uma loja", (tmp_path / "folha.png",), "S01")


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{"id": "S01 Loja", "prompt": "x"}],
        [{"id": "../fora", "prompt": "x"}],
        [{"id": "s01", "prompt": "  "}],
        [{"id": "s01", "prompt": "x"}, {"id": "s01", "prompt": "y"}],
        [{"id": "s01", "prompt": "x", "refs": ["nao-existe.png"]}],
        [{"id": "s01", "prompt": "x", "cena": "3"}],
    ],
)
def test_refuses_invalid_orders(tmp_path: Path, items: list[dict[str, object]]) -> None:
    with pytest.raises(queue.ImageQueueError):
        queue.read_orders(orders_file(tmp_path, items))


def test_saved_image_leaves_the_pending_list_with_the_old_log_format(tmp_path: Path) -> None:
    path = orders_file(tmp_path, [{"id": "a", "prompt": "x", "cena": "S02"}, {"id": "b", "prompt": "y"}])
    orders, out = queue.read_orders(path), tmp_path / "saida"
    saved = save(out, orders[0], JPG, origin="https://gemini.google.com/app/abc")
    assert saved.name == "a.jpg" and saved.read_bytes() == JPG and not list(out.glob("*.tmp"))
    assert [order.id for order in queue.pending(orders, out)] == ["b"]
    [line] = queue.read_log(out)
    assert {k: line[k] for k in ("id", "estado", "site", "arquivo", "sha256", "cena", "conversa")} == {
        "id": "a",
        "estado": "gerada",
        "site": "gemini",
        "arquivo": "a.jpg",
        "sha256": sha256_file(saved),
        "cena": "S02",
        "conversa": "https://gemini.google.com/app/abc",
    }


def test_log_written_by_the_old_script_still_counts_as_ready(tmp_path: Path) -> None:
    out = tmp_path / "saida"
    out.mkdir()
    (out / "a.png").write_bytes(PNG)
    old = {
        "id": "a",
        "estado": "gerada",
        "site": "gemini",
        "arquivo": "a.png",
        "sha256": sha256_file(out / "a.png"),
        "prompt": "x",
        "refs": [],
        "data": "2026-11-12T16:15:58-03:00",
    }
    (out / "registro.jsonl").write_text(json.dumps(old) + "\n", encoding="utf-8")
    assert queue.ready(out) == {"a"}


def test_failure_missing_or_changed_file_stay_pending(tmp_path: Path) -> None:
    orders = queue.read_orders(
        orders_file(tmp_path, [{"id": i, "prompt": "x"} for i in ("falhou", "sumiu", "mudou")])
    )
    out = tmp_path / "saida"
    queue.record_failure(out, orders[0], "gemini", "sem imagem nova em 180 s")
    save(out, orders[1], PNG).unlink()
    save(out, orders[2], PNG).write_bytes(JPG)
    assert [order.id for order in queue.pending(orders, out)] == ["falhou", "sumiu", "mudou"]
    assert queue.read_log(out)[0] | {"data": ""} == {
        "id": "falhou",
        "estado": "falhou",
        "site": "gemini",
        "motivo": "sem imagem nova em 180 s",
        "data": "",
    }
