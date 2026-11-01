# Pauta: "Um comando de barra que revisa o código" (Short tec em inglês, episódio 3 da série de mods), 2026-10-26

Para o baixo nível, em inglês (o canal é só em inglês). Sexta, 30/10, a ser agendada depois do gate 4.

## Ângulo

Um comando de barra é um arquivo Markdown em `.claude/commands/`: o nome do arquivo vira o comando. Este roda o
ruff e os testes e devolve só os erros, com arquivo e linha.

## Demonstração (saídas reais em `demo/saidas.txt`; o comando é `demo/revisar.md`)

- `ruff check .`: B006 em `lista.py:1`.
- `pytest -q`: falha em `test_lista.py:6`, com `['pão', 'leite'] == ['leite']`, o mesmo bug visto pelo teste.

Limite: a execução do `/revisar` numa sessão do Claude Code não foi gravada; a demo mostra os dois comandos que o
arquivo manda rodar. Se o dono gravar a sessão, o painel de cima passa a ser a gravação.

## Hipótese (a registrar)

Retenção acima de 60% nos 15 s iniciais com o gancho do erro. Medida: retenção e inscritos aos 7 e 28 dias.

## Pendências

- OK do dono na pauta e na narração.
- Voz (Modal), `tempos`, render e gate 4 (o dono assiste e carimba).
- Pacote, dúvida cega e agendamento para sexta, com a confirmação do dono.
