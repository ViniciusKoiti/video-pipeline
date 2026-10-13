# Relatório de gaps de audiência e engajamento

**Data:** 12/10/2026. **Escopo:** análise do repositório no estado local, incluindo alterações em andamento e amostra de episódios locais. **Objetivo:** identificar onde o conteúdo pode perder atenção, compreensão, interação e retorno, com caminhos de solução e tradeoffs.

Para entender o estado operacional conferido em 13/10, consulte o [mapa do workspace e dos componentes](WORKSPACE-ATUAL-E-COMPONENTES.md).

## Resumo executivo

O projeto produz vídeos narrados a partir de fontes verificáveis, com revisão humana, controle de direitos e render em Remotion ou ffmpeg. A base protege bem a confiabilidade do conteúdo; a jornada de audiência ainda precisa conectar promessa, abertura, compreensão, resposta final e aprendizado após publicação.

Os pontos mais urgentes são: completar legendas no fluxo de montagem, validar se o roteiro entrega uma promessa clara e criar um registro simples de resultados próprios. Depois vêm posicionamento, embalagem, ritmo e continuidade entre vídeos. Melhorar animações antes de resolver esses pontos pode aumentar o trabalho sem esclarecer se o conteúdo interessa ao público.

**Limite da conclusão:** não foram acessados painéis de audiência, vídeos publicados ou contas externas. Não há base para afirmar que o canal já perde determinado percentual de público. Os gaps de implementação e documentação são observados; seus efeitos sobre audiência são hipóteses a testar.

Há uma divergência de estado: `CLAUDE.md` e o roadmap registram ausência de publicação no pipeline editorial, enquanto a agenda do clipe registra agendamentos no YouTube via Postiz. Agendamento não comprova publicação ou desempenho. As frentes devem ser tratadas separadamente até confirmar seu estado real.

### Resumo de prioridades

| Prioridade | Gap | Onde pode perder público | Primeira ação |
|---|---|---|---|
| P0 | Legendas não chegam ao render pelo fluxo examinado | Compreensão sem áudio e acessibilidade | Completar um vertical com SRT revisado |
| P0 | Objetivo opcional e entrega sem avaliação semântica | Expectativa e satisfação final | Revisar promessa e resposta no gate 2 |
| P0 | Aprendizado com dados próprios ainda não operacionalizado | Repetição de erros | Criar registro manual por publicação |
| P1 | Públicos e formatos distintos sem recorte consolidado | Retorno e identificação | Escolher uma série piloto |
| P1 | Aberturas exigem contexto ou interpretação cedo | Primeiros segundos | Testar compreensão do gancho |
| P1 | Título, capa e primeiro quadro fora do fluxo principal | Entrada no vídeo | Revisar embalagem junto da promessa |
| P1 | Informação densa e encerramentos pouco conclusivos | Miolo e conclusão | Dar uma função clara a cada bloco |
| P1 | Legendas podem desaparecer em planos `keyword` | Continuidade da compreensão | Comparar a frase visual com a fala completa |
| P1 | Radar externo pode orientar além da evidência | Escolha de forma e duração | Transformar associações em testes próprios |
| P2 | Ritmo e sincronização aproximados | Esforço de leitura | Revisar planos densos no áudio final |
| P2 | CTA e continuidade de série pouco específicos | Comentários e retorno | Definir uma próxima ação relevante |
| P2 | Produção lenta e revisão concentrada no dono | Frequência e aprendizado | Medir trabalho por etapa |

P0 significa prioridade antes de usar uma publicação como teste confiável, não incidente já ocorrido. P1 vem no próximo ciclo editorial; P2 depende dos resultados e da capacidade de produção. Não é necessário implementar todos os caminhos: escolher um por problema inicialmente.

## Tópico 1 — Posicionamento e público

### Subtópico 1.1 — Recorte editorial e expectativa de retorno

**Problema:** o README apresenta documentários históricos em inglês; `CLAUDE.md` inclui dinheiro e poder em português; os episódios locais também incluem proteína, Armênia e privacidade. A frente musical tem canal identificado próprio. Essa diversidade não prova mistura no mesmo canal, mas deixa pouco clara a unidade usada para validar audiência. Se assuntos e idiomas diferentes forem publicados para o mesmo público sem uma promessa comum, alguém pode gostar de um vídeo e não querer o seguinte.

