# Promessa e título

Referência única da promessa e do título de um episódio, longo ou curto. A pauta escreve a seção
"Promessa e título" do `pauta.md` com este método; a checagem confere se o roteiro a entrega; a
`vp-metadados-youtube` fecha o título final; a miniatura e a `vp-engajamento` partem dela.

## As quatro perguntas

Adaptadas da equação de valor de Alex Hormozi. Responda cada uma numa linha e diga o que vai sustentá-la:
a pergunta às fontes, a ficha esperada ou "opinião do dono".

1. **Resultado:** o que a pessoa leva ao fim do vídeo: uma descoberta, uma resposta, um jeito de olhar. No
   ensaio do Cena e Conceito, o resultado é compreensão. Mudança na vida de quem assiste só entra com ficha
   `impact_today` (skill `checagem`, item 5) ou dita como hipótese ou opinião do dono.
2. **Confiança:** o que no vídeo torna a promessa crível: a fonte, o pensador, o caso, a conta feita na tela.
3. **Tempo:** prazo curto e real, quando o próprio tema tem prazo ("o último ano do aprendiz"). Sem prazo no
   tema, a resposta é "não se aplica".
4. **Esforço:** a barreira que o vídeo tira de quem assiste ("sem ler o livro inteiro"), quando ele de fato
   tira. Senão, "não se aplica".

"Não se aplica" é resposta completa, e a checagem não a cobra. O público do canal (CLAUDE.md §1) pede
acolhimento: tempo e esforço viram convite calmo, no tom de quem conversa.

## Título

Um bom título junta três coisas:

- **curiosidade:** uma pergunta ou tensão que o vídeo resolve;
- **clareza:** lido sozinho, diz do que o vídeo trata;
- **palavra-chave:** o termo que o público digitaria na busca (o pensador, a obra, o período, o conceito), de
  preferência no começo.

Proponha de duas a três opções e marque em cada uma a pergunta (1 a 4) que ela puxa mais forte. Essa marca
alimenta o teste A/B de título no YouTube e a leitura posterior da `vp-engajamento`.

## Promessa entregável

Cada palavra do título e da capa tem uma cena que a entrega e, quando é fato, uma ficha que a sustenta.
Número, superlativo e causa no título seguem as mesmas regras da checagem. O critério de parada da pauta
inclui a promessa: se as fichas não a sustentarem, o título volta ao dono antes do roteiro. Na ficção
histórica (ADR 055), o título promete a experiência narrada, sem afirmar fato histórico.

## Links internos (opcional)

Um vídeo ou playlist do próprio canal para sugerir na descrição, que segura a pessoa na sessão. A URL vem do
dono; sem ela, o campo fica "a definir pelo dono". A tela final usa o elemento "Melhor para o espectador"
(lista do Studio da `vp-metadados-youtube`), então o link interno da pauta vai para a descrição.

## Formato no `pauta.md`

```markdown
## Promessa e título

- Resultado: … (sustenta: pergunta 2 às fontes)
- Confiança: …
- Tempo: não se aplica
- Esforço: …
- Títulos: 1) … [resultado] 2) … [confiança] 3) … [esforço]
- Palavra-chave: …
- Links internos: <título do vídeo do canal> <URL> | a definir pelo dono
- Teste A/B: miniatura e/ou título | não
```
