"""Fila e registro das imagens geradas (`vp imagens`, ADR 065; era scripts/provisorio/fila_imagens.py).

`pedidos.json`: lista de {"id": "s03-patio", "prompt": "...", "refs": ["folha.png"], "cena": "S03"}. `refs` e
`cena` são opcionais; os caminhos de `refs` valem a partir da pasta do pedidos.json; `cena` conta no teto por
cena (§6). Cada tentativa vira uma linha em `<saida>/registro.jsonl`, só acrescentada: estado `gerada` (com
arquivo e sha256) ou `falhou` (com o motivo). Um pedido está pronto quando tem linha `gerada` e o arquivo
existe com o mesmo sha256; rodar de novo só faz o que falta. Nada aqui registra ativo no episódio: as
imagens ficam fora do pipeline até o dono escolher (gate 3).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.errors import PipelineError
from app.pipeline.constants.image_queue_constants import ImageQueueConstants as Constants
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.image_order import ImageOrder
from app.providers.image_gen.base import GeneratedImage


class ImageQueueError(PipelineError, ValueError):
    pass


def read_orders(path: Path) -> list[ImageOrder]:
    if not path.is_file():
        raise ImageQueueError(f"{path} não existe")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ImageQueueError(f"{path} precisa ser uma lista de pedidos, não vazia")
    orders: list[ImageOrder] = []
    for index, item in enumerate(raw):
        order = _order(path.parent, index, item)
        if any(known.id == order.id for known in orders):
            raise ImageQueueError(f"pedido {index}: id {order.id!r} repetido")
        orders.append(order)
    return orders


def _order(folder: Path, index: int, item: dict[str, Any]) -> ImageOrder:
    ident, prompt = str(item.get("id", "")), str(item.get("prompt", "")).strip()
    if not Constants.ORDER_ID.match(ident):
        raise ImageQueueError(f"pedido {index}: id {ident!r} inválido (minúsculas, números e hífen)")
    if not prompt:
        raise ImageQueueError(f"pedido {ident}: prompt vazio")
    scene = item.get("cena")
    if scene is not None and not Constants.SCENE_ID.match(str(scene)):
        raise ImageQueueError(f"pedido {ident}: cena {scene!r} inválida (ex.: S03)")
    refs = tuple((folder / ref).resolve() for ref in item.get("refs", []))
    for ref in refs:
        if not ref.is_file():
            raise ImageQueueError(f"pedido {ident}: referência {ref} não existe")
    return ImageOrder(ident, prompt, refs, scene and str(scene))


def read_log(out: Path) -> list[dict[str, Any]]:
    path = out / Constants.LOG_FILE
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ready(out: Path) -> set[str]:
    """Ids com imagem gerada, arquivo presente e sha256 igual ao registrado."""
    done: set[str] = set()
    for line in read_log(out):
        if line.get("estado") != Constants.GENERATED:
            continue
        file = out / line["arquivo"]
        if file.is_file() and sha256_file(file) == line["sha256"]:
            done.add(line["id"])
    return done


def pending(orders: list[ImageOrder], out: Path) -> list[ImageOrder]:
    done = ready(out)
    return [order for order in orders if order.id not in done]


def target(out: Path, order: ImageOrder) -> Path:
    """Destino sem extensão: o gerador acrescenta a do arquivo que recebeu (.png, .jpg, .webp)."""
    return out / order.id


def record_generated(out: Path, order: ImageOrder, image: GeneratedImage) -> None:
    line: dict[str, Any] = {
        "id": order.id,
        "estado": Constants.GENERATED,
        "site": image.generator,
        "arquivo": image.path.name,
        "sha256": sha256_file(image.path),
        "prompt": order.prompt,
        "refs": [str(ref) for ref in order.refs],
    }
    if order.scene:
        line["cena"] = order.scene
    if image.origin:
        line["conversa"] = image.origin  # para reabrir a imagem no site, se preciso
    _append(out, line)


def record_failure(out: Path, order: ImageOrder, generator: str, reason: str) -> None:
    _append(out, {"id": order.id, "estado": Constants.FAILED, "site": generator, "motivo": reason})


def _append(out: Path, line: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    line = {**line, "data": datetime.now().astimezone().isoformat(timespec="seconds")}
    with (out / Constants.LOG_FILE).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(line, ensure_ascii=False) + "\n")
