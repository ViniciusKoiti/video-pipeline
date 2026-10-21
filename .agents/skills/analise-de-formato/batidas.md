# Batidas: a narrativa de um vídeo em linhas marcadas

Um arquivo por vídeo, `<id>.batidas.tsv`, escrito por um agente que leu só a transcrição. O `narrativa.py` conta em
cima dele; o script não interpreta o texto. Lê-se a transcrição inteira antes de marcar.

## Formato

Primeiro, três linhas de cabeçalho começando com `#`:

```
# assunto: voce
# tese: <em uma frase, com palavras suas: o que quem assiste deve sair pensando>
# mensagem: <para quem fala e o que pede: "você também faz isso", "veja como a obra é genial"…>
```

`assunto` é um destes: `voce` (a vida de quem assiste), `obra` (a obra de ficção), `mundo` (um fato, um país, uma
época), `pensador` (a vida ou a ideia de um autor).

Depois, uma linha por batida, separada por tabulação, com estas colunas:

```
inicio	tipo	bloco	ref	resumo
```

- `inicio`: `mm:ss` (ou `h:mm:ss`) da primeira palavra da batida na transcrição.
- `tipo`: um dos tipos abaixo, em caixa alta.
- `bloco`: 0 na abertura, 1 no primeiro capítulo, e assim por diante. Um bloco novo começa no `CAPITULO` ou, sem
  título dito, onde o assunto muda.
- `ref`: só nos ganchos, um código que liga o plantio ao pagamento (`g1`, `g2`); vazio nos outros.
- `resumo`: até 12 palavras suas. Nada de copiar frase da transcrição.

A última linha é `FIM`, com o tempo da última fala.

Uma batida dura até a próxima linha. Batidas de ponto (`CAPITULO`, `PROMESSA`, `PONTE`, `GANCHO-PLANTA`,
`GANCHO-PAGA`, `CHAMADA`) podem dividir o minuto com a batida longa que começa junto: escreva primeiro a de ponto.

## Tipos

| Tipo | Quando |
|---|---|
| `CASO` | uma história contada: experimento, anedota histórica, cena de obra, vida de alguém, caso do dia a dia contado como cena |
| `CONCEITO` | uma ideia nomeada ou explicada, sem história em andamento |
| `APLICA` | a ideia levada a quem assiste ou à vida comum ("a gente faz…", "você…", exemplo do cotidiano), sem ser pergunta |
| `PERGUNTA` | pergunta direta a quem assiste (mesmo retórica) |
| `CONFISSAO` | o narrador conta algo dele que o expõe: erro, vergonha, mudança de ideia, roteiro reescrito |
| `OPINIAO` | julgamento do narrador sobre o assunto, sem ser confissão |
| `PONTE` | frase que liga o fim de um bloco ao próximo |
| `CAPITULO` | título de capítulo dito na fala |
| `PROMESSA` | o que o vídeo diz que vai responder ou mostrar |
| `GANCHO-PLANTA` | algo deixado para depois ("guarda isso", "volto nisso") |
| `GANCHO-PAGA` | a volta ao que foi plantado; mesmo `ref` do plantio |
| `FECHO-VOLTA` | o fim retoma a cena ou a frase da abertura |
| `FECHO-CONTRA-SI` | o fim vira a tese contra o próprio narrador |
| `CHAMADA` | pedido a quem assiste: inscrever, comentar, compartilhar, ser membro, ler um livro |
| `FIM` | a última fala |

Na dúvida entre dois tipos, o que a batida faz para quem ouve decide: se conta, `CASO`; se explica, `CONCEITO`; se
fala de quem ouve, `APLICA`. Trechos curtos (menos de ~10 s) entram na batida vizinha, salvo os de ponto,
`CONFISSAO` e `PERGUNTA`: esses são marcados mesmo quando são uma frase só, porque são o que se quer contar.

## Exemplo

Inventado, só para mostrar a forma:

```
# assunto: voce
# tese: a gente guarda objeto velho por medo de perder quem era
# mensagem: você também faz isso, e o narrador também
00:00	CASO	0		a mudança de uma avó e as caixas no corredor
01:10	PROMESSA	0		entender por que é tão difícil jogar fora
01:25	CONFISSAO	0		o narrador tem uma gaveta de cabos
01:50	GANCHO-PLANTA	0	g1	o bilhete achado numa das caixas
02:05	CAPITULO	1		um filósofo e um navio
02:05	CASO	1		o navio que troca todas as tábuas
03:40	CONCEITO	1		identidade que continua apesar da troca
04:30	APLICA	1		a gente trata a gaveta como se fosse a gente
05:00	PERGUNTA	1		o que sobra de você sem as coisas?
05:15	PONTE	1		um psicólogo vai medir isso
18:20	GANCHO-PAGA	5	g1	o que estava escrito no bilhete
18:50	FECHO-VOLTA	5		de volta ao corredor das caixas
19:30	FECHO-CONTRA-SI	5		ele ainda não jogou a gaveta fora
19:45	FIM	5		
```
