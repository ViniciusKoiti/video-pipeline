"""Glossário de pronúncia por episódio (`voice/glossary.json`, §9): como a voz deve ler uma palavra.

Serve a qualquer voz, porque troca a grafia e não usa fonemas: "FBI" vira "efe bê i" só no texto da voz.
A tela, a legenda e as âncoras dos planos continuam com a grafia do roteiro, e o `scenes.json` aprovado não
muda. A troca é por palavra inteira e respeita maiúsculas e minúsculas; o texto trocado entra na chave do WAV,
então só as cenas com um termo do glossário ganham fala nova.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.media.constants.pronunciation_constants import PronunciationConstants
from app.media.models._pronunciation_model import _Model as _Model
from app.media.models.glossary import Glossary as Glossary
from app.media.models.term import Term as Term


def load_glossary(episode_dir: Path) -> Glossary:
    """O glossário do episódio; sem o arquivo, vazio."""
    path = episode_dir / PronunciationConstants.GLOSSARY_FILE
    if not path.is_file():
        return Glossary()
    return Glossary.model_validate_json(path.read_text(encoding="utf-8"))


def respell(text: str, glossary: Glossary) -> str:
    """O texto que vai para a voz: cada termo do glossário, como palavra inteira, trocado pela fala."""
    for term in glossary.termos:
        text = re.sub(rf"(?<!\w){re.escape(term.escrita)}(?!\w)", term.fala.replace("\\", "\\\\"), text)
    return text
