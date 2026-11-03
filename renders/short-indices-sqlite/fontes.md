# Fontes do Short de índices (SQLite)

Registro de 2026-11-03. Páginas da documentação oficial do SQLite baixadas com `curl` às 07:35 (BRT), em
`fontes/*.html`, com o texto extraído em `fontes/*.txt`. As frases abaixo foram copiadas do texto extraído
(grep literal), não de um resumo. Conferir na página antes de publicar.

| Página | URL | sha256 (16) |
| --- | --- | --- |
| Query Planning | https://www.sqlite.org/queryplanner.html | f5e810a7c03401a3 |
| EXPLAIN QUERY PLAN | https://www.sqlite.org/eqp.html | 9bcf6cac4798d8ca |
| Database File Format | https://www.sqlite.org/fileformat2.html | 905067afacc30583 |
| CREATE INDEX | https://www.sqlite.org/lang_createindex.html | 13c810d494653e24 (baixada; não citada) |

## Mecanismo, com a frase registrada

| Id | Afirmação usada no roteiro | Trecho (inglês, como na página) | Página |
| --- | --- | --- | --- |
| Q1 | Sem índice, o banco lê a tabela inteira para achar as linhas | "This algorithm is called a full table scan since the entire content of the table must be read and examined in order to find the one row of interest." | Query Planning |
| Q2 | Com o índice, o banco faz uma busca binária no índice, que está ordenado pela coluna | "SQLite can do this binary search on the Idx1 index but not on the original FruitsForSale table because the rows in Idx1 are sorted by the \"fruit\" column." | Query Planning |
| Q3 | Depois do índice, uma segunda busca vai à linha original da tabela | "Then the database engines does a second binary search on the original FruitsForSale table to find the original row that contains fruit='Peach'." | Query Planning |
| Q4 | O custo deixa de ser proporcional ao tamanho da tabela (N) e passa a ser proporcional a logN | "If the table contains N elements, the time required to look up the desired row is proportional to logN rather than being proportional to N as in a full table scan." (dito da busca por rowid; para o índice: "the cost of doing the query is proportional to (K+1)*logN") | Query Planning |
| E1 | `SCAN` no plano é leitura da tabela inteira | "\"SCAN\" is used for a full-table scan, including cases where SQLite iterates through all records in a table in an order defined by an index." | EXPLAIN QUERY PLAN |
| E2 | `SEARCH` no plano é visitar só parte das linhas | "\"SEARCH\" indicates that only a subset of the table rows are visited." | EXPLAIN QUERY PLAN |
| F1 | Cada índice é uma B-tree própria no arquivo do banco | "There is one index b-tree in the database file for each index in the schema, including implied indexes created by uniqueness constraints." | File Format |
| F2 | Cada linha da tabela tem uma entrada em cada índice da tabela | "In a normal index, there is a one-to-one mapping between rows in a table and entries in each index associated with that table." | File Format |

## Como as fontes entram na fala

- "lê a tabela inteira" (Q1, E1), "busca no índice, que está ordenado pelo cliente" (Q2), "e vai direto às
  linhas" (Q3, E2): mecanismo.
- "o índice é uma árvore própria no arquivo" (F1): só como desenho (layout `tree`) e na palavra "árvore".
- "cada pedido novo também entra no índice" (F2): é a razão do custo de escrita. O tamanho do custo vem
  só da medição (`demo/resultado.txt`).

## O que a documentação não diz (e o roteiro não afirma)

- Que a inserção fica N vezes mais lenta em geral. O quanto fica mais lenta é o que **esta** demonstração mediu,
  com o cache padrão do SQLite (`cache_size = -2000`, cerca de 2 MB) e chaves aleatórias.
- Que um índice sempre compensa. A decisão depende de quanto a aplicação lê e escreve naquela tabela; o
  vídeo mostra os dois lados medidos, não uma regra.
- A segunda fonte primária: só a documentação do SQLite foi registrada. Nada de outros bancos.
