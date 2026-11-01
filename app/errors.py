"""Base dos erros esperados do projeto (ADR 045).

Todo erro que o dono pode causar ou corrigir (episódio travado, gate que não vale, fonte sem texto, provedor
sem cota, arquivo ausente) herda de `PipelineError`. Quem trata é a borda (`app.commands.errors.run`): imprime
a mensagem e sai com o código de erro. Bug continua sendo outra exceção e continua com traceback (§2.1).

As classes herdam também da base de antes (`ValueError`, `RuntimeError`...), para que nenhum `except`
existente deixe de pegá-las. Módulo sem dependências: qualquer camada pode importá-lo.
"""

from __future__ import annotations


class PipelineError(Exception):
    pass
