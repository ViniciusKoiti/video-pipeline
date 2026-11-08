from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from app.bootstrap.models.registration import Registration
from app.pipeline.ports import ManifestStore, ReviewGate
from app.providers.alignment.base import SubtitleAligner, WordAligner
from app.providers.archives.base import ArchiveProvider
from app.providers.image_gen.base import ImageGenProvider
from app.providers.text.base import TextProvider
from app.providers.tts.base import TTSProvider
from app.render.base import RenderEngine


class Registry(TypedDict):
    text: Mapping[str, Registration[TextProvider]]
    tts: Mapping[str, Registration[TTSProvider]]
    image_gen: Mapping[str, Registration[ImageGenProvider]]
    archives: Mapping[str, Registration[ArchiveProvider]]
    aligner: Mapping[str, Registration[SubtitleAligner]]
    word_aligner: Mapping[str, Registration[WordAligner]]
    render: Mapping[str, Registration[RenderEngine]]
    store: Mapping[str, Registration[ManifestStore]]
    review: Mapping[str, Registration[ReviewGate]]
