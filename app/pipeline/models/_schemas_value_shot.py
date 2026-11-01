from __future__ import annotations

from typing import Annotated

from pydantic import Field

from app.pipeline.models.broll_shot import BrollShot
from app.pipeline.models.calculation_shot import CalculationShot
from app.pipeline.models.chart_shot import ChartShot
from app.pipeline.models.compare_shot import CompareShot
from app.pipeline.models.end_card_shot import EndCardShot
from app.pipeline.models.family_tree_shot import FamilyTreeShot
from app.pipeline.models.hook_shot import HookShot
from app.pipeline.models.keyword_shot import KeywordShot
from app.pipeline.models.lower_third_shot import LowerThirdShot
from app.pipeline.models.map_shot import MapShot
from app.pipeline.models.network_shot import NetworkShot
from app.pipeline.models.number_shot import NumberShot
from app.pipeline.models.photo_shot import PhotoShot
from app.pipeline.models.quote_shot import QuoteShot
from app.pipeline.models.receipt_shot import ReceiptShot
from app.pipeline.models.stamp_shot import StampShot
from app.pipeline.models.timeline_shot import TimelineShot

Shot = Annotated[
    PhotoShot
    | BrollShot
    | NumberShot
    | ChartShot
    | QuoteShot
    | MapShot
    | StampShot
    | LowerThirdShot
    | TimelineShot
    | FamilyTreeShot
    | CompareShot
    | NetworkShot
    | KeywordShot
    | CalculationShot
    | ReceiptShot
    | HookShot
    | EndCardShot,
    Field(discriminator="kind"),
]
