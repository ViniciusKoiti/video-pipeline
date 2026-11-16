# Posts do rate limiter: rascunhos locais (2026-11-16)

Data pedida pelo dono em 2026-11-16: **quinta 19/11/2026, 12h de Brasília**, públicos nas três saídas. Gates aprovados
(translation do `-en`, preview de `-pt`, `-en` e `-ig`); mídias enviadas ao Postiz (pt `3af17c37…`, en `d5477537…`, a
mesma para o Reel); pacotes e dúvida cega ("segue" ×3, pareceres `parecer-*.json`) gravados.

| Rascunho | Canal (id do Postiz, o mesmo do virtual threads agendado em 09/11) | Mídia | Gate |
| --- | --- | --- | --- |
| `post-youtube-pt.json` | YouTube `@viniciusnakahara` (`cmvx0omyy0005l26yggavdqpu`) | `../final.pt.mp4` | `short-rate-limiter-java-pt` |
| `post-youtube-en.json` | YouTube `@baixo.nivel.dev.s` (`cmvx0nn9g0003l26yf4npmb66`) | `../final.en.mp4` | `short-rate-limiter-java-en` |
| `post-instagram-en.json` | Instagram `koiti.dev` (`cmv8r4jw30001l2863lr8x1lo`, `post_type: post`) | `../final.en.mp4` (sem janela do dono: a pele segue sem licença; sem música) | `short-rate-limiter-java-ig` |

Títulos em CAIXA ALTA (pedido do dono de 2026-11-15), a partir do título provisório da pauta.

## Origem do texto

- Números: `../demo/resultado.txt` (medianas das 15 rodadas por modo, 2026-11-11, OpenJDK 25.0.5): 2867 → 51 ms nos
  clientes normais, robô com 100 aceitas e 900 recusadas, 0 normais recusados. Parâmetros da demo: 20 fichas/s,
  balde 100, 10 vagas, 50 ms, 5 clientes a 10/s, robô com 1000 de uma vez (`../demo/Demo.java`).
- Mecanismo: RFC 6585 §4 (429 Too Many Requests) e RFC 2697 (balde de fichas), em `../fontes.md`.
- O pico legítimo recusado é dito como consequência do mecanismo, não medido.
- Sem link para o código: o repositório público da demo não foi verificado, e a fala não promete link.

## Hipótese a medir aos 7 e 28 dias

Abrir com a pergunta concreta ("e a requisição 101?") e mostrar o custo (pico legítimo também recusado) ajuda o
público Java a entender o trade-off do limitador. Variável: pergunta numérica no título e na capa. Medidas: retenção
aos 3 s e completude no Studio, e comentários que respondam com um tamanho de balde (o fecho pede isso). Sem base de
comparação, é leitura descritiva.

## Pendências

1. ~~Gates~~ aprovados pelo dono em 2026-11-16.
2. Música planejada (`ytal-spirit-of-fire`, ver `../plano-animacao.md`), **mistura pendente**: o `vp short juntar` não
   mistura música. Os MP4 saem só com voz e efeitos.
3. ~~Data~~ e ~~upload~~ feitos (ids conferidos em `vp postiz integrations` em 2026-11-16).
