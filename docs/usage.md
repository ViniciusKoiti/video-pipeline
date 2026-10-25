# Consumo editorial em SQLite

`vp usage` registra metadados de consumo e reservas em
`DATA_DIR/telemetry/usage.sqlite3` (padrão `data/telemetry/usage.sqlite3`).
O banco é local, privado e ignorado pelo Git. Usa somente a biblioteca padrão.
Decisão: [ADR 032](decisions/032-sqlite-consumo-agentes.md).

Esta primeira integração importa eventos já exportados e normalizados. Ela não
inicia agentes, habilita coleta automática nem intercepta requisições do Claude
Code. `reserve` recusa saldo insuficiente; aplicar essa decisão ao lançamento de
agentes depende de um controlador que use essa porta.

## Começar

```bash
.venv/bin/vp usage init
.venv/bin/vp usage --help
```

A inicialização não define tetos, importa sessões nem faz inferência. Os comandos
abaixo exemplificam uma execução fictícia; os valores não são recomendações de teto.

```bash
.venv/bin/vp usage budget exemplo --id exemplo-tokens --metric tokens_total --limit 200000
.venv/bin/vp usage budget exemplo --id exemplo-custo --metric cost_usd_micros --limit 10000000
.venv/bin/vp usage start exemplo --id roteiro-01 --stage roteiro --agent roteirista --session sessao-exemplo
```

`--project` em `budget`, `start` e `report` permite separar projetos no mesmo banco;
o padrão é `auto-play`. Em `budget`, `--model` aceita um identificador exato do modelo
observado nos eventos; sem a opção, o teto cobre todos os modelos. Não usa o alias
`fable` como se ele fosse o id retornado pelo provedor.

Para reservar, criar `reservas.json` com uma quantidade na unidade de **cada** teto
existente para o episódio, inclusive zero quando não se pretende usar aquele teto:

```json
{"exemplo-tokens": 50000, "exemplo-custo": 2000000}
```

```bash
.venv/bin/vp usage reserve roteiro-01 reservas.json
.venv/bin/vp usage report exemplo
```

`tokens_total` soma entrada, saída, cache lido e cache escrito. Essa soma é uma
métrica interna de volume; a cota da assinatura não tem conversão exata conhecida.
`cost_usd_micros` usa milionésimos de dólar: `1000000` equivale a US$ 1 estimado.
Esses tetos não modificam `ALLOW_PAID_API=false` ou `MAX_API_SPEND_USD=0`.

## Importar requisições

A entrada é JSONL, com um objeto de metadados por linha, vinculado a uma execução.
Exemplo fictício de uma linha em `eventos.jsonl`:

```json
{"request_id":"req-exemplo-1","model":"modelo-exemplo","event.timestamp":"2026-10-24T12:00:00Z","input_tokens":100,"output_tokens":50,"cache_read_tokens":500,"cache_creation_tokens":100,"cost_usd_micros":2000,"duration_ms":1200}
```

```bash
.venv/bin/vp usage import roteiro-01 eventos.jsonl
.venv/bin/vp usage report exemplo
```

Os nomes correspondem aos atributos de `claude_code.api_request`:
[contrato oficial](https://code.claude.com/docs/en/monitoring-usage#api-request-event).
Exportações OTLP completas precisam ser achatadas e correlacionadas antes da
importação; o comando não interpreta envelopes OTLP, stdout misturado ou transcripts.

Também aceita `event_key`, `provider_request_id`, `occurred_at` e `cache_write_tokens`
como nomes normalizados. Sem `request_id`, fornecer uma `event_key` estável da origem,
reutilizada em cada retransmissão. Sem inventar uma chave nova a cada importação.

- `model` e data com fuso são obrigatórios. Contadores são inteiros não negativos.
- Campo ausente permanece desconhecido. Zero só quando o evento informa zero.
- Para uma tentativa com erro, usar `status: "error"`; não deduzir consumo zero.
- Só os campos permitidos entram no banco. Conteúdo de prompts/respostas não é retido.
- Um lote é validado antes de gravar e inserido em uma transação. Conflitos desfazem
  o lote inteiro. Uma mesma requisição não pode mudar de execução ou de modelo.
- Reimportar o mesmo evento não aumenta o consumo. Importar novamente dados que
  completam campos anteriormente desconhecidos atualiza a conciliação.

`report` inclui execuções, totais agrupados por etapa e modelo em `models` e saldo
por orçamento em `budgets`. `incomplete_requests` e `unknown_requests` sinalizam
lacunas: somas de campos com valores ausentes representam só a parcela conhecida.
Não somar tetos geral e por modelo como se fossem gastos independentes.

## Subagentes, término e retomadas

```bash
.venv/bin/vp usage start exemplo --id checagem-01 --stage checagem --agent verificador --parent roteiro-01
.venv/bin/vp usage import checagem-01 eventos-verificador.jsonl
.venv/bin/vp usage finish checagem-01 --reconciled
.venv/bin/vp usage finish roteiro-01 --reconciled
```

A reserva pertence à execução raiz e cobre seus descendentes. Subagentes não
criam uma segunda reserva sobre o mesmo saldo. Importar cada evento na execução
que efetivamente o emitiu; seu vínculo não é inferido do nome do agente.

`finish` sem `--reconciled` marca `pending_reconciliation` e mantém o saldo
comprometido. `--reconciled` é a declaração de que todos os eventos chegaram;
só libera a sobra com dados completos e filhos encerrados. Uma execução sem
requisições pode ser conciliada explicitamente se de fato não houve consumo.

Reabrir o programa não zera o banco nem as reservas. Retomar o mesmo contexto
preserva o id da execução; `start` com os mesmos metadados é idempotente. Uma
execução encerrada não ganha outra reserva: se novos eventos chegarem, eles são
preservados e a raiz volta a aguardar conciliação. Uma nova rodada de trabalho
deve receber outro id e consultar o saldo acumulado.

## Operação

O banco usa `BEGIN IMMEDIATE`, espera de até cinco segundos por bloqueio, FKs e
rollback journal (`DELETE`). O SQLite 3.50.4 do ambiente antecede a correção do
[WAL-reset](https://www.sqlite.org/wal.html#walresetbug); não habilitar WAL neste
arquivo sem revisar a versão e a decisão de implantação. Transações de banco
nunca permanecem abertas durante uma chamada ao modelo.

Para backup com processos ativos, usar a API `sqlite3.Connection.backup` da
biblioteca padrão. O arquivo é local: não compartilhá-lo por uma pasta de rede.
Não editar as tabelas para liberar saldo; importar dados completos e conciliar.
Um erro de versão de schema interrompe a abertura sem apagar ou migrar os dados.

Eventos tardios e chamadas em andamento podem revelar gasto acima do teto. O
registro preserva essa diferença e impede novas reservas incompatíveis; ele
não garante um corte exato antes de cada requisição do Claude Code.
