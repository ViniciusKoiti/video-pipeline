"""Constantes de postiz_cadeia; dados fixos sem I/O."""

from __future__ import annotations

from pathlib import Path
from typing import Final


class PostizCadeiaConstants:
    REGISTRO: Final = Path("publicacoes/registro.jsonl")
    UNDO: Final[str] = (
        "Antes do horário: apagar o post no Postiz (os ids saem no registro e em "
        "`vp postiz posts`). Depois do horário: apagar a publicação na rede; o "
        "Postiz não desfaz o que já saiu."
    )
    FIXED_RISKS: Final = (
        "O Postiz não garante idempotência: se o envio falhar, consultar a fila antes de repetir.",
        ("A API não marca conteúdo alterado ou sintético: com voz ou imagem gerada, marcar à mão na rede."),
        (
            "Depois de publicar: conferir no Studio (ERROR no Postiz não prova falha), "
            "fixar o primeiro comentário e marcar o conteúdo alterado, tudo à mão."
        ),
    )
    VERDICTS: Final = ("segue", "não segue")
    NO_PACKAGE: Final[str] = (
        "sem pacote de decisão para este JSON: rode `vp postiz pacote` e mostre o pacote ao dono"
    )