**Evidências:** [README](../README.md), [contexto e validação de audiência](../CLAUDE.md), [roadmap](ROADMAP.md), agenda local `renders/clipe/agenda-postagens.md`; episódios locais `proteina-igual-pt`, `armenia-brasil` e `thiel-empresa-pt`.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Série piloto única, recomendado | Escolher um público, idioma, tema e formato para um pequeno lote editorial. Registrar a promessa da série na pauta. | Facilita comparação e retorno; adia outras ideias interessantes. |
| 2 — Séries nomeadas no mesmo canal | Separar assuntos em séries com identidade e promessa explícitas. | Preserva variedade; a audiência de uma série pode não acompanhar as demais. |
| 3 — Canais separados por público | Separar somente quando houver incompatibilidade comprovada de público e capacidade de manter cada frente. | Expectativa mais clara; multiplica operação e divide o aprendizado inicial. |

**Resumo:** variedade de protótipos é útil; variedade sem recorte de validação dificulta saber para quem o projeto funciona.

**Ação:** dono define o recorte do próximo lote em cinco linhas: público, idioma, problema, promessa e formato. Comparar retorno apenas dentro desse recorte; não criar novos canais por hipótese.

## Tópico 2 — Promessa e satisfação

### Subtópico 2.1 — O roteiro pode ser correto e não entregar um ponto claro

**Problema:** `objective` é opcional no schema; sua ausência gera alerta. O checker valida estrutura e idade da notícia, mas não se o roteiro entrega a promessa. A ADR 019 documenta o caso de `thiel-empresa-pt`, considerado sem objetivo pelo dono. Nos quatro verticais examinados, o campo ainda está ausente. O risco é manter frases verdadeiras que não constroem uma resposta reconhecível.

**Evidências:** ADR 019 local (`docs/decisions/019-objetivo-do-video.md`), [schemas](../app/pipeline/schemas.py), [checagem](../app/pipeline/check.py). Amostra: `thiel-empresa-pt`, `thiel-contrato-pt`, `proteina-igual-pt` e `armenia-brasil`.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Revisão explícita no gate 2, recomendado | Escrever promessa e resposta final; marcar como cada cena contribui. O revisor resume o ponto com suas palavras. | Pouco trabalho técnico; depende da disciplina de revisão. |
| 2 — Exigir objetivo nos roteiros novos | Impedir aprovação de um novo roteiro sem objetivo, mantendo compatibilidade com o acervo antigo. | Evita omissão; campo preenchido ainda pode esconder um roteiro sem direção. |
| 3 — Leitura independente de compreensão | Pedir a alguém que não participou da pesquisa para explicar o que aprendeu e qual pergunta foi respondida. | Detecta pressupostos invisíveis ao autor; acrescenta uma rodada editorial. |

**Resumo:** declarar intenção é necessário; conferir a entrega é uma etapa distinta.

**Ação:** antes da próxima voz final, revisar um episódio com três perguntas: “o que promete?”, “onde responde?” e “qual cena não ajuda?”. Mudanças em conteúdo aprovado devem passar pela revisão correspondente.

## Tópico 3 — Entrada e descoberta

### Subtópico 3.1 — Gancho com contexto insuficiente ou benefício tardio

**Problema:** `thiel-empresa-pt` começa perguntando se a pessoa conhece Palantir e logo apresenta um software e uma parceria. `proteina-igual-pt` abre com percentuais antes de dizer o que medem. `armenia-brasil` pergunta o que é possível comparar, sem antecipar uma descoberta específica. Um espectador novo pode precisar interpretar nomes e números antes de entender por que continuar. São hipóteses sobre os textos, não abandono comprovado.

**Evidências:** primeiras cenas dos episódios locais citados; [skill de roteiro](../.claude/skills/roteiro-explicativo/SKILL.md). O próprio método já prevê gancho e pergunta central: o gap é a aplicação e sua verificação.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Benefício ou conflito primeiro, recomendado | Abrir com uma pergunta concreta que as fichas respondam; apresentar siglas e contexto depois. | Reduz esforço inicial; exige cortar contexto que o autor pode considerar importante. |
| 2 — Resultado com contexto mínimo | Mostrar um achado verificável já com unidade, comparação ou significado. | Entrega valor cedo; pode reduzir curiosidade se todo o argumento for antecipado. |
| 3 — Exemplo visual primeiro | Começar por imagem relevante e uma frase curta que introduza o mecanismo. | Ajuda entendimento; depende de um ativo adequado e aprovado. |

