---
name: roteiro-ficcao-historica
description: |
  Escreve o roteiro do formato "sua vida em cada nível" / "como era ser X" (história narrada em segunda pessoa,
  ADR 055): o "você" vive uma vida num degrau de uma sociedade histórica. Este formato dispensa fichas, fontes e
  claims (decisão do dono, 2026-11-05). Entrada: pauta com o recorte. Saída: outline.md e scenes.json v2. Para
  ensaio e explicativo use `roteiro-explicativo`.
argument-hint: "<episode-id>"
---

# Roteiro de história em segunda pessoa: pauta → outline.md + scenes.json

Formato: uma vida num degrau (ou em vários) de uma sociedade histórica, contada em segunda pessoa, com ritmo de história e não de aula. **Sem fichas,
sem fontes na fala, sem `claims`:** o vídeo não cita ninguém, como os modelos do formato. O contrato de `scenes.json` e os planos são os de
`roteiro-explicativo` (ADR 008); releia as seções de planos e de formato dele. Isto aqui só muda o que se exige de fato.

## Retenção e público (dados do canal, 2026-11-14)

Você escreve como **especialista em retenção e conteúdo**: cada cena dá um motivo para chegar à próxima, e cada minuto
entrega uma coisa nova da vida no degrau, nunca enchimento. Leia a seção "Retenção e público" de `roteiro-explicativo`;
os pontos que mais pesam aqui:

- **Público:** jovens de 20 a 30 anos com desânimo profundo. O "você" vive a cena ao lado de quem assiste, sem sermão,
  sem lição de moral e sem comparar a vida de hoje com a de antes para diminuir o que a pessoa sente.
- **Duração-alvo: 8 a 9 min** (teste decidido pelo dono em 2026-11-14). As pessoas ficam uns 3 min em qualquer duração;
  o que não é essencial sai.
- **Os primeiros 2 minutos recebem o maior cuidado** (cerca de 60% saem até ali, igual no ensaio e neste formato).
  Declare no `outline.md` a única mudança testável nos 2 min iniciais em relação ao vídeo anterior do formato. Para
  `idade-media-ser-rico`, a abertura era uma cena de 16 s e a pergunta do título vinha aos 19 s.

## O que continua valendo (cuidado de qualidade, não de fonte)

- **Não afirme com precisão o que você não saberia sustentar.** Número, data, preço, medida e nome específicos só entram se você os conhece com segurança; na dúvida, use
  uma forma geral ("séculos depois", "um criado para cada tarefa", "mais que um camponês ganhava em anos") em vez de um valor inventado.
  Um erro de fato num vídeo de história é o que mais envergonha o canal.
- **O recorte da pauta manda** (lugar e época), e a fala diz o recorte logo no começo. Não misture lugar e século.
- **Cada degrau abre como reconstrução** ("imagine que você nasceu…"). A fala é história de "você", nunca afirmação sobre a vida de quem assiste.
- **Nada de pessoa real como personagem**, nem citação inventada de pessoa real, nem documento inventado.
- **Nenhuma franquia, obra de terceiros ou personagem protegido.** O avatar é original, sem nome nem rosto real.
- **Roteiro ou transcrição de outro canal não é texto-base.** Só o mapa de batidas em `analise-modelo-*.md` orienta a forma; nenhuma frase, ordem de cenas, piada ou metáfora
  do vídeo-modelo é reaproveitada. O que o modelo diz como fato não é copiado nem confirmado por ele.
- Estereótipo e generalização: não escreva "na Idade Média todos…". Diga de quem e de onde se fala.

## Estrutura

1. **Abertura:** uma cena do degrau, sem apresentação. A fala diz o recorte e que a vida do "você" é reconstrução. A pergunta do título fica clara nos primeiros ~30 s.
2. **Corpo:** responde, em ordem escolhida por você (diferente da do modelo), a perguntas concretas do degrau: o que se ganhava ou possuía, quem trabalhava para você ou para quem você trabalhava,
   a casa, a comida, a roupa, o que se temia, o que não se podia fazer. Uma ideia por bloco, uma virada a cada ~1,5 a 2 min, e a cena concreta antes da explicação.
3. **Virada de fim:** o que a vida naquele degrau custava (o lado de baixo), dita com cuidado e sem carregar na tinta.
4. **Fecho:** a pergunta do funil. A recapitulação não repete a abertura nem o fecho do modelo.

## Planos e tela

Os planos são os de `roteiro-explicativo`, sem tipo novo. **Declare `"fiction": true` no topo do `scenes.json`** (ADR 055). Com a marca, `number`, `stamp`, `timeline`
e os outros planos com fato na tela entram sem `claims`; sem ela, esses planos sem `claims` são erro.

A regra de precisão acima vale em dobro na tela, porque o que aparece escrito fica:
- só entra número ou data que você sustentaria (o ano do recorte, uma ordem de grandeza redonda);
- na dúvida, use `keyword` com a forma geral;
- `chart` continua fora, porque gráfico pede uma série de dados.

`keyword` e `quote` só com texto que a narração diz. Cena e avatar desenhados são `photo` com `visual_need: illustrative_reconstruction` (`broll` é vídeo em movimento); imagem de
acervo é ilustração com crédito. Sem
`claims` no `scenes.json`.

## O que entregar

`outline.md` (pergunta, gancho, blocos, duração estimada, o recorte, a frase de divulgação para a primeira cena e a descrição, e as afirmações de fato mais arriscadas que você
escreveu, uma lista curta para o dono conferir se quiser) e `scenes.json`. Com `fiction: true`, o `vp check` não dá o alerta "frase afirmativa em cena sem claims", que neste formato
seria ruído. Passe a `humanizer-narracao` e rode `vp check` (sem erros; sem `facts.json` nem `sources.json` ele valida só o `scenes.json`).
