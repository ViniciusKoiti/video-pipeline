from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import RegionCode
from app.pipeline.models.place import Place
from app.pipeline.models.route import Route


class MapShot(_Shot):
    kind: Literal["map"] = "map"
    places: list[Place] = Field(min_length=1)
    scope: Literal["region", "world"] = "region"  # ADR 011
    highlight: list[RegionCode] = []  # países ou estados acesos, em ordem
    routes: list[Route] = []

    @model_validator(mode="after")
    def _routes_and_claims(self) -> Self:
        names = {p.name for p in self.places}
        for route in self.routes:
            missing = sorted({route.from_, route.to} - names)
            if missing:
                raise ValueError(f"rota com lugar fora de places: {', '.join(missing)}")
        if (self.highlight or self.routes) and not self.claims:
            raise ValueError("mapa com países acesos ou rotas afirma algo: precisa de claims (§2.2)")
        return self
