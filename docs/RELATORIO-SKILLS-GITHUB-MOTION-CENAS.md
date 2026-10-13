# Skills de animação no GitHub: gaps e cenas para o motion-kit

**Data da consulta:** 13/10/2026. **Escopo:** explorar skills públicas de animação, edição e motion design no GitHub e avaliar como seus padrões podem melhorar os vídeos do auto-play usando `@viniciusk/motion-kit`.

Este relatório complementa o de [audiência e engajamento](RELATORIO-GAPS-AUDIENCIA-ENGAJAMENTO.md). As skills locais não são o objeto principal desta pesquisa: o código local foi consultado para determinar quais ideias externas já estão disponíveis, quais precisam de integração e quais exigem componentes novos.

O [mapa do workspace e dos componentes](WORKSPACE-ATUAL-E-COMPONENTES.md) detalha o fluxo implementado. A conferência adicional do pin e das declarações do pacote instalado confirmou as capacidades listadas abaixo; elas não dependem apenas do checkout mais recente.

## Resumo

As melhores oportunidades são **guiar a compreensão com movimento**: mostrar um mecanismo em etapas, manter uma lista enquanto a fala avança, destacar o ponto certo de um gráfico e apresentar a evidência documental com clareza. Legendas por palavra precisam de tempos reais; animação de entrada por palavra já existe no kit, mas não substitui legendagem sincronizada.

Não falta uma coleção genérica de efeitos. O kit já tem câmera, parallax, transições, gráficos, grafo, retrato recortado e anotações. Parte dessas capacidades não está exposta pelos contratos do auto-play. Também há diferenças importantes entre o kit fixado pelo projeto e o checkout mais recente.

**Recomendação inicial:** estudar os packs do iart-ai de explicação, dados e direção de movimento, usando o repositório oficial do Remotion para conferir implementação. Aproveitar princípios e receitas; evitar importar um fluxo completo que substitua fontes, gates, voz e render existentes.

## Tópico 1 — Repositórios e skills externos examinados

### Subtópico 1.1 — Fontes e o que aproveitar