**Resumo:** a primeira frase precisa dar um motivo compreensível para assistir, sem inventar ligação com a vida do espectador.

**Ação:** preparar duas aberturas textuais com as mesmas fichas. Mostrar a pessoas do público pretendido e perguntar o que esperam aprender. Escolher pela clareza; após publicação, verificar permanência inicial e abandono.

### Subtópico 3.2 — Título, capa e primeiro quadro sem entrega padronizada

**Problema:** o script de montagem atribui ao manifesto um título técnico com o ID e “rascunho”. A ADR vertical deixa título e capa fora do escopo. A agenda musical tem títulos próprios, portanto o gap não é ausência absoluta de embalagem: falta um procedimento equivalente e verificável no pipeline editorial. Sem ele, uma boa pesquisa pode chegar ao público com apresentação pouco clara ou prometer algo diferente do conteúdo.

**Evidências:** [montagem provisória](../scripts/provisorio/montar_episodio.py), [ADR 014](decisions/014-perfil-vertical.md), agenda local `renders/clipe/agenda-postagens.md`.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Pacote editorial manual, recomendado | Entregar título público, capa ou primeiro quadro, legenda do post e promessa antes do gate 4. | Sem infraestrutura nova; exige revisão por publicação. |
| 2 — Duas alternativas de embalagem | Criar duas opções sustentadas pelo mesmo conteúdo e escolher após teste de entendimento. | Reduz escolha por gosto pessoal; custa design e o teste não garante mais alcance. |
| 3 — Modelos por série | Reutilizar composição e critérios de título, variando o ponto central. | Produção mais rápida; pode tornar peças parecidas demais. |

