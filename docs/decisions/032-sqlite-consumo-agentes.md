# 032 — SQLite local para consumo e orçamento dos agentes

- **Status:** aceito
- **Data:** 2026-10-24
- **Decisão:** dono autorizou SQLite após revisar o modelo de consumo por episódio.
- **Relaciona-se com:** ADR 006 (portas e adapters), ADR 009 (agentes editoriais).

## Contexto

O consumo da sessão mistura etapas, modelos, subagentes e retomadas. O dono pediu
controle persistente, com histórico por requisição e reservas que coordenem o saldo
entre processos. Os artefatos editoriais continuam em arquivos.

## Decisão

1. Usar `sqlite3` da biblioteca padrão, sem servidor, ORM ou dependência nova.
   `app/pipeline/usage.py` define os contratos, `app/storage/usage_sqlite.py` implementa
   a porta e `app/bootstrap.py` faz a composição.
2. Guardar `runs`, `requests`, `budgets` e `reservations` em
   `DATA_DIR/telemetry/usage.sqlite3`, ignorado pelo Git. Criar o arquivo com modo 0600
   e a pasta de telemetria com modo 0700. Versão de schema por `PRAGMA user_version`;
   uma versão desconhecida é recusada sem migrar seus dados.
3. Reservas usam `BEGIN IMMEDIATE`, integridade referencial e transações curtas. Os
   subagentes compartilham a reserva da execução raiz. Reservar todos os tetos do
   episódio em uma transação; reexecutar a mesma reserva não aumenta o saldo reservado.
4. Persistir só metadados permitidos. A importação recebe JSONL normalizado e permite
   os nomes de campos dos eventos Claude Code achatados. Não lê automaticamente os
   transcripts, não configura exportadores e não grava prompts, respostas ou credenciais.
5. Identidade estável por evento e unicidade do id de requisição do provedor quando
   presente. Reimportações não contam duas vezes. Valores desconhecidos podem ser
   completados; valores já conhecidos e vínculos não são substituídos silenciosamente.
6. Manter quatro contadores de tokens, sem equiparar sua soma à cota da assinatura.
   Dinheiro usa inteiros em milionésimos de dólar, sempre como custo estimado. Dados
   ausentes ficam `NULL`; não se infere que uma chamada com erro custou zero.
7. Uso acima do teto permanece no histórico. Sem confirmação explícita de conciliação,
   ou com uso incompleto/subagentes pendentes, a reserva continua comprometida. Eventos
   tardios fazem a execução raiz voltar a aguardar conciliação.
8. Usar rollback journal (`DELETE`) e `synchronous=FULL`. O SQLite 3.50.4 do ambiente
   é anterior à correção do WAL-reset; avaliar WAL só após atualizar para uma versão
   corrigida e medir necessidade de concorrência entre leitores e escritor.
   [Referência oficial](https://www.sqlite.org/wal.html#walresetbug).

## Consequências e limites

`vp usage` disponibiliza inicialização, orçamento, execução, reserva, importação,
conciliação e relatório. Ele não inicia o Claude Code e não intercepta chamadas.
O bloqueio implementado protege novas reservas; o controlador e a coleta automática
discutidos na arquitetura permanecem uma integração futura, dependente de medição
com os eventos reais. Esta entrega não afirma limitar a cota da assinatura.

A exceção ao banco proibido no MVP vale somente para telemetria e orçamento editorial.
Manifestos, aprovações, fontes, modelos escolhidos e política de API paga permanecem
nos contratos existentes. Não definir tetos reais pelo dono nem importar histórico
sem vínculo confiável entre episódio e execução.

Uso e formato de entrada: [docs/usage.md](../usage.md).
