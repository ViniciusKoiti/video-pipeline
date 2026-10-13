# Agentes no auto-play

Guia do workspace para Codex/OpenAI e outros agentes. `AGENTS.md` aponta para este arquivo
para permitir a descoberta pelo Codex. Contexto detalhado: [CLAUDE.md](CLAUDE.md).
Decisões: [docs/decisions/](docs/decisions/). Contratos: [schemas.py](app/pipeline/schemas.py).

## Contexto e limites

Este projeto produz vídeos documentais e explicativos a partir de fontes verificáveis,
em inglês ou pt-BR. O explicativo aceita horizontal e vertical; o documentário usa ffmpeg,
o explicativo usa Remotion + motion-kit. A pipeline ainda mistura CLI, arquivos e scripts
provisórios. O foco vigente é validar o template e o processo editorial; publicação é manual.

- Preserve alterações existentes e arquivos de episódios aprovados. Verifique `git status`
  antes de editar; um pedido sobre um episódio não autoriza reescrever outros.
- Custo de API permanece zero (`ALLOW_PAID_API=false`, `MAX_API_SPEND_USD=0`). A criação
  de skills não ativa chamadas à API da OpenAI nem troca provedores configurados.
- Fontes, números, datas, citações e relações causais precisam de evidência real. As fichas
  usam `excerpt_id` e `quote` literal; o roteiro usa as fichas e identifica fontes/trechos.
- Radar orienta temas candidatos e forma; nunca prova um fato do vídeo. Diferencie
  `pattern` de `hint` e registre quando o resumo está desatualizado ou não existe.
- O dono define `objective` e a tese de opinião (ADR 019). Se faltarem, avance no que
  independe disso e solicite a definição antes de fechar o roteiro. Não atribua tese ao dono.
- Só ativos com licença registrada entram na produção. Stock e geração são ilustração.
  Aprovação de IA não decide direitos, autenticidade nem os gates humanos.
- Não publique, aprove gates ou altere decisões humanas por iniciativa do agente.
  `vp check` sem erros significa validação técnica, não aprovação editorial.
- Dados pessoais do apresentador e referência de voz ficam fora do Git e de provedores
  remotos. Não leia nem exponha `.env`, tokens ou gravações para compor relatórios.
- Use a arquitetura existente de portas/adaptadores. Não acrescente framework multiagente,
  serviço, banco, dependência ou provedor para executar estes papéis no workspace (ADR 009).

Instruções explícitas do dono prevalecem. Para decisões do projeto, consulte as ADRs aceitas;
para capacidades implementadas, confira o código. Documentos antigos podem descrever planos.

## Skills e papéis

