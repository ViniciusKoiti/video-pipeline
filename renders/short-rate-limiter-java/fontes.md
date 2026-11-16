# Fontes: rate limiter em Java

Baixadas em 2026-11-16 por `curl` (domínio liberado em `.claude/settings.local.json`); arquivos em `fontes/`.
Trechos literais em `fontes/excertos.md`. As fontes explicam o mecanismo e o código de status; os parâmetros e os
resultados vêm exclusivamente da demo local.

| ID | Fonte primária | Uso |
| --- | --- | --- |
| F1 | RFC 6585 (Nottingham, Fielding), *Additional HTTP Status Codes*, abril de 2012, §4. https://www.rfc-editor.org/rfc/rfc6585.txt (`fontes/rfc6585.txt`) | Significado do 429 ("rate limiting"); a RFC não define como o servidor identifica o usuário nem como conta as requisições |
| F2 | RFC 2697 (Heinanen, Guerin), *A Single Rate Three Color Marker*, setembro de 1999, §§2–3. https://www.rfc-editor.org/rfc/rfc2697.txt (`fontes/rfc2697.txt`) | Mecanismo do balde de fichas: começa cheio, enche a uma taxa fixa até um tamanho máximo, e o pacote só passa se houver fichas suficientes; sem elas, não conforme e nada é descontado |
| D1 | `demo/Demo.java`, `demo/LimitadorTest.java`, `demo/medir.sh` e `demo/resultado.txt` | Token bucket didático em Java, cenário, teste da 101ª requisição e 30 medições (15 por modo), OpenJDK 25.0.5, 2026-11-11 |

## O que as fontes dizem e o que não dizem

- A F2 é um marcador de tráfego de rede (bytes, três cores), não um limitador de API. Usamos só o mecanismo do balde
  (taxa de enchimento, tamanho máximo, gasto por unidade, recusa sem fichas); na demo a unidade é uma requisição por
  ficha e há um balde por cliente. Isso é decisão da demo, não da RFC.
- A F1 diz que 429 é "rate limiting" e que a resposta pode trazer `Retry-After`. Não diz qual algoritmo usar.
- Nenhuma fonte diz que 20 fichas por segundo ou 100 de capacidade são bons valores: são parâmetros escolhidos na demo.
- A fonte não diz que um pico legítimo maior que o balde seria recusado: é a consequência do mecanismo (F2: sem fichas
  suficientes, o pacote não é conforme). A demo **não mediu** isso (zero clientes normais recusados nos dois modos).

## Evidência local

`demo/resultado.txt` (2026-11-11, 15 rodadas por modo, JVM nova sem aquecimento, ordem alternada, execução
sequencial, sonda de CPU antes de cada rodada, todas abaixo de 0,3 s; a sonda não garante ausência de ruído):

| Métrica (mediana das 15 rodadas; extremos) | sem limite | com limite |
| --- | --- | --- |
| mediana dos clientes normais, ms | 2867 (2863–2870) | 51 (51–51) |
| p99 dos clientes normais, ms | 5034 (5030–5039) | 478 (477–481) |
| requisições do robô aceitas | 1000 | 100 |
| requisições do robô recusadas (429) | 0 | 900 |
| clientes normais recusados | 0 | 0 |
| fila máxima no serviço de trás | 993 | 93 |

Simulação com `Thread.sleep` e threads virtuais; serviço de trás com 10 vagas e 50 ms por requisição, 5 clientes
normais a 10 por segundo, robô com 1000 requisições de uma vez. Não mede rede, banco, biblioteca nem produção.
A tela mostra 2,9 s (2867 ms), 51 ms e 900 recusas; as demais linhas da tabela não vão à tela.

## Direitos e ativos

Trechos textuais curtos das RFCs (IETF Trust) para rastrear as afirmações, com atribuição e URL; nenhuma imagem das
fontes é usada. Os diagramas são do fluxo do `motion-video` local, originais, sem assets externos, Lottie, pele do
apresentador ou promessa de código público. Publicação e gates humanos permanecem pendentes.
