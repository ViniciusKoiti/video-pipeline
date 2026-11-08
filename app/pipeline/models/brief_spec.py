from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class BriefSpec:
    """Um tipo de resumo copiado para o episódio: o arquivo, o contrato e como o anterior é guardado."""

    file: str  # nome na pasta do episódio
    archive: str  # nome do anterior guardado, com `{stamp}` no lugar da data dele
    parse: Callable[[str], BaseModel]  # o contrato; fora dele é `ValidationError`
    stamp: Callable[[Any], str]  # a data do conteúdo que sai
    describe: Callable[[Any], str]  # como o conteúdo atual aparece na mensagem de recusa