As skills ficam em `.agents/skills/`, com `SKILL.md` e metadados `agents/openai.yaml`.
Invoque com `$vp-pauta`, por exemplo. Se não aparecerem no seletor, reinicie a sessão.
O formato e a descoberta seguem a [documentação oficial de skills](https://learn.chatgpt.com/docs/build-skills).
O arquivo de entrada segue a [documentação de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

| Papel / skill | Entrada e resultado | Limite |
|---|---|---|
| Editor de pauta — `$vp-pauta` | Ângulo do dono, radar se houver → `pauta.md`, perguntas às fontes | Pauta precisa de decisão do dono antes dos downloads |
| Pesquisador — `$vp-fichamento` | Fontes baixadas e trechos → `facts.json` | Sem acrescentar fatos da memória ou da web |
| Roteirista — `$vp-roteiro` | Fichas aprovadas, pauta/objetivo → `outline.md`, `scenes.json` | Preservar significado ao humanizar e escolher planos |
| Verificador — `$vp-checagem` | Fontes, fichas e roteiro → relatório com evidência e prioridade | Só leitura; não escreveu o material revisado |
| Analista — `$vp-engajamento` | Radar e métricas fornecidas → hipóteses e próximo teste | Não inventar audiência, taxas nem ganho causal |

`.claude/agents/` e `.claude/skills/` continuam disponíveis para o fluxo existente. As skills
Codex reutilizam referências editoriais úteis sem exigir Claude Code ou os seus nomes de ferramentas.

Quando houver delegação, cada agente recebe episódio, objetivo, arquivos de entrada, saída
permitida e critério de entrega. Pesquisa de fontes independentes pode ocorrer em paralelo;
fichamento, roteiro e checagem têm dependências e passam suas entregas na sequência.
Evite dois escritores no mesmo arquivo. Passe ao verificador os artefatos e a promessa;
a revisão deve se apoiar nos trechos, sem receber a conclusão do roteirista como resposta pronta.

## Fluxo editorial

Projetos vizinhos vivem em `~/projetos/`: `motion-kit`, `lab-voz` e `radar-de-reels`.
O [mapa operacional](docs/WORKSPACE-ATUAL-E-COMPONENTES.md) e o
[diagrama de integração](docs/pipeline-hoje.mermaid) distinguem estes pontos:

- **Radar antes da pauta:** gerar o brief no radar, quando necessário/autorizado, e copiar
  com `scripts/provisorio/radar_resumo.py`. Pauta/roteiro leem a cópia do episódio; `vp check`
  compara a forma. O auto-play não coleta automaticamente dados do radar.
- **Ambiente de voz:** lab-voz é a bancada histórica do Chatterbox. O adapter usa o Python
  indicado em `CHATTERBOX_PYTHON`, com o worker do próprio auto-play; não chama `falar.py`.
  A pasta do ambiente pode variar. Rascunho usa Kokoro; final usa o provedor configurado.
- **Motion-kit no render:** o template importa o pacote instalado e fixado no `video/package.json`.
  Consultar o checkout vizinho ajuda a escolher componentes, mas mudar seu código não muda
  automaticamente o vídeo. Conferir API e pin antes de integrar um recurso.

1. Para Reels, copie o radar se já existir; escreva a pauta com público, pergunta concreta,
   objetivo do dono, promessa e limites de pesquisa. O dono decide a pauta.
2. Baixe as fontes necessárias e numere trechos. Fiche fatos, tensões, limites e lacunas;
   os fatos principais precisam de fontes independentes. Execute `vp check`; gate 1: dono.
3. Escreva roteiro e planos a partir das fichas. Ligue abertura, progressão e fechamento
   à promessa. Quando não houver base para falar do impacto na vida do público, registre
   a lacuna: não acrescente um "você" ou uma consequência pessoal sem prova.
4. Execute `vp check` e a checagem independente após a última reescrita. O verificador
   também resume em uma frase o que o vídeo entrega e indica as cenas que sustentam isso.
   Se a promessa não for cumprida, devolva o problema ao dono e ao papel responsável.
5. Gate 2: dono revisa o roteiro. Busque ativos, registre direitos e faça o gate 3.
   Depois produza voz, timing e prévia; gate 4: revisão humana da prévia e descrição.

A recomendação aqui é validar o roteiro antes de gastar tempo com voz/render, conforme
ADR 009 e CLAUDE.md §4. Há registros de gate 2 após prévia em CLAUDE.md §15; o diagrama
atual explicita a ordem recomendada. Os scripts provisórios não impõem toda essa ordem.
Os gates implementados na CLI são `sources`, `script` e `assets`. Pauta e prévia têm
revisão manual; não invente `vp approve --step preview`.

Ao corrigir uma evidência, volte ao pesquisador; ao corrigir texto ou plano, ao roteirista.
Mudança de conteúdo invalida a decisão correspondente. `vp reopen` ainda é um placeholder:
prepare a proposta de alteração separadamente e deixe explícita a necessidade de nova decisão,
sem sobrescrever o conteúdo aprovado ou editar `review.json` para contornar a restrição.

## Direcionamento e engajamento

Escolha temas pela combinação de pergunta relevante para o público, evidência disponível,
ângulo específico e viabilidade visual. Uma tendência do radar é um candidato a teste.
O roteiro precisa responder uma pergunta ou sustentar o objetivo definido pelo dono.
Gancho, título e legenda devem prometer o que o vídeo efetivamente entrega.

Antes de produzir, registre na pauta uma hipótese verificável e a métrica principal.
Após publicação autorizada, use `$vp-engajamento` com dados reais da mesma plataforma,
formato e janela de observação. Registre numerador/denominador das taxas, tráfego e tempo
de produção. Compare uma mudança por vez e declare limitações da amostra. Sem dados de
audiência próprios, a entrega é uma hipótese editorial, não um aumento comprovado.

## Comandos disponíveis

Execute da raiz; `.venv/bin/` usa o ambiente já instalado sem instalar pacotes.

```bash
.venv/bin/vp --help
.venv/bin/vp status <id>
.venv/bin/vp excerpts <id>
.venv/bin/vp check <id>
.venv/bin/python -m pytest
.venv/bin/ruff check .
```

`bench`, `excerpts`, `check`, `approve`, `reject` e `status` têm handlers reais.
`new`, `sources`, `script`, `scenes`, `assets`, `gallery`, `voice`, `subs`, `render`,
`export` e `reopen` saem com código 3: ainda não implementados.
`approve`/`reject` só registram uma decisão humana efetivamente dada.

Os scripts em `scripts/provisorio/` cobrem radar, downloads, voz e render. Leia a ajuda
e a implementação pertinente antes de executar; não presuma que imponham os gates.
Ollama é usado hoje na checagem local experimental e no benchmark, não para produzir
automaticamente o roteiro. Prompts: `prompts/local/checagem.md` e `app/pipeline/bench_data.py`.

Antes de modelos locais, benchmark ou render longo, use `cpu_probe()`; máquina limitada
invalida comparação. Um trabalho pesado por vez. Não encerre processos do dono.
Testes são offline; não rode modelos pesados, gere TTS ou renderize para validar uma
mudança apenas de documentação. Para mudanças de prompts, verifique payloads/contratos
com testes offline; qualidade semântica exige rodada local medida separadamente.

## Mapa e entregas

`app/pipeline/`: validação, estado, gates e schemas; `app/providers/`: interfaces/adapters;
`app/bootstrap.py`: composição; `app/render/` e `video/`: produção; `data/episodes/<id>/`:
artefatos privados do episódio; `data/benchmarks/`: medições e termos.

Entregue os arquivos alterados, verificações executadas, alertas e decisão pendente do
dono quando houver gate. Distingua estimativas de duração dos tempos reais medidos na voz.
As análises desta revisão estão em [pipeline e agentes](docs/analise-pipeline-agentes.md)
e [prompts locais](docs/analise-prompts-locais.md).
