# Direção dos vídeos técnicos: Java, animação e System Design

Decisão do dono em 2026-11-01, depois da revisão do Short de concorrência em C:
priorizar conteúdo sobre Java e considerar a animação desde o planejamento de cada vídeo.
O dono reforçou na mesma sessão: **todos os vídeos técnicos devem explicar e representar
visualmente o impacto em System Design de uma aplicação**. A prioridade Java e a ordem
da série "eu medi" estão em `fila.md`; o próximo tema escolhido é `CompletableFuture`.

## Antes de produzir voz ou render

A pauta define a pergunta que o vídeo vai responder, a linguagem do exemplo e a decisão
de System Design que o conceito ajuda a avaliar numa aplicação concreta.
O roteiro entrega a resposta e explica o mecanismo com fonte primária registrada.
O plano de animação descreve como a imagem acompanha essa explicação. Só então
se escolhem as peças do motion-kit e se prepara a voz.

Para cada cena de explicação, registrar no `plano-animacao.md` do episódio:

| Trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| O que o narrador está explicando | Valores/objetos antes da ação | Quem se conecta a quem e o significado da seta | O que se move, espera ou muda | O que o espectador deve perceber | Código, documentação ou medição |

Esse plano precisa permitir avaliar a cena antes de gastar com voz ou render.
Depois da voz, os tempos vêm dos WAVs e os movimentos são ajustados aos trechos falados.

## System Design faz parte da explicação

Cada vídeo deve ligar o mecanismo ao fluxo da aplicação e mostrar essa ligação na animação:
onde o recurso entra, o que muda no caminho da requisição ou dos dados e qual decisão
de arquitetura o espectador consegue avaliar depois de assistir.

Mostrar o benefício e o limite relevantes ao exemplo. Latência, vazão, ocupação de threads,
filas, limites de dependências, falhas e custo operacional são dimensões possíveis;
selecionar as que o conteúdo e as evidências sustentam, sem uma lista obrigatória por vídeo.
Uma frase genérica como "isso melhora a escalabilidade" no final não atende à direção.

O plano inclui uma cena ou sequência em que componentes da aplicação, conexões e estados
de espera/execução/conclusão tornam o impacto visível. A revisão verifica se essa sequência
explica uma decisão real e distingue uma ilustração de um resultado medido.

## Controle obrigatório em todo tema

Cada pauta de vídeo técnico contém o quadro abaixo preenchido para o próprio tema.
Reaplicar o controle em toda nova pauta ou revisão, sem depender de lembrar desta conversa.

| Item | O que deve estar definido | Antes da voz/render | Depois do render |
| --- | --- | --- | --- |
| Aplicação | Cenário concreto e componentes afetados | Cenário descrito na pauta | Componentes reconhecíveis na animação |
| Decisão de System Design | O que o conceito muda no desenho ou na operação da aplicação | Pergunta e decisão explícitas | Relação explicada pela fala e pelo fluxo |
| Benefício e limite | Ganho pretendido e custo/risco relevante, com evidência ou como hipótese a verificar | Fontes e demonstração necessárias identificadas | Afirmações conferidas, sem extrapolar a demonstração |
| Explicação visual | Blocos, conexões, estados e transições que mostram o impacto | Sequência planejada e rastreável à fala | Quadros de antes/durante/depois abertos e conferidos |

Antes da voz/render, uma lacuna impede avançar: registrar o que falta e completar
a pauta/plano. Depois do render, um item sem conferência impede apresentar a versão
como pronta para aprovação. Esse controle editorial não substitui os gates humanos.

## O que conta como explicação visual

- Usar caixas para os elementos do exemplo e setas para o fluxo ou para a relação que a fonte sustenta.
- Revelar os passos na ordem da explicação, destacar o elemento ativo e tornar visível a mudança de estado.
- Quando houver comparação, mostrar onde as execuções passam a se comportar de forma diferente.
- Usar texto curto para nomear ações e valores; uma tela cheia de frases entrando não substitui o fluxo.
- Dizer e mostrar a linguagem. Quando relevante, registrar versão/runtime e limites do exemplo.
- Identificar os valores escolhidos para ilustração como exemplo didático; os resultados medidos têm outra origem.

O `short-concorrencia-fluxo-pt` é a referência atual de forma: duas colunas de threads,
caixas ligadas ao contador, valores em trânsito e destaque da operação ativa.
Conteúdo e números desse exemplo são de C e não passam automaticamente a valer para Java.

## Abertura em quadros (decisão do dono, 2026-11-07)

A partir do próximo Short técnico, os primeiros 3 a 5 segundos mostram a situação em 3 ou 4 quadros, e não em um cartão de texto parado. Os quadros usam caixas, ícones e setas. Não há personagem desenhado à mão (regra de `feedback-sem-desenho-a-mao`). A pergunta de abertura aparece no último quadro, escrita na tela. Os Shorts já agendados para 08/11 não mudam: essa abertura entra numa rodada seguinte, para não misturar variáveis com o teste de ângulos.

## Conferência antes de considerar pronto

Abrir os quadros de antes, durante e depois das transições principais. Conferir se
os blocos, as setas, os valores e a fala contam a mesma história, com tempo de leitura
e sem sobreposição ao rodapé ou à interface da plataforma.

O `vp medicao` deve passar para fala/tela. Números dentro de animações Lottie também
precisam de rastreio e conferência visual: o comando não inspeciona os textos internos
desse ativo. Manter a licença e o hash dos gráficos originais registrados.

A pergunta final pode pedir a próxima linguagem ou o próximo teste. A dúvida central
e a relação com o System Design já devem estar explicadas visualmente antes desse convite.

## Prioridade Java

Preparar pautas e exemplos próprios de Java, com documentação e medição desse ambiente.
Registrar versão do JDK/JVM, comando, parâmetros e condições de execução quando medir.
Não traduzir a explicação de C nem reaproveitar seus tempos como se fossem resultados de Java.

As novas pautas seguem a aprovação do dono. Essa direção não aprova temas, medições,
gates ou publicação por antecipação e não muda a cadência por conta própria.
