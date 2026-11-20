"""Teto e rodada do `vp imagens gerar` (ADR 065).

**Teto (§6):** no máximo 12 imagens geradas por episódio e 2 por cena (`[limits]` do `providers.toml`).
Conta o que já está pronto na pasta de saída mais o que a rodada vai pedir; pedido sem `cena` conta só no
total.
Passar do teto é decisão do dono: o comando recusa sem `--acima-do-teto` e avisa com ele.

**Rodada:** uma imagem por vez, com pausa entre pedidos e custo estimado antes de cada um (custo > 0 para,
§2.1). Pedido sem imagem (`InvalidOutput`) é anotado e a rodada segue; duas falhas seguidas param (seletor
quebrado). Bloqueio de acesso, cota ou outra falha do provedor é anotado e para a rodada na hora.
"""

from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from app.pipeline.constants.image_queue_constants import ImageQueueConstants as Constants
from app.pipeline.models.image_order import ImageOrder
from app.pipeline.visuals.image_queue import (
    ImageQueueError,
    read_log,
    ready,
    record_failure,
    record_generated,
    target,
)
from app.providers.errors import InvalidOutput, PaidApiBlocked, ProviderError
from app.providers.image_gen.base import ImageGenProvider, ImageRequest


def ceiling_problems(
    orders: list[ImageOrder], batch: list[ImageOrder], out: Path, *, per_episode: int, per_scene: int
) -> list[str]:
    ids = ready(out) | {order.id for order in batch}
    problems = []
    if len(ids) > per_episode:
        problems.append(f"{len(ids)} imagens na pasta com esta rodada; o teto é {per_episode} por episódio")
    scene_of = {line["id"]: line["cena"] for line in read_log(out) if line.get("cena")}
    scene_of |= {order.id: order.scene for order in orders if order.scene}
    per = Counter(scene_of[ident] for ident in ids if ident in scene_of)
    problems += [
        f"{scene}: {n} imagens; o teto é {per_scene} por cena"
        for scene, n in sorted(per.items())
        if n > per_scene
    ]
    return problems


def run_round(
    provider: ImageGenProvider,
    batch: list[ImageOrder],
    out: Path,
    *,
    interval_s: float,
    report: Callable[[str], None],
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """Gera o lote em ordem e devolve quantas imagens ficaram prontas."""
    name, made, failures = provider.info.name, 0, 0
    for index, order in enumerate(batch):
        if index:
            sleep(interval_s)
        request = ImageRequest(prompt=order.prompt, out_path=target(out, order), refs=order.refs)
        try:
            if provider.estimate_cost(request).usd > 0:
                raise PaidApiBlocked(name, "custo por imagem acima de zero (§2.1)")
            image = provider.generate_image(request)
        except InvalidOutput as error:
            record_failure(out, order, name, str(error))
            report(f"  {order.id}: falhou ({error})")
            failures += 1
            if failures >= Constants.MAX_CONSECUTIVE_FAILURES:
                raise ImageQueueError(
                    f"{failures} falhas seguidas; conferir seletores com `vp imagens mapear`"
                ) from error
            continue
        except ProviderError as error:
            record_failure(out, order, name, str(error))
            raise
        record_generated(out, order, image)
        made, failures = made + 1, 0
        report(f"  {order.id}: {image.path}")
    return made
