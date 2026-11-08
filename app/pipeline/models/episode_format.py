from __future__ import annotations

from enum import StrEnum


class EpisodeFormat(StrEnum):
    """Formato do episódio: decide o motor de render pelo mapa de config/providers.toml (ADR 001)."""

    ARCHIVAL_DOCUMENTARY = "archival_documentary"  # fotos de arquivo + narração (motor ffmpeg)
    EXPLAINER = "explainer"  # visual gerado a partir de dados (Remotion + motion-kit; etapa 43)