| Repositório / fonte primária | O que foi examinado | Aplicação ao nosso projeto |
|---|---|---|
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Router `remotion-best-practices` e referências de markup e captions | Conferir APIs e regras de render por quadro. O router consultado declara versão 4.0.535; o auto-play usa Remotion 4.0.529. |
| [iart-ai/explainer-video-skills](https://github.com/iart-ai/explainer-video-skills) | Skills `explainer-video`, `diagram-animation`, `whiteboard-animation` e `isometric-animation` | Storyboard ligado à fala, revelação de mecanismos e desenhos explicativos. |
| [iart-ai/data-animation-skills](https://github.com/iart-ai/data-animation-skills) | `animated-infographic` e `chart-animation` | Composição estática clara antes da animação; foco sequencial em dados e relações. |
| [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | Catálogo e `caption-animation` | Blocos curtos de legenda, destaque da palavra ativa e timing vindo do áudio. |
| [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | `motion-art-direction`, `shot-composition` e `beat-sync-editing` | Vocabulário curto de movimento, um foco por plano, reenquadramento e cortes motivados. |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | `SKILL.md`, `motion-patterns.md` e `design-rules.md` | Referências de acabamento e inspeção visual; filtrar prescrições que animam tudo. |

O [hub iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) serviu para descobrir os packs específicos. O hub agrega links; a avaliação acima se apoia nos arquivos dos packs, não em contagem de estrelas ou promessas de retenção.

### Subtópico 1.2 — Compatibilidade: não copiar as receitas literalmente

**Problema:** algumas skills misturam exemplos para web e vídeo. A skill de diagrama inclui GSAP, CSS e `requestAnimationFrame`; a de captions contém `transition` CSS no exemplo React. Esses mecanismos não devem controlar o tempo de um render Remotion. Algumas também recomendam serviços de transcrição e padrões de idioma que não correspondem ao pt-BR e à voz local do projeto.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Extrair princípios e implementar no kit, recomendado | Reaproveitar hierarquia, ordem de revelação e critérios de revisão; derivar cada movimento do frame usando os componentes existentes. | Preserva determinismo e arquitetura; exige adaptação dos exemplos. |
| 2 — Usar uma skill externa como referência técnica pontual | Consultar apenas o tema necessário, como captions ou composição, e confrontar a API com a versão instalada. | Menos instruções conflitantes; exige seleção por tarefa. |
| 3 — Adotar um pack inteiro após revisão | Ajustar seus gatilhos e instruções ao nosso pipeline antes de usá-lo na produção. | Pode acelerar trabalho recorrente; amplia manutenção e conflitos de orientação. |

**Resumo:** uma skill ensina um método; não garante compatibilidade de código, qualidade visual ou aumento de audiência.

**Ação:** começar pelo caminho 1. Para implementação, conferir a [referência oficial de markup](https://github.com/remotion-dev/skills/blob/main/skills/remotion-best-practices/remotion-markup/REFERENCE.md). Não foram instaladas skills, dependências ou ferramentas nesta análise.

## Tópico 2 — O que já temos e onde estão os gaps

### Subtópico 2.1 — Versão consumida versus biblioteca atual

**Problema:** `video/package.json` fixa o kit no SHA `b39301244999c6b062445c90942c7fe470815496`; o checkout local do motion-kit está em `7cd8a10b9bd7965b3e9bfcb11f3a0c69ee982a9a`. No checkout, o código fica em `packages/motion-kit/src/`; no pin consultado, em `src/`. Não se pode assumir que uma capacidade encontrada no checkout esteja disponível no vídeo.

**Evidências locais:** [dependência fixada](../video/package.json), [despacho de planos](../video/src/ShotView.tsx), [integrações editoriais](../video/src/Editorial.tsx). Consulta direta do histórico git confirmou no pin `SceneSlide`, `Pipeline`, `KineticHeadline.wordFrames`, `StyleTheme.motion`, `Callout`, `DrawPath`, `BarList`, `ShareList` e `LottieAsset`. As declarações de `dist` do pacote instalado, versão 0.3.0, também expõem estilos, anotações e Lottie. `ShareChart` já tem variantes `bar100` e `donut` no pin.

| Capacidade | Biblioteca | Auto-play | Natureza do gap |
|---|---|---|---|
| Texto com entradas por palavra | `KineticHeadline.wordFrames`, inclusive no pin | `KeywordShot` não passa esse campo | Timing e integração; não criar outro headline |
| Legenda com palavra ativa | Não foi identificado componente `WordCaption` | Cues por frase; SRT ainda não fechado no fluxo examinado | Componente de legenda e alinhamento |
| Transições variadas | `SceneSlide` já tem modos no pin | `Scene.tsx` fixa `mode="push"` entre planos de tela cheia | Direção e integração |
| Etapas com fluxo | `Pipeline` no pin; grafos também existem | Não há plano de processo; rede excluída do vertical | Layout, contrato e sincronização |
| Lista textual acumulativa | Sem componente equivalente identificado | Não há plano `list` | Componente novo e contrato |
| Tabela com texto/unidades misturados | Sem `ValueTable` identificado | `compare` tem dois lados | Componente novo e contrato |
| Limite linear e zonas | `Gauge` radial existe; sem `LimitMeter` identificado | Não há plano específico | Componente novo, se houver pauta concreta |
| Anotação e zoom de detalhe | `Marker`, `Highlighter`, `CameraPath` e `Callout` já disponíveis | Sem receita de detalhe/anotação ligada às claims | Integração e contrato |
| Tokens de movimento | Pin e pacote instalado têm `StyleTheme.motion` | Template usa `MotionThemeProvider`, sem `StyleProvider` | Integração com estilos; não recriar tokens |
| Mapa / documento / cronologia | Componentes já existem | Excluídos de `PORTRAIT_SHOT_KINDS` | Adaptação vertical e contrato |
| Ilustração animada pronta | `LottieAsset` já está no pin e nas declarações instaladas; peers opcionais | Sem plano de animação no schema | Integração de ativos, peers e direitos, não outro gerador |
| Trilha e efeitos | `MusicBed` e `SfxTrack` | Render de cena visual; voz juntada depois em ffmpeg | Mixagem e montagem final |

**Solução-descrição:** integrar primeiro capacidades confirmadas no pin; atualizar a dependência apenas para uma entrega que realmente exija APIs novas. Atualizar tudo de uma vez oferece mais recursos, mas aumenta a superfície de regressão de estilos, fontes, bundle e render.

**Resumo:** os documentos antigos de componentes e texto são úteis, mas estão parcialmente defasados: tokens de movimento e `Callout` já estão disponíveis na versão consumida. O auto-play ainda não os integra ao seu fluxo editorial.

**Ação:** antes de cada implementação, registrar “existe no pin”, “existe só no checkout” ou “precisa nascer”. Conferir fonte, export e build publicado; o pin declarado sozinho não comprova qual conteúdo está em `node_modules`.

## Tópico 3 — Direção do movimento

### Subtópico 3.1 — Falta escolher o movimento pela função da cena

**Problema:** o template usa avanço lento de câmera em vários cartões e `push` entre planos de tela cheia. Há variedade de componentes, mas não uma escolha explícita entre apresentar, revelar, comparar e concluir. Se tudo se move da mesma maneira, a animação pode deixar de orientar o olhar. A concorrência entre fonte, apresentador, número e texto precisa ser conferida visualmente; não foi medida nesta análise.

**Referência externa:** [motion-art-direction](https://github.com/iart-ai/motion-design-skills/blob/main/skills/motion-art-direction/SKILL.md) propõe hierarquia entre movimento principal, apoio e ambiente. A recomendação útil é restringir o vocabulário e deixar estático o que não precisa mover.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Direção editorial curta, recomendado | Para cada plano, declarar foco, o que entra, o que permanece e o momento de leitura. Escolher corte, entrada sóbria ou revelação por função. | Não exige componente novo; depende da aplicação consistente. |
| 2 — Integrar tokens de estilo existentes | Usar `StyleTheme.motion` da versão disponível, preservando o padrão editorial. | Centraliza o comportamento; requer revisar componentes que ainda usam defaults próprios. |
| 3 — Perfis por série | Criar apenas perfis necessários, por exemplo explicação sóbria e clipe musical. | Mais adequação ao conteúdo; mais combinações para verificar. |

**Resumo:** melhorar animação começa pela decisão do que merece atenção.

**Ação:** descrever a direção de três planos: gancho, mecanismo e resposta. Conferir se há um único movimento principal em cada momento.

### Subtópico 3.2 — Acabamento e transições sem competição com a informação

**Problema:** a skill de haidrrrry exige movimento em todas as imagens, entradas com múltiplas propriedades e atividade nos elementos parados. Essas prescrições podem conflitar com leitura de documento, gráfico financeiro e a identidade sóbria do projeto. Já temos fundos, grain, parallax e câmera; copiá-los criaria duplicação.

**Referência externa:** [regras da skill](https://github.com/haidrrrry/claude-remotion-skill/blob/main/remotion-motion-graphics/SKILL.md) e [receitas de acabamento](https://github.com/haidrrrry/claude-remotion-skill/blob/main/remotion-motion-graphics/references/motion-patterns.md).

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Corte e continuidade de foco, recomendado | Usar cortes claros e manter posição de um elemento relacionado entre planos quando isso mostrar continuidade. | Pouco custo; exige planejar o par de planos. |
| 2 — Expor poucos modos de `SceneSlide` | Escolher um modo motivado por mudança de assunto ou revelação, usando a API já existente. | Acrescenta variedade; transição não cria sobreposição real entre renders independentes. |
| 3 — Acabamento pontual | Usar câmera/parallax apenas no ativo cujo conteúdo ganha com profundidade. | Mais presença visual; exige camadas e pode dificultar leitura ou aumentar render. |

**Resumo:** não adotar “tudo deve animar” como regra. Movimento contínuo pode ser adequado a fluxo de dados; easing não precisa substituir velocidade constante em toda situação.

**Ação:** comparar um corte simples com uma transição motivada no mesmo par de planos. Evitar criar uma nova biblioteca de efeitos.

## Tópico 4 — Cenas que faltam ou precisam ser integradas

### Subtópico 4.1 — Legenda por palavra sincronizada

**Problema:** a entrada `wordFrames` de um headline não destaca necessariamente a palavra falada no bloco de legenda. O fluxo atual usa cues por frase e ainda depende da entrega do SRT. Dividir o tempo da frase igualmente ou por caracteres gera uma aparência sincronizada que pode estar errada no áudio.

**Referências externas:** [caption-animation](https://github.com/iart-ai/tiktok-video-skills/blob/main/skills/caption-animation/SKILL.md) e [captions do Remotion](https://github.com/remotion-dev/skills/blob/main/skills/remotion-best-practices/remotion-captions/REFERENCE.md). Aproveitar timestamps reais e agrupamento legível; manter tipografia e área segura do projeto, sem copiar posição ou cores de outro canal.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Fechar legenda por frase primeiro | Gerar SRT revisado e completar a montagem existente. | Resolve acessibilidade cedo; ainda sem destaque por palavra. |
| 2 — `WordCaption` no kit | Receber palavras com tempos e desenhar blocos curtos com palavra ativa; integração após alinhamento. | Maior controle e reutilização; exige componente, timing e tratamento de pontuação/pausas. |
| 3 — Compor com ferramentas oficiais | Usar recursos de captions compatíveis com a versão do projeto, envoltos na identidade do kit. | Menos lógica própria; pode exigir pacote adicional e avaliação de licença/versão. |

**Resumo:** é uma lacuna real, mas o alinhamento vem antes do efeito.

**Ação:** validar em pt-BR uma frase com número, nome próprio e pausa. Conferir também se planos `keyword` ocultam informações que não aparecem no destaque. Não usar `medium.en` como solução de transcrição para português.

### Subtópico 4.2 — Lista que acumula: passos, fatores e resumo

**Problema:** `keyword` troca a frase; não mantém os itens anteriores. Em `votorantim-5-jeitos`, o público percorre fatores distribuídos em cenas sem um suporte visual acumulativo. Não foi identificado `RevealList` no kit. A spec local `docs/specs/reveal-list.md` já descreve parte do trabalho: não precisa ser reescrita como um novo projeto.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — `RevealList` com tempos por item, recomendado | Revelar cada item na ordem da fala, reservar espaço e manter os anteriores. | Boa orientação; cria plano e exige limites de leitura. |
| 2 — Lista estática em plano único | Mostrar poucos itens de uma vez e destacar o atual. | Menos animação/timing; entrega a estrutura antes da fala. |
| 3 — Resumo em grade no final | Reunir apenas o que já foi explicado numa composição de poucos cartões. | Menor necessidade de estado durante o vídeo; não ajuda a orientação no miolo. |

**Resumo:** falta uma cena de enumeração, não mais variantes de headline.

**Ação:** prototipar de três a cinco itens curtos no vertical. Se a lista atravessar cenas, transportar seu estado em props: renders separados não compartilham estado React. Tempos aproximados continuam exigindo revisão; não apresentá-los como alinhamento exato.

### Subtópico 4.3 — Mecanismo em etapas: entrada → processamento → resultado

**Problema:** `thiel-contrato-pt` descreve um processo em S03 com mídia, frases e comparação. `proteina-igual-pt` explica composição e aproveitamento sem uma cena própria para o mecanismo. Temos `Pipeline` e `ExpandingNetwork`, mas a rede é proibida em retrato e `Pipeline` não tem contrato integrado. Uma seta deve representar apenas uma relação que a ficha sustente.

**Referência externa:** [diagram-animation](https://github.com/iart-ai/explainer-video-skills/blob/main/skills/diagram-animation/SKILL.md) trabalha revelação progressiva e foco no elemento ativo. Aproveitar o método; portar exemplos web para animação por frame.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Processo linear curto, recomendado | Adaptar `Pipeline` para etapas legíveis em retrato e entrada ligada à fala. | Reutiliza base; layout atual é horizontal e o stagger é uniforme. |
| 2 — Pequena rede vertical | Adaptar `ExpandingNetwork` para poucos nós e uma cadeia claramente documentada. | Cobre relações mais ricas; layout, rótulos e regras do apresentador custam mais. |
| 3 — Etapas em cartões sequenciais | Um cartão por passo com continuidade visual entre planos. | Menor alteração; contexto global fica menos visível. |

**Resumo:** prioridade alta: mostrar como algo funciona pode substituir uma sequência de cartões sem relação visual.

**Ação:** escolher um mecanismo já fichado e limitar o primeiro caso a três etapas. Não animar fluxo de dados pessoais, dinheiro ou causalidade apenas porque a metáfora parece convincente.

### Subtópico 4.4 — Evidência documental no vertical

**Problema:** `DocumentPage` existe, mas `quote` está fora dos planos permitidos em retrato. Em assuntos de contratos e relatórios, foto genérica e selo de data não mostram ao público o trecho que sustenta a afirmação. Um documento inteiro encolhido para caber também não resolve.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Cartão documental de trecho, recomendado | Adaptar `DocumentPage` com cabeçalho curto, citação e destaque, deixando clara a recriação gráfica. | Reutiliza componente e claims; depende de layout vertical e corte fiel do texto. |
| 2 — Recorte real do documento | Usar imagem licenciada/autorizada do trecho com zoom e anotação. | Aproxima o público da evidência; exige direitos, resolução e cuidado de recorte. |
| 3 — Citação textual atribuída | Mostrar o trecho como texto e fonte, sem simular uma página. | Simples e legível; menor contexto visual do documento. |

**Resumo:** falta liberar uma receita documental legível no retrato, não inventar um componente de jornal do zero.

**Ação:** validar um trecho já fichado em 720×1280, mantendo negação, atribuição e ressalvas. Documento recriado não deve parecer screenshot autêntico.

### Subtópico 4.5 — Apontar um detalhe na imagem ou no gráfico

**Problema:** o kit já tem instrumentos de anotação, incluindo `Callout`, `Dimension` e `TickRuler`. O auto-play não tem uma receita que vincule ponto, zoom e texto à informação narrada. `chart.highlight` muda a aparência do dado, mas o schema não expõe `LineChart.annotate` nem várias séries. Isso limita explicações de detalhe sem que falte a base gráfica.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Destaque de dado existente, recomendado primeiro | Expor a anotação de `LineChart` ou usar `Marker` no ponto já identificado. | Menor mudança; depende de acesso correto à posição do dado. |
| 2 — Receita com `Callout` e câmera | Integrar `Callout` disponível, com alvo e texto vinculados às claims. | Mais reutilização em imagens; exige coordenadas e prevenção de colisões. |
| 3 — Recorte editorial simples | Mostrar um crop que preserve o assunto e a legenda explicativa. | Menor custo; perde contexto se o recorte for excessivo. |

**Resumo:** integrar anotações existentes antes de construir `ChartCallout` novo.

**Ação:** um detalhe, uma chamada e um foco por plano. O `Callout` atual não evita automaticamente cruzamentos entre rótulos; o layout precisa ser conferido.

### Subtópico 4.6 — Tabela de valores e comparação de três ou mais itens

**Problema:** `compare` representa exatamente dois lados. `proteina-igual-pt` apresenta três fontes de proteína; os temas de economia e planos/taxas podem misturar porcentagens, valores e texto. Usar barras para unidades incompatíveis ou vários pares em sequência dificulta comparar. Não foi identificado `ValueTable` no kit; já existe spec local em `docs/specs/value-table.md`.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Barras horizontais com unidade comum | Usar `BarChart` ou `BarList` quando os dados forem de fato comparáveis. | Sem novo componente; não aceita comparação de métricas diferentes como se fossem uma escala. |
| 2 — `ValueTable` compacta | Linhas com rótulo, valor, unidade e nota; destacar a linha da fala. | Cobre dados mistos; cria componente e regras de densidade. |
| 3 — Dois itens por comparação | Dividir a explicação em pares com a mesma base. | Mantém contrato atual; aumenta duração e exige memória do espectador. |

**Resumo:** tabela é lacuna real; gráfico com mais barras não substitui tabela de dados heterogêneos.

**Ação:** usar o caminho 1 em uma comparação homogênea. Fazer tabela apenas quando uma pauta aprovada exigir unidades ou notas misturadas.

### Subtópico 4.7 — Linha do tempo e localização em retrato

**Problema:** mapa e timeline existem no kit, mas o contrato vertical os exclui. Discussões de países e datas ficam em selos ou fotos. Encolher uma cena horizontal perde legibilidade. A [skill shot-composition](https://github.com/iart-ai/motion-design-skills/blob/main/skills/shot-composition/SKILL.md) é uma boa referência para recompor o layout por formato; seus percentuais de margem não substituem a área segura já adotada no projeto.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Locator com um ou dois lugares | Compor `GeoMap` com poucos rótulos e reenquadramento próprio para retrato. | Reutiliza geografia; exige validar dados e área segura. |
| 2 — Timeline vertical curta | Mostrar poucos eventos em coluna e destacar o evento narrado. | Dá orientação temporal; depende de adaptação de layout e timing. |
| 3 — Selo acompanhado de mídia | Usar os planos atuais quando localização/data forem só contexto. | Nenhum plano novo; não explica deslocamento ou relação entre eventos. |

**Resumo:** adaptar somente a cena exigida pelo argumento, sem liberar automaticamente todos os layouts horizontais em 9:16.

**Ação:** mapa para explicar localização ou rota; timeline para explicar sequência. Para texto de prazos sem escala temporal necessária, a futura tabela pode bastar.

### Subtópico 4.8 — Limite, proporção e decomposição de dinheiro

**Problema:** falta uma cena de limiar linear, e `ShareChart` não tem waffle no código examinado. `share` já cobre proporções; não criar outro gráfico de participação apenas por variedade. Cascata de receitas e taxas exige valores explícitos e regras para números derivados. As specs locais `docs/specs/limit-meter.md` e `docs/specs/waffle-chart.md` já delimitam caminhos.

**Referência externa:** [animated-infographic](https://github.com/iart-ai/data-animation-skills/blob/main/skills/animated-infographic/SKILL.md) ajuda a organizar ícone, valor, rótulo e conector em sequência. Essa referência não comprova necessidade de todos os gráficos abaixo.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Reutilizar `ShareChart` / `ValueCompare` | Manter participação ou dois valores quando isso responde à pergunta. | Nenhum componente novo; não mostra um limite rotulado ou decomposição passo a passo. |
| 2 — `LimitMeter` ou waffle conforme a pauta | Criar limite linear para limiar; waffle como variante de proporção para “em cada 100”. | Novas possibilidades didáticas; precisam de caso concreto e limites de arredondamento. |
| 3 — Cascata com valores fichados | Mostrar entrada, deduções e resultado já explícitos na ficha. | Explica dinheiro que sobra; exige contrato e consistência contábil, sem cálculo editorial oculto. |

**Resumo:** são cenas condicionais à pauta, abaixo de legenda, mecanismo e lista na prioridade geral.

**Ação:** escolher apenas o gráfico exigido pelo próximo roteiro. Não representar aproveitamento de proteína como contagem de pessoas: a visualização precisa manter o significado do denominador.

### Subtópico 4.9 — Ilustração de mecanismo: desenho e isometria

**Problema:** B-roll pode contextualizar, mas nem sempre demonstra um mecanismo abstrato. O kit disponível já tem `DrawPath`, anotações, componentes de movimento 2.5D e `LottieAsset`; falta uma receita editorial no auto-play que use essas peças com ativos aprovados. Não foi identificada uma cena específica de diagrama explodido no contrato.

**Referências externas:** [whiteboard-animation](https://github.com/iart-ai/explainer-video-skills/blob/main/skills/whiteboard-animation/SKILL.md) e [isometric-animation](https://github.com/iart-ai/explainer-video-skills/blob/main/skills/isometric-animation/SKILL.md) apresentam famílias úteis para explorar. Adotar o mecanismo visual, sem exigir mão desenhando ou um motor 3D novo.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Desenho vetorial simples, recomendado | Traços e setas entram por etapas, com rótulos e relação documentada. | Determinístico e leve; exige desenho adequado ao assunto. |
| 2 — Animação Lottie revisada | Integrar `LottieAsset` para um mecanismo com arquivo adequado e licença registrada. | Reaproveita animação pronta; exige peers, direitos e revisão da semântica do ativo. |
| 3 — Camadas 2.5D | Separar partes de uma figura e revelar função/estrutura com movimentos moderados. | Mais profundidade; aumenta produção de ativos, risco de colisões e custo de render. |

**Resumo:** prioridade posterior e dependente de caso. Para três etapas abstratas, a cena de processo costuma bastar.

**Ação:** provar primeiro o desenho estático. Uma ilustração esquemática deve ser apresentada como explicação visual, sem simular registro histórico ou científico específico.

## Tópico 5 — Edição e validação

### Subtópico 5.1 — Cortes na fala, continuidade e trilha

**Problema:** o auto-play renderiza cenas visuais independentes e junta voz depois em ffmpeg. Adicionar `MusicBed` dentro de uma composição não comprova que o áudio será preservado pelo fluxo final. Uma transição gráfica também não cria um J-cut ou L-cut real, em que áudio e imagem mudam em momentos diferentes. Esses recursos exigem olhar a montagem final.

**Referência externa:** [beat-sync-editing](https://github.com/iart-ai/motion-design-skills/blob/main/skills/beat-sync-editing/SKILL.md) distingue cortes motivados e continuidade de áudio. Nos explicativos, priorizar a frase; no clipe musical, o beat pode dirigir o corte.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Marcar beats editoriais na fala, recomendado | Cortar em mudança de ideia, pergunta ou resposta; conferir áudio final antes de acelerar planos. | Compatível com o pipeline; ainda exige revisão manual. |
| 2 — Mixar trilha discreta na montagem final | Integrar uma faixa licenciada com fades e volume subordinado à voz. | Evita duplicar música por cena; exige conferir nível, inteligibilidade e continuidade. |
| 3 — Separar timeline de áudio e imagem | Permitir J/L-cuts apenas se um caso concreto justificar alterar a montagem. | Mais liberdade de edição; muda o contrato e aumenta complexidade de sincronização. |

**Resumo:** efeitos sonoros em todo corte e speed ramps não são prioridades para vídeos explicativos baseados em dados.

**Ação:** começar por cortes no áudio aprovado. Usar os componentes de áudio existentes somente depois de confirmar como sua saída entra na montagem final.

### Subtópico 5.2 — Faltam critérios de revisão temporal, além da folha de quadros

**Problema:** o projeto já tem vídeo-régua e comparação de quadros. Isso ajuda a detectar mudanças, mas um quadro final correto não demonstra leitura, fluidez, sincronização ou preservação da mensagem durante entradas e saídas. As skills externas reforçam inspeção em vários momentos; não devem impor render completo para toda alteração.

**Solução-descrição:**

| Caminho | Descrição | Tradeoff |
|---|---|---|
| 1 — Amostra temporal por cena, recomendado | Conferir antes da entrada, durante o movimento, na pausa de leitura e na saída; depois assistir ao trecho com áudio. | Baixo custo e reaproveita ferramentas; não cobre todos os frames. |
| 2 — Pequena régua de cenas novas | Acrescentar demos neutras de legenda, lista, mecanismo e documento em retrato. | Comparação reproduzível; demos precisam acompanhar as APIs. |
| 3 — Checks automáticos de geometria e valores | Testar tempos, posições e valor final onde há lógica; manter julgamento visual humano. | Detecta regressões objetivas; não mede qualidade narrativa. |

**Resumo:** tipagem, build e render bem-sucedidos são necessários, mas não certificam qualidade de animação.

**Ação:** para cada nova cena, declarar o que o público deve enxergar em cada etapa e verificar esse comportamento. Não foi gerado render nesta pesquisa.

## Resumo e ação — Backlog priorizado

As prioridades são uma avaliação para este pipeline, não um ranking universal das skills externas. Esforço é relativo: **S** integração pequena; **M** componente/layout com contrato; **L** alteração de montagem ou timing. Não são estimativas de dias.

| Ordem | Entrega | Reutilização | Esforço provável | Por que vem aqui |
|---|---|---|---|---|
| 1 | SRT completo e alinhamento real; depois legenda por palavra | Porta de alinhamento, cues, `KineticHeadline` apenas para headline | M–L | Sustenta leitura e toda sincronização posterior |
| 2 | Direção de movimento de três cenas e revisão temporal | Câmera, `SceneSlide`, régua | S | Melhora uso do que existe antes de ampliar a biblioteca |
| 3 | Processo curto em retrato | `Pipeline` ou rede pequena | M | Mostra mecanismos hoje distribuídos em cartões |
| 4 | Lista acumulativa | Spec `RevealList` existente | M | Organiza fatores, passos e resumos |
| 5 | Documento/trecho e anotação de detalhe | `DocumentPage`, `Highlighter`, `Marker`, `Callout` | M | Aproxima explicação e evidência |
| 6 | Comparação múltipla; tabela quando necessária | Barras atuais; spec `ValueTable` | S–M | Resolve comparação sem inventar escalas |
| 7 | Locator ou timeline curta no vertical | `GeoMap` / `YearTimeline` como base | M | Depende da pauta geográfica/temporal |
| 8 | Limite, waffle ou cascata | Gráficos e specs existentes | M–L | Só vale com pergunta que exige esse tipo |
| 9 | Ilustração vetorial/Lottie/2.5D | Primitivos já disponíveis no kit | M–L | Depois de comprovar que processo simples não basta |
| 10 | Trilha e continuidade de áudio | Mixagem final; `MusicBed`/`SfxTrack` quando compatíveis | M–L | Evitar competir com a voz e alterar montagem cedo |

### Integração mínima de um novo tipo de plano

1. **Kit:** componente ou variante com API pública, export, documentação, demo, build e `dist` conforme as regras do motion-kit.
2. **Contrato:** ADR aplicável, schema Python, união de planos, restrição de retrato, claims e espelho em `video/src/types.ts`.
3. **Timing e render:** âncoras/tempos, props do adapter, `ShotView`, `Editorial` e regras de camadas/legendas em `Scene` quando afetadas.
4. **Revisão:** `text_fit`, ritmo, cantos do apresentador, testes de contratos e revisão visual/temporal. Ao criar novos diretórios de template, incluir seus arquivos no `template_hash` para não reutilizar cache obsoleto.
5. **Uso editorial:** somente depois de existir a implementação, documentar a receita para o roteirista. Atualizar pin/lock quando necessário e conferir a versão efetivamente instalada.

Não criar um `kind` genérico que aceite TSX arbitrário só para integrar rápido: perderíamos validação de fatos e consistência do contrato. O `motion-video` do checkout já aceita grid, animação e outros tipos, mas é outro contrato e sua produção atual é silenciosa; não substitui diretamente o render narrado do auto-play.

### O que adiar

Bar chart race sem série temporal adequada, 3D/WebGL/Manim como novo motor, mãos desenhando como obrigação, transições aleatórias, grain em toda tela, overshoot em dados financeiros e intros longas de logo. Nenhum desses recursos resolve por si só as lacunas prioritárias identificadas.

## Limites e riscos

Foram consultadas fontes primárias no GitHub e arquivos reais de biblioteca, template, schemas, timing e specs. A disponibilidade de componentes foi separada entre o pin e o checkout e conferida nas declarações públicas do pacote instalado. Isso não equivale a executar todas as APIs ou auditar cada bundle compilado. Os arquivos locais e branches públicos podem mudar após esta consulta.

Não foram instaladas skills nem executados seus scripts; seus `SKILL.md` foram tratados como material de pesquisa. Não houve alteração de código, atualização de dependência, render, escuta ou teste de audiência. As cenas propostas ainda precisam de revisão visual em 16:9/9:16 quando implementadas.

As specs citadas por caminho estavam sem versionamento na revisão e não fazem parte dos commits destes relatórios. As descrições aqui preservam as decisões necessárias mesmo em uma cópia sem esses rascunhos locais.

**Risco principal:** importar receitas de skills externas sem adaptar tempo, contratos e identidade pode aumentar efeitos e reduzir compreensão. As prioridades e benefícios aqui são julgamento técnico/editorial, não ganho medido de engajamento.