**Resumo:** a promessa deve ser consistente entre apresentação e entrega. CTR de miniatura em vídeos longos e decisão de permanecer no feed de Shorts medem momentos diferentes, conforme a [documentação do YouTube](https://support.google.com/youtube/answer/12220281?hl=en).

**Ação:** acrescentar a revisão da embalagem ao gate 4 existente. Registrar CTR por origem quando disponível e permanência no feed de Shorts; não usar uma única taxa para todos os formatos.

## Tópico 4 — Compreensão e acessibilidade

### Subtópico 4.1 — Legendas suportadas, mas ausentes na montagem examinada

**Problema:** os quatro verticais examinados têm `captions: null` e não têm SRT na raiz do episódio. O script monta `EpisodeManifest` sem preencher `captions`. O render queima legendas no vertical somente se esse campo estiver presente. Assim, seguir esse fluxo pode gerar um vídeo final sem legendas completas, embora existam frases-chave na tela. Quem depende da leitura pode perder informação central.

**Evidências:** [montagem](../scripts/provisorio/montar_episodio.py), [condição de legendas no render](../app/render/remotion.py), [porta de alinhamento](../app/providers/alignment/base.py), [ADR 014](decisions/014-perfil-vertical.md). O adapter de alinhamento ainda não é uma etapa completa nesse caminho.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — SRT manual revisado, recomendado para validar | Alinhar o roteiro ao áudio aprovado, salvar SRT e vincular ao manifesto antes do render. | Resolve sem nova dependência; exige tempo por episódio. |
| 2 — Alinhamento local assistido | Implementar a porta existente com alinhamento e revisão de nomes e tempos. | Reduz trabalho repetido; adiciona processamento e erros precisam ser corrigidos. |
| 3 — Editor externo com export de SRT | Usar uma ferramenta já disponível e trazer o arquivo revisado para o pipeline. | Pode acelerar o piloto; cria uma etapa externa e requer avaliar condições de uso. |

**Resumo:** frases em destaque não substituem a fala completa. O suporte de render já existe; falta fechar a entrega.

**Ação:** completar um vertical e assistir integralmente sem áudio. Antes de publicar um vertical narrado, verificar existência do SRT, vínculo no manifesto, sincronização e legibilidade.

### Subtópico 4.2 — Frase-chave oculta toda a legenda durante o plano

**Problema:** `Scene.tsx` zera a opacidade da camada de legendas durante qualquer plano `keyword`. A justificativa é evitar duplicação, mas uma palavra ou frase curta pode representar só parte da fala. Nesse caso, quando houver SRT, o espectador sem áudio perde o restante da mensagem durante esse intervalo. Trata-se de comportamento confirmado; sua ocorrência depende da combinação concreta de fala, cue e plano.

**Evidências:** [Scene.tsx](../video/src/Scene.tsx), [regra de planos](../.claude/skills/roteiro-explicativo/SKILL.md).

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Manter legenda em área própria | Exibir fala completa e destaque sem colisão. | Preserva informação; pode aumentar carga visual e duplicação. |
| 2 — Ocultar apenas com equivalência | Suprimir a legenda somente quando o destaque representar toda a fala daquele intervalo. | Mantém limpeza visual; equivalência e tempos exigem cuidado. |
| 3 — Reescrever ou encurtar o plano, recomendado primeiro | Ajustar o destaque e sua duração para que a informação falada continue compreensível. | Pouca alteração técnica; limita escolhas de roteiro e precisa de revisão por plano. |

**Resumo:** a regra de evitar repetição precisa preservar a informação para quem não ouve.

**Ação:** depois de completar o SRT, revisar todos os planos `keyword` sem som. Corrigir os intervalos em que a frase visual não cobre o sentido da fala.

## Tópico 5 — Narrativa e retenção no miolo

### Subtópico 5.1 — Dados e ressalvas podem substituir a progressão da explicação

**Problema:** `thiel-empresa-pt` termina com a declaração da empresa sobre sua atividade; `armenia-brasil` encerra com uma ressalva sobre as fontes. Esses encerramentos podem ser necessários para precisão, mas, isoladamente, não deixam uma resposta editorial forte. `proteina-igual-pt` oferece contraste: responde à pergunta central e dá uma conclusão. O risco é o público receber informações e ressalvas sem conseguir resumir a descoberta.

**Evidências:** cenas finais dos episódios locais citados; diagnóstico na ADR 019 local (`docs/decisions/019-objetivo-do-video.md`); método de mecanismo e fecho na [skill de roteiro](../.claude/skills/roteiro-explicativo/SKILL.md).

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Pergunta, mecanismo e resposta, recomendado | Dar a cada bloco uma função e terminar com o que foi demonstrado, incluindo o limite da evidência. | Melhora compreensão; remove fatos interessantes que não servem ao objetivo. |
| 2 — Dividir em episódios autônomos | Separar mecanismo, controvérsia e impacto quando não couberem com clareza. | Menos densidade; precisa dar resposta útil em cada parte, sem depender da próxima. |
| 3 — Reorganizar visualmente a evidência | Trocar enumeração por uma comparação ou sequência causal sustentada pelas fichas. | Torna relações visíveis; exige plano adequado e não autoriza inventar causalidade. |

**Resumo:** preservar ressalvas e fontes, mas conectá-las à resposta que o vídeo prometeu.

**Ação:** revisar o fecho de um episódio: uma frase de resposta e uma de limite, quando necessário. Verificar se uma pessoa consegue explicar o mecanismo após assistir; depois comparar esse trecho com a curva de retenção.

## Tópico 6 — Ritmo, sincronização e carga visual

### Subtópico 6.1 — Média de duração não garante tempo de compreensão

**Problema:** `shot_bounds` distribui tempos pela posição dos caracteres, proporcional à duração real da cena. Isso não identifica o instante exato de cada palavra no áudio. `pacing_warnings` verifica planos abaixo de 1,5 s e média por formato; não mede compreensão. `text_fit` usa estimativas de largura e verifica tempo de leitura da linha do tempo, sem cobrir igualmente todos os tipos. Uma comparação pode entrar antes da fala ou sair antes de ser entendida mesmo com média aceitável.

**Evidências:** [timing e ritmo](../app/pipeline/shots.py), [estimativas de texto](../app/pipeline/text_fit.py), [regras de planos](../.claude/skills/roteiro-explicativo/SKILL.md). Já existem alertas úteis: o gap é seu alcance, não ausência de checagem.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Revisão pontual no áudio final, recomendado | Conferir números, comparações e transições densas; ajustar texto ou âncora. | Menor implementação; revisão manual continua necessária. |
| 2 — Alinhamento por palavra compartilhado com legendas | Reutilizar tempos do alinhador para planos quando o erro aproximado for relevante. | Resolve duas necessidades; amplia contratos e testes de timing. |
| 3 — Alertas de leitura por tipo | Expandir os avisos de densidade aos componentes usados no piloto. | Ajuda triagem; estimativas continuam sem provar leitura real. |

**Resumo:** cortar mais rápido não é automaticamente melhor. A informação precisa coincidir com a fala e permanecer tempo suficiente.

**Ação:** revisar uma comparação e um plano numérico no tamanho de um celular, com voz final. Não redesenhar todos os componentes antes de identificar quais realmente falham.

## Tópico 7 — Uso do radar e qualidade do aprendizado

### Subtópico 7.1 — Associação em conteúdo de terceiros pode virar regra rígida

**Problema:** o radar orienta abertura, duração e legenda por associações observadas em Reels de terceiros. A ADR 018 documenta uma amostra de 34 Reels e leitura em boa parte das legendas escritas. O código avisa corretamente que se trata de orientação, mas os pedidos de roteiro podem transformar duração ou vocabulário em obrigação. Compartilhamento externo não prova retenção, compreensão ou preferência do público próprio.

**Evidências:** [ADR 018](decisions/018-radar-de-reels-no-workflow.md), [leitura do radar](../app/pipeline/radar.py), prompt local `docs/prompts-de-sessao/2026-10-12-thiel-dados-e-vigilancia.md`, [pauta](../.claude/skills/pauta/SKILL.md).

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Hipótese por publicação, recomendado | Escolher uma característica do radar e registrar o que se espera observar no público próprio. | Aprendizado claro; amostras pequenas continuam inconclusivas. |
| 2 — Evidência própria como prioridade | Usar o radar para ideias e as séries publicadas para decidir duração e estrutura. | Mais aderente ao canal; exige histórico comparável. |
| 3 — Ampliar leitura dos exemplos | Assistir aos exemplos relevantes e distinguir fala, edição e legenda antes de aplicar uma orientação. | Reduz erro de interpretação; custa pesquisa, e coleta adicional pode ter custo. |

**Resumo:** o radar já reconhece seus limites. Falta transformar orientação em uma hipótese verificável, sem impor conteúdo que as fontes não sustentam.

**Ação:** adicionar ao outline “hipótese de forma”, “métrica”, “resultado” e “limite”. Não escolher automaticamente a duração acima de 72 s apenas porque essa faixa apareceu na amostra externa.

## Tópico 8 — Engajamento e retorno

### Subtópico 8.1 — Pedido genérico de comentário e próxima etapa indefinida

**Problema:** `thiel-contrato-pt` termina perguntando qual pergunta a pessoa faria sobre o contrato. Isso abre conversa, mas exige inventar uma pergunta depois de absorver assunto técnico. O radar detecta presença de pedido de comentário, sem avaliar sua pertinência. A agenda musical prevê ligação entre Shorts e o clipe completo, porém esse vínculo é manual e não tem confirmação de conclusão no documento examinado. Não há evidência de uma rotina equivalente nas séries editoriais.

**Evidências:** fecho local de `thiel-contrato-pt`; [checagem do radar](../app/pipeline/radar.py); agenda local `renders/clipe/agenda-postagens.md`.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Pergunta específica, recomendado | Pedir uma dúvida ou experiência diretamente ligada ao mecanismo explicado, sem sugerir fatos não demonstrados. | Facilita resposta; pergunta estreita pode limitar a discussão. |
| 2 — Próximo conteúdo relevante | Indicar outro vídeo disponível que aprofunde a questão e conferir o vínculo após publicar. | Dá continuidade; depende de acervo e das funções da plataforma. |
| 3 — Encerrar só com a resposta | Dispensar CTA quando ele não acrescenta valor. | Preserva um final forte; interação terá de vir espontaneamente. |

**Resumo:** presença de CTA não garante engajamento; a ação precisa fazer sentido para quem acabou de assistir.

**Ação:** escolher uma única ação principal por peça. Ler comentários para identificar compreensão e dúvidas reais; registrar retorno ao conteúdo relacionado quando houver dados disponíveis.

## Tópico 9 — Métricas próprias e diagnóstico

### Subtópico 9.1 — Plano de medição existe, registro operacional não foi identificado

**Problema:** `CLAUDE.md` prevê coleta manual aos 7 e 28 dias para vídeos longos. Na amostra de arquivos examinada, não foi identificado histórico próprio de audiência que permita ligar versões, resultados e decisões. Benchmarks medem produção e qualidade técnica. Sem essa ligação, é possível mudar voz, tema, duração e visual simultaneamente e não saber qual ajuste ajudou.

**Evidências:** [validação no contexto do projeto](../CLAUDE.md), [benchmarks](../data/benchmarks/README.md), [evolução do template](../data/benchmarks/evolucao-template.md). Ausência observada no repositório não significa inexistência de métricas em uma conta externa.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — CSV ou planilha manual, recomendado | Registrar plataforma, URL, série, versão, duração, hipótese, métricas, data da coleta e decisão. | Custo e manutenção baixos; depende de preenchimento consistente. |
| 2 — Resumo por episódio | Manter `resultado.md` com métricas e leitura da curva de retenção. | Aproxima decisão do conteúdo; comparação entre episódios fica menos prática. |
| 3 — Importação de export disponível | Consolidar relatórios da plataforma apenas quando a coleta manual virar gargalo. | Economiza trabalho em volume; formatos e definições podem variar. |

**Resumo:** separar descoberta, atenção, compreensão, interação e retorno. O [YouTube explica como ler quedas e picos de retenção](https://support.google.com/youtube/answer/9314415?hl=en); as [métricas de Shorts incluem assistir versus deslizar](https://support.google.com/youtube/answer/12942217?hl=en). Um pico também pode indicar repetição por dificuldade, não apenas interesse.

**Ação:** preparar o registro antes da primeira publicação do lote. Usar janelas fixas de 7 e 28 dias para comparação; registrar plataforma, duração, origem e denominador de cada taxa. Em Shorts, incluir visualizações engajadas quando disponíveis. Não juntar views de plataformas diferentes numa taxa única.

### Subtópico 9.2 — Como interpretar os resultados sem prometer causalidade

| Sinal observado | Hipótese inicial | Ação de investigação |
|---|---|---|
| Poucas impressões, boa retenção | Distribuição limitada ou tema com pouco alcance | Comparar origem e público antes de reescrever o roteiro |
| Impressões e poucos cliques em vídeo longo | Título ou capa pouco claros para aquele público | Testar entendimento da embalagem |
| Muitos deslizam no início de um Short | Primeiro quadro e gancho pouco relevantes ou claros | Rever abertura com as mesmas fichas |
| Entrada boa e queda no miolo | Promessa desalinhada, contexto excessivo ou explicação difícil | Relacionar timestamp às cenas e pedir leitura independente |
| Pico em um gráfico | Interesse ou necessidade de rever para entender | Testar leitura; não presumir sucesso do gráfico |
| Boa conclusão e pouco retorno | Peça útil, mas sem promessa de série reconhecível | Rever posicionamento e próximo conteúdo |
| Comentários numerosos | Interesse, dúvida, discordância ou conflito | Classificar o conteúdo dos comentários antes de comemorar volume |

Essa tabela orienta investigação, não diagnostica automaticamente. Não há meta universal de CTR, retenção ou comentário neste relatório; usar histórico comparável e registrar quando a amostra não permite concluir.

## Tópico 10 — Capacidade de execução

### Subtópico 10.1 — Tempo técnico pode atrasar aprendizado editorial

**Problema:** há comandos ainda não implementados e scripts provisórios cobrindo partes do fluxo. A voz final local é registrada como cerca de 30 vezes mais lenta que o tempo real, e pesquisa e aprovação dependem do dono. O projeto tem uma decisão explícita de priorizar template com calma; isso é legítimo. Para validar audiência, porém, o gargalo será concluir peças comparáveis e medir resultados, não apenas melhorar o template.

**Evidências:** [estado e voz](../CLAUDE.md), [pendências](ROADMAP.md), [montagem provisória](../scripts/provisorio/montar_episodio.py), [ADR da voz](decisions/016-voz-clonada-do-dono.md).

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Congelar visual durante o piloto, recomendado | Usar o template disponível e resolver apenas bloqueios concretos de compreensão, legenda e export. | Acelera conclusão; limita exploração visual no período. |
| 2 — Voz de rascunho até roteiro aprovado | Validar texto e tempos preliminares antes da voz final; reaproveitar cache quando válido. | Evita síntese cara em tempo; voz final ainda exige revisão de timing. |
| 3 — Automatizar o maior gargalo medido | Medir horas humanas e tempo de máquina por etapa e concluir apenas o comando que mais economiza trabalho. | Ataca custo real; deixa outras etapas provisórias por mais tempo. |

**Resumo:** não remover gates de fontes e direitos para ganhar frequência. Reduzir retrabalho e complexidade antes de ampliar a produção.

**Ação:** medir um episódio de ponta a ponta e escolher um gargalo. A agenda de publicação deve caber no tempo real disponível; publicar permanece uma decisão separada do dono.

## Resumo e ação — Sequência recomendada

1. **Escolher o recorte:** definir uma série e confirmar quais frentes já estão publicadas, agendadas ou apenas em teste. Responsável: dono.
2. **Fechar uma peça completa:** revisar objetivo, abertura, resposta e ressalvas; completar SRT e vínculo no render. Responsáveis: roteiro e produção, com aprovação do dono.
3. **Conferir compreensão:** assistir no celular, com e sem áudio; revisar planos `keyword`, comparações e números. Responsável: revisão final.
4. **Preparar embalagem e medição:** registrar título, capa ou primeiro quadro, hipótese e próxima ação. Criar CSV manual sem integração nova. Responsável: publicação.
5. **Quando autorizado publicar:** concluir os gates existentes e publicar um pequeno lote no mesmo recorte. Variar uma hipótese principal por vez; isso ajuda interpretação, mas não transforma publicações orgânicas em experimento controlado.
6. **Revisar resultados:** comparar peças do mesmo formato e janela; relacionar dúvidas e quedas às cenas; escolher a próxima mudança pelo problema observado.

### Critérios mínimos para o próximo piloto

- Uma promessa que o revisor consegue repetir e uma resposta reconhecível no fecho.
- Todos os fatos continuam sustentados por fichas e todos os ativos têm direitos aprovados.
- Vertical narrado compreensível sem áudio, com legendas sincronizadas e leitura conferida.
- Embalagem coerente com o que o vídeo entrega.
- Uma hipótese editorial registrada e um local definido para resultados aos 7 e 28 dias.
- Próxima ação útil, quando existir; sem obrigação de pedir comentários em toda peça.

## Cobertura e limitações da análise

Foram examinados README, contexto, roadmap, análise anterior, decisões sobre objetivo, radar, vertical e voz, skills locais de pauta e roteiro, schemas e checks, timing, texto na tela, montagem, suporte de legendas no render, template de cena e apresentador, configurações de dependências, agenda musical e amostra de episódios locais. Os links para código e documentos usam o estado atual da árvore de trabalho; algumas mudanças ainda não estão commitadas.

Os episódios locais usados como evidência ficam fora do Git: seus IDs foram registrados para localizar os casos nesta máquina, sem copiar fontes, imagens ou dados de voz para o relatório. Uma cópia isolada do repositório pode não conter esses exemplos.

Agenda musical, ADR 019 e prompt Thiel também estavam sem versionamento na revisão. Seus caminhos foram mantidos como referências locais; este relatório não incorpora esses arquivos nem as outras mudanças em andamento.

Não foram reproduzidos ou ouvidos os vídeos, capturadas telas das publicações, medidos contraste e tamanho efetivo de texto no celular, executados renders ou testes, nem auditados todos os providers e aspectos de segurança. Este é um diagnóstico editorial e do fluxo de produção, baseado em arquivos, e não uma auditoria visual dos vídeos ou uma medição de audiência real.

**Risco central:** mudar muitas variáveis antes de registrar resultados próprios pode gerar mais produção sem aprendizado. As soluções acima são caminhos de teste; nenhuma garante alcance ou engajamento.
