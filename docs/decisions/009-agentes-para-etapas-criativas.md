# 009 — Agentes para as etapas criativas; fichas de fatos; `vp check`

- **Status:** aceito
- **Data:** 2026-09-26
- **Etapa do roadmap:** #48 (fatia vertical Votorantim); muda o caminho das etapas #26–#28
- **Relaciona-se com:** ADR 002 (antecipa a numeração dos trechos), ADR 003 (o provedor de texto
  continua em aberto para o modo sem agente), ADR 006 (portas), ADR 008 (planos)

## Contexto

O exemplo de 22 s da fatia Votorantim ficou correto e sem graça. A causa foi a pesquisa rasa: cinco fatos
e nenhuma pergunta que prenda (quanto custou, por que faliu, o que mudou). O dono pediu "um agente para
cada etapa". O CLAUDE.md proibia "framework multiagente" (§2.8) e previa o Ollama local como autor do
roteiro (§7), e um modelo de 9B em CPU não dá conta de pesquisa nem de narrativa com essa qualidade.

## Decisão

1. **Agentes só nas etapas de julgamento.** Fichamento, roteiro com planos e checagem são feitos por
   subagentes do Claude Code definidos no repositório (`.claude/agents/`: `pesquisador`, `roteirista`,
   `verificador`), com o método em skills (`.claude/skills/`: `fichamento`, `roteiro-explicativo`,
   `checagem`, `humanizer-narracao`). Busca de ativos, voz, legendas e render continuam código.
2. **O código não ganha framework multiagente.** Os agentes escrevem arquivos; o `vp check` valida tudo o
   que eles escrevem, sem chamar modelo: schema, trecho existente, citação literal dentro do trecho,
   fonte conhecida, afirmação do roteiro só a partir de trecho fichado, âncoras e ritmo estimado.
3. **Portável.** O método fica nas skills (Markdown) e o contrato nos arquivos. Outro agente (Codex,
   Gemini CLI, OpenCode), um modelo local ou uma pessoa podem escrever os mesmos arquivos e passar pelo
   mesmo `vp check`. Só os arquivos de `.claude/agents/` são do Claude Code, e são curtos.
4. **Trechos numerados determinísticos** (parte da ADR 002): no texto extraído de cada fonte, um
   parágrafo (separado por linha em branco) é um trecho, `source-01#E7`. `vp excerpts <id>` gera a
   versão numerada para leitura.
5. **`facts.json`:** cada fato tem `kind` (`number`, `conflict`, `turning_point`, `mechanism`,
   `curiosity`, `context`), `why_it_matters` e evidências com **citação literal** conferida pelo código.
   `open_questions` guarda as perguntas que as fontes não respondem. `Source.interested` marca fonte
   interessada (a própria empresa ou família): fato só com ela gera alerta.
6. **Separação de papéis.** O verificador tem contexto limpo e só ferramentas de leitura (sem Write,
   Edit nem Bash). O humanizer (adaptado do blader/humanizer v3.0.0, MIT) roda depois do roteiro e antes
   da checagem; a checagem roda de novo depois de qualquer reescrita.
7. **Custo.** Os agentes usam o plano do Claude do dono, sem cobrança por chamada. Decisão do dono em
   2026-09-26: não conta como API paga (§2.1). O Ollama local continua como alternativa sem esse plano
   (etapa #27); a comparação de remotos gratuitos (ADR 003) fica para esse modo.
8. **Gates humanos não mudam:** o dono escolhe os fatos nas fichas (gate 1) e aprova o roteiro (gate 2).

## Consequências

- Etapa #26 (`vp sources`): continua código (busca, download, extração); a numeração já existe.
- Etapas #27 e #28: o caminho padrão vira agente + `vp check`; o adapter Ollama fica como alternativa.
- Com `facts.json` presente, afirmação de roteiro sem `excerpt_ids` é erro (o schema continua aceitando
  a forma antiga para os episódios v1 de teste).
- Agentes rodam numa sessão com o dono presente, o que combina com a revisão humana obrigatória (§2.5).
