# Roteiro: índices no SQLite (série "eu medi")

Pauta: `data/episodes/short-indices-sqlite-pt/pauta.md`. Tema escolhido pelo dono em 2026-11-03 (pauta de 31/10
atualizada para a direção de System Design). Funil `topo` (padrão da série; a confirmar pelo dono). Sem música.

Pergunta central: **o que um índice muda no caminho de uma consulta, e quanto ele custa na escrita?**
Promessa: ver a mesma consulta ler a tabela inteira e depois ir direto às linhas pelo índice, e o preço que cada
pedido novo paga.

## A lição em uma frase

**Sem índice, cada consulta lê a tabela inteira; com o índice, ela desce uma árvore ordenada até as linhas que
quer, e em troca cada escrita também precisa gravar no índice.** Por isso a decisão de indexar uma coluna depende
de quanto a tabela é lida e gravada.

Cada cena de explicação diz na fala uma parte dessa regra:

| Cena | Regra ou consequência dita na fala |
| --- | --- |
| `sem-indice` | sem índice, o banco lê a tabela inteira para achar um cliente |
| `codigo` | uma linha (`CREATE INDEX`) troca o plano de `SCAN` para `SEARCH` |
| `com-indice` | o índice é uma árvore ordenada por cliente; a busca desce direto às linhas |
| `comparacao` | sem ler a tabela, a consulta cai de 86 ms para 0,05 ms |
| `escrita` | cada pedido novo também entra no índice: gravar fica 13 vezes mais lento |
| `custo` | criar o índice custa tempo e espaço |
| `fecho` | a decisão depende de leitura × escrita |

## Origem de cada número

Medição própria: `demo/resultado.txt` (`indice.py` + `medir.sh`, SQLite 3.46.1, Python 3.14.4, Ryzen 7 5700U,
15 rodadas, banco recriado em cada rodada, sonda de CPU entre 0,046 e 0,067 s em todas). O cache do SQLite é o
padrão (`cache_size = -2000`, cerca de 2 MB) e o cache do sistema operacional estava quente: os tempos são
desta máquina e desta tabela, não de um servidor.

| Cena | Fala / tela | Origem |
| --- | --- | --- |
| `gancho` | "mais de mil vezes" | razão das medianas, 1824,3 (`razoes.sh`); "mais de mil" é limite inferior |
| `sem-indice` | um milhão de linhas | constante do programa (`LINHAS`), no cabeçalho |
| `comparacao` | 85,7 ms / "oitenta e seis" | mediana `sem_indice_ms` 85.741 |
| `comparacao` | 0,047 ms / "cinco centésimos" | mediana `com_indice_ms` 0.0470 |
| `escrita` | "treze vezes" | razão das medianas de inserção, 13,12 (`razoes.sh`) |
| `custo` | 24 ms e 319 ms para gravar 10 mil | medianas `inserir_sem_indice_ms` 24.3 e `inserir_com_indice_ms` 318.9 |
| `custo` | 736 ms para criar | mediana `criar_indice_ms` 736.3 |
| `custo` | "quase treze megas" | 87,2 − 74,6 = 12,6 MB (`razoes.sh`) |
| `com-indice` | 50.000, 25.000, 75.000, 12.500, 41.230, 42.017 | **chaves didáticas** do desenho da árvore, não lidas do banco |

Medições invalidadas e guardadas (não usadas): `resultado.invalido-2026-11-03T0751.txt` (máquina limitada durante o
render do ensaio, sonda 0,345 s no fim), `resultado.abortado-1.txt` (erro no caminho da sonda) e
`resultado.abortado-2.txt` (sonda 0,356 s na rodada 6).

## Fontes do mecanismo

`fontes.md` (documentação do SQLite, frases literais Q1–Q4, E1–E2, F1–F2). O `EXPLAIN QUERY PLAN` da própria demo
mostra `SCAN pedidos` sem índice e `SEARCH pedidos USING INDEX pedidos_cliente (cliente_id=?)` com ele.

## Regras seguidas

- Nenhum tempo sem medição; a fala não generaliza o "treze vezes" para outros bancos ou configurações.
- SQL e SQLite explícitos no gancho e no código.
- System Design: a tela "Meus pedidos" (leitura) e o Checkout (escrita) aparecem como componentes; a decisão é
  indexar `cliente_id` sabendo o preço na escrita.
- A pergunta do fecho devolve a decisão ao espectador.

## Fora deste Short

- Índice que o banco não usa (`lower(campo)`, `LIKE '%x'`), índice de cobertura, outros bancos.
- "O índice sempre compensa" ou qualquer regra de proporção leitura/escrita.
