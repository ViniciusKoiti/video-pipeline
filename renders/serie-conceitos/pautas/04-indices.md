# Pauta 4: índices, sábado 2026-11-28, 12h

Série "eu medi" (`../serie.md`). Nada foi medido, gravado nem renderizado.

## Por que este conceito fecha a série

Índice é a árvore do Short 3 **em uso**: o banco monta uma por baixo da tabela. Fecha a série ligando os quatro
conceitos (memória, threads, árvore, banco) ao que o iniciante usa todo dia, a consulta SQL.

## Os ângulos

### A. A mesma consulta, sem índice e com índice (recomendado)
- **Gancho (3 s):** "Uma linha de SQL. Rodei duas vezes. A segunda foi X vezes mais rápida."
- **Demonstração:** SQLite (já no Python do projeto, sem dependência nova): tabela com um milhão de linhas
  (id, um campo inteiro aleatório, um texto curto); a consulta `WHERE campo = ?` para mil valores, sem índice
  e com `CREATE INDEX`. Tempo total (mediana de 15 rodadas) e o `EXPLAIN QUERY PLAN` das duas, que diz `SCAN`
  numa e `SEARCH ... USING INDEX` na outra.
- **O que a medição precisa responder:** o tempo das mil consultas sem e com índice, a razão, o tempo de criar o
  índice (o custo que a fala precisa dizer) e o tamanho do arquivo antes e depois.
- **Risco:** com a tabela em cache, o `SCAN` de um milhão de linhas pode ser rápido demais e a razão ficar
  pequena. Mitigação: mil consultas, não uma; e o tamanho do campo de texto para a tabela não caber toda no
  cache de página do SQLite. Registrar o `PRAGMA cache_size` usado.
- **Por que eu escolheria:** é a única demonstração da série que o público reproduz em cinco minutos no próprio
  banco, e a palavra `SCAN` contra `SEARCH` na tela é a explicação sem explicar.

### B. O índice que não é usado
- **Gancho:** "Criei o índice. O banco ignorou."
- **Demonstração:** a mesma consulta com `WHERE lower(campo) = ?` ou `LIKE '%x'`: o plano volta a `SCAN` mesmo com
  índice. Medido: tempo e plano.
- **Risco:** pressupõe o A; é o Short seguinte sobre o tema.

### C. O custo de escrever
- **Gancho:** "O índice deixou a leitura rápida. E a escrita?"
- **Demonstração:** inserir cem mil linhas com e sem o índice; tempo.
- **Risco:** o número costuma ser menos impressionante; serve de cena de contraste no A ("o índice custou Y ms
  para criar"), não de abertura.

## Demonstração planejada (ângulo A, com o custo de criar o índice como contraste)

- `demo/indice.py` (só biblioteca padrão: `sqlite3`, `time`, `random` com semente fixa): cria o banco, roda as
  mil consultas sem índice, cria o índice (tempo medido), roda de novo, imprime os dois `EXPLAIN QUERY PLAN`, o
  tamanho do arquivo e a linha de ambiente (versão do SQLite, Python, CPU, data).
- `demo/resultado.txt`: 15 rodadas.
- Tela: `codigo` (a consulta e o `CREATE INDEX`), `resultado` (`comparison`: ms sem contra com), `plano` (texto:
  `SCAN tabela` contra `SEARCH tabela USING INDEX`), custo de criar no rodapé da cena.

## Forma (35 a 45 s)

1. Gancho, 3 s.
2. Código, 10 s: a consulta, depois o `CREATE INDEX`.
3. Resultado, 12 s: os ms das duas, a razão; o plano.
4. Só a medida, 8 s: "criar o índice custou Y ms e o arquivo cresceu Z MB".
5. Fecho, 6 s: "O que o banco monta quando você cria um índice? Comenta aqui, que o código está na descrição."

## Hipótese

Fechar a série ligando ao Short 3 ("o índice é a árvore do vídeo passado") faz os dois serem vistos em
sequência. Variável: a ponte explícita. Medida: views do Short 3 nos 7 dias após este sair; retenção deste aos 7 e
28 dias.

## O que o dono decide

1. Ângulo (recomendo A com o custo de criar como contraste).
2. Título provisório: "Uma linha de SQL, X vezes mais rápida" / "One line of SQL, X times faster" (o X vem da
   medição).

## O que esta pauta não diz

Nenhum número. "O banco monta uma árvore" é a ponte com o Short 3 e só entra na fala se a fonte (a documentação
do SQLite sobre o B-tree do índice) for registrada em `sources.json`; senão fica na pergunta do fecho.
