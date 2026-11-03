# Publicação do Short de concorrência em C

- Canal: YouTube `@viniciusnakahara` (`cmvx0omyy0005l26yggavdqpu`).
- Vídeo: `renders/short-concorrencia/final.pt.fluxo.mp4`, 51,4 s.
- Título: **Por que o contador perde somas em C? Mutex e atomic**.
- Autorização: o dono avaliou o vídeo e pediu "Pode postar o video por favor" nesta sessão.
- Gate 4 registrado por `vp approve`; pacote e dúvida cega concluídos antes do envio.
- Horário solicitado ao Postiz: 01/11/2026 às 14h14min08s de Brasília.
- ID no Postiz: `cmvy39tii0006n16tz5dvotmi`.
- Estado confirmado pela API: **PUBLISHED**.
- Link informado pelo Postiz: https://www.youtube.com/watch?v=zX7OwsdeqjQ
- Evidência: `publicacao-confirmada.json`; etapas em `data/publicacoes/registro.jsonl`.

## Pendências fora da API de publicação

Conferir no YouTube Studio o vídeo e o rótulo de conteúdo alterado/sintético; a API
do Postiz não oferece esse rótulo. A descrição já declara a voz clonada por IA.
Comentário fixado e leituras de métricas aos 7 e 28 dias continuam manuais.

## Skills do Claude

`shorts-tec` passou a abranger conceitos de programação e exemplos próprios, com plano
de animação, blocos conectados, revisão dos estados e impacto visual em System Design.
`short-diario` usa o plano e o gerador deste vídeo como referência de forma, preservando
a prioridade Java e a fila de temas. Não transfere semântica ou números de C para Java.

Validação: `short-diario` passou no quick_validate; os dois frontmatters YAML foram
conferidos preservando `argument-hint` do Claude. Ruff passou. A suíte geral desta
rodada foi interrompida na coleta por ImportError em `tests/test_shorts_tec.py`, durante
alterações de aplicação externas a este ajuste de skills; não foi corrigida nesta tarefa.
