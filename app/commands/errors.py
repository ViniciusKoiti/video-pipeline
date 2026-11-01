"""O tratamento único dos erros esperados, na borda dos comandos e dos scripts (ADR 045).

`run` captura só `PipelineError`: imprime `<rótulo>: <mensagem>` no stderr e devolve o código de erro (1).
Qualquer outra exceção é bug e sobe com o traceback (§2.1). Com `VP_DEBUG` definido, o erro tratado também
sobe, para depurar sem editar código. Comandos e scripts não têm `try/except` de erro do projeto: levantam,
e este é o único ponto que decide a saída. A recuperação por cena ou por item continua no lugar onde ela é
possível (`for_each_scene`, `run_scenes`, o laço de `vp assets take`).

`postiz` e `usage` têm um contrato próprio de erro em JSON (`{"error": ...}`, mensagens fixas, sem detalhe
que vaze segredo) e o mantêm.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable

from app.commands.constants.cli_constants import CliConstants
from app.errors import PipelineError


def run(label: str, action: Callable[[], int | None]) -> int:
    try:
        return action() or 0
    except PipelineError as error:
        if os.environ.get(CliConstants.DEBUG_ENV):
            raise
        print(f"{label}: {error}", file=sys.stderr)
        return CliConstants.EXIT_ERROR
