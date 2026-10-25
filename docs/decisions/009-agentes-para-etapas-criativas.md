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

## Emendas

- **2026-09-26:** `Source.authors`. Fontes que compartilham um autor (mesmo por meio de outra fonte) contam
  como uma só para a independência; fato sustentado só por elas gera alerta no `vp check`. Motivo: na fatia
  Votorantim, os artigos do SciELO e do Redalyc são dos mesmos autores, e o check os contava como duas.
- **2026-09-26 (modelo de perfil de poder):** `FactKind` ganha `impact_today` (o que o público usa ou paga hoje
  por causa do personagem) e `rule` (lei, tarifa, crédito ou decisão de Estado que mudou o negócio). As skills
  passam a seguir a estrutura de perfil (gancho de impacto, ponte com o espectador, origem e vantagem, virada,
  mecanismo, regras e Estado, custo e controvérsia, presente), com perguntas de pesquisa neutras e controvérsia
  sempre atribuída. Motivo e análise em `docs/pesquisa/modelo-perfil-de-poder.md`.
- **2026-09-27 (gates por comando, #12):** nas etapas feitas por agente ou pessoa não há estado em
  `manifest.json`; a decisão humana carimba os arquivos revistos. Gate 1 (`sources`): `sources.json` +
  `facts.json`; gate 2 (`script`): `scenes.json` + `outline.md`; gate 3 (`assets`, por ativo): o arquivo de mídia
  (`sha256`). `vp approve` e `vp reject` (`--changes` para mudanças pedidas) gravam em `review.json`; aprovar um
  ativo reflete `review_status` no JSON dele, e o schema recusa sem licença, crédito ou conferência (ADR 007).
  `vp status` mostra a última decisão de cada gate e ativo e se ela ainda vale. Motivo: na abertura, a ficha F38
  mudou depois da aprovação do gate 1 e ninguém percebeu. As decisões da abertura de 2026-09-26 usaram a mesma
  receita e continuam valendo; as da fatia usaram outra, que não dá para reproduzir, e aparecem como alteradas.

## Emenda (2026-10-15): parecer do verificador exigido no gate 2

Decisão do dono, na cadeia de provas (ADR 025, emenda). O relatório do verificador não ficava guardado, e o gate
2 podia ser aprovado sem ele.

- `vp checagem <id> parecer.json` acrescenta o parecer (`verdict` approved | rejected, `problems`) ao
  `checagem.json` do episódio, carimbado com o hash de `facts.json` + `scenes.json` + `outline.md`.
- `vp approve <id> --step script` recusa sem um parecer `approved` sobre esse mesmo conteúdo. Ficha ou roteiro
  mudou depois do parecer → nova checagem. Pedir mudança ou reprovar não exige parecer.
- Saída do dono: `--sem-checagem "motivo"` aprova mesmo assim, e o motivo vai para as notas no `review.json`.
- `vp status` mostra o último parecer e se ainda vale.
- O código confere que o parecer existe e vale para o conteúdo atual, não que veio do agente.

## Emenda (2026-10-23): um modelo por agente

Decisão do dono. Os cinco agentes rodavam com `model: inherit` (o modelo da sessão), e o verificador lia o roteiro
com o mesmo modelo que o tinha escrito. Cada agente passa a declarar o modelo no seu arquivo em `.claude/agents/`,
escolhido pelo custo de um erro dele e por quem o pega depois (código, gate ou ninguém). O `/model` da sessão não
muda mais o modelo dos agentes; mudar um agente vale a partir da sessão seguinte. O item 7 (custo) continua: tudo
no plano do Claude do dono, sem API paga.

| Agente | Modelo | Motivo |
|---|---|---|
| `roteirista` | `fable` | Erro de escrita só aparece no ouvido do dono, no gate 2, e refazer custa reescrita, checagem e voz. Fica com o modelo mais forte, fixo. |
| `pesquisador` | `opus` | As fichas são a única base do roteiro; a citação literal já é conferida pelo `vp check`. |
| `verificador` | `haiku` | Escolha do dono; a recomendação era `opus`, pela leitura adversarial de trechos longos. Se a checagem deixar passar o que o gate 2 pega, rever aqui. |
| `duvida-cega` | `sonnet` | Checklist com data, fuso e JSON exato antes do agendamento; o dono ainda confirma pela regra `ask`. |
| `diretor-musical` | `haiku` | Escolhe faixa por etiqueta e texto; o `vp check` confere as âncoras e o dono decide na escuta. |

## Emenda (2026-10-24): rodadas de checagem no mesmo contexto

Decisão do dono. No `montaigne-desapego` a checagem levou quatro rodadas, cada uma em contexto limpo relendo as
quinze fontes: ~1,15 M tokens, metade do consumo dos agentes do episódio. A partir daqui: a primeira rodada continua
em contexto limpo e lê tudo; as rodadas seguintes retomam o **mesmo** verificador com a lista do que mudou, que
confere só isso contra o que já leu (o cache do contexto paga a releitura); a conferência das imagens entra nessa
mesma conversa; e há um teto de duas rodadas por versão do roteiro, além do qual o dono decide (rodada curta ou
`--sem-checagem "motivo"`). Para a primeira rodada vir menor, o roteirista passa a se conferir contra a lista dos
erros recorrentes antes de entregar (skill `roteiro-explicativo`, "Fechamento"). O `vp checagem` e o gate 2 não
mudam: o parecer continua carimbado com o hash do conteúdo, e conteúdo que muda depois do parecer pede parecer novo.
