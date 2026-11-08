from __future__ import annotations

import copy
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.pipeline.constants.motion_constants import MotionConstants
from app.pipeline.models.fit_row import FitRow


@dataclass(frozen=True, eq=False)
class MotionContent:
    """O JSON do `motion-video` do kit, já validado (`app.pipeline.motion_inputs`). Só o que o auto-play usa é
    interpretado (cenas, `durationSec`, `fps`, `host`); todo o resto fica como veio e volta em `dumps`.
    Nenhum método altera o objeto: `fitted` devolve outro."""

    raw: Mapping[str, Any]

    @property
    def fps(self) -> int:
        return int(self.raw.get("fps", MotionConstants.DEFAULT_FPS))

    @property
    def scene_ids(self) -> list[str]:
        return [scene["id"] for scene in self.raw["scenes"]]

    def starts(self) -> dict[str, float]:
        """O começo de cada cena em segundos, com a mesma conta do motion-video: frames inteiros por cena."""
        starts: dict[str, float] = {}
        frame = 0
        for scene in self.raw["scenes"]:
            starts[scene["id"]] = frame / self.fps
            frame += round(float(scene["durationSec"]) * self.fps)
        return starts

    def fitted(
        self, seconds: Mapping[str, float], pad: float = MotionConstants.PAD_SEC
    ) -> tuple[MotionContent, list[FitRow]]:
        """Estica cada cena até a fala caber: `max(duração do JSON, fala + folga)`, no décimo de segundo
        acima. Cena sem fala fica como está. A fala entra no começo da cena: a boca da janela do apresentador
        fala só nesse trecho. Devolve o conteúdo novo e uma linha por cena; o original não muda."""
        content = copy.deepcopy(dict(self.raw))
        windowed = content.get("host") is not None
        grid, eps = MotionConstants.FIT_GRID, MotionConstants.FIT_EPSILON
        rows = []
        for scene in content["scenes"]:
            before = after = float(scene["durationSec"])
            spoken = seconds.get(scene["id"])
            if spoken is not None:
                after = max(before, math.ceil((spoken + pad) * grid - eps) / grid)
                scene["durationSec"] = after
                hidden = scene.get("host") is False or scene["type"] in MotionConstants.HOST_HIDDEN_TYPES
                if windowed and not hidden:
                    scene["host"] = {**(scene.get("host") or {}), "speaking": [0.0, round(spoken, 2)]}
            rows.append(FitRow(scene["id"], before, after, spoken))
        return MotionContent(content), rows

    def dumps(self) -> str:
        return json.dumps(self.raw, ensure_ascii=False, indent=2) + "\n"
