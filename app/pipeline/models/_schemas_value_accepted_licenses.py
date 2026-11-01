from __future__ import annotations

from app.pipeline.models._schemas_types import (
    ATTRIBUTION_LICENSES,
    AUDIO_LIBRARY_LICENSE,
    CITATION_LICENSE,
    PUBLIC_DOMAIN_LICENSES,
)
from app.pipeline.models._schemas_value_stock_licenses import STOCK_LICENSES

ACCEPTED_LICENSES = (
    PUBLIC_DOMAIN_LICENSES
    | ATTRIBUTION_LICENSES
    | set(STOCK_LICENSES.values())
    | {"CC0-1.0", "Flickr-NKCR", "Generated", "Original", CITATION_LICENSE, AUDIO_LIBRARY_LICENSE}
)
