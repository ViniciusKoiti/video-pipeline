from __future__ import annotations

from pathlib import Path

from app.settings.models._settings_model import _Model


class ChatterboxModalSettings(_Model):
    """A mesma voz clonada numa GPU do Modal (ADR 024). Modelo, idioma, pausa, entrega e gravação de
    referência vêm de `[chatterbox]`; aqui fica só o que é da nuvem."""

    python: Path = Path("~/.local/share/uv/tools/modal/bin/python")  # o Python da CLI do Modal
    app: str = "voz-dono"  # nome publicado por `modal deploy deploy/modal_chatterbox.py`
    reference_name: str = "referencia.wav"  # a gravação no volume privado `voz-dono-referencia`
