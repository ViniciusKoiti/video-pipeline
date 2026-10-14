---
name: roteiro-explicativo
description: |
  Escreve o roteiro de um episódio explicativo (estilo How Money Works) a partir das fichas de fatos:
  pergunta central, gancho, viradas ligadas por causa, narração falada e lista de planos por cena
  (scenes.json v2, ADR 008). Use depois do fichamento aprovado e antes da checagem (ADR 009).
argument-hint: "<episode-id>"
---

# Roteiro explicativo: fichas → outline.md + scenes.json

Você escreve **só** com o que está em `data/episodes/<id>/facts.json`. Se uma frase precisa de um fato
que não está nas fichas, não escreva a frase: anote a lacuna no fim do `outline.md`.

## Saída

1. `data/episodes/<id>/outline.md`, para a revisão humana (gate 2): pergunta central, gancho, as viradas
   em ordem com os ids das fichas (F03, F07...), o fecho, e as lacunas.
2. `data/episodes/<id>/scenes.json`, no schema `ScenesManifest` (`app/pipeline/schemas.py`), com planos
   (exemplo só de formato; os textos não são fatos verificados):

```json
{
  "episode_id": "exemplo",
  "language": "pt-BR",
  "scenes": [
    {
      "id": "S02",
      "narration": "Em 1950, a Empresa A comprou uma fábrica que estava parada havia dois anos.",
      "shots": [
        {"kind": "photo", "anchor": "Em 1950", "visual_need": "historical_exact",
         "search_query": "Empresa A fábrica 1950", "asset_id": null, "motion": "push_in"},
        {"kind": "stamp", "anchor": "a Empresa A comprou", "date": "1950", "place": "Cidade A",
         "claims": [{"text": "compra em 1950", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E12"]}]},
        {"kind": "keyword", "anchor": "parada havia dois anos", "text": "parada havia dois anos"}
      ]
    }
  ]
}
```

## Estrutura do perfil de poder

Episódio sobre uma pessoa ou família e o seu dinheiro (modelo em `docs/pesquisa/modelo-perfil-de-poder.md`).
Os blocos são funções, não capítulos obrigatórios: bloco sem ficha fica de fora e vira lacuna no outline.

| Bloco | Fatia | Pergunta que responde para quem assiste |
|---|---|---|
| Gancho de impacto | 0–10% | O que isso tem a ver comigo? (algo que eu uso ou pago, ou um número que assusta) |
| Ponte com o espectador | dentro do 1º minuto | Por que eu deveria ver até o fim? (a pergunta central, dita em voz alta) |
| Origem e vantagem | 10–20% | De onde veio o primeiro dinheiro, e que acesso os outros não tinham? |
| Virada | 20–30% | Que decisão ou evento os separou dos concorrentes? |
| Mecanismo | 30–50% | Como o dinheiro de um negócio virou o próximo? |
| Regras e Estado | 50–65% | Que lei, tarifa, crédito ou decisão pública mudou o jogo? |
| Custo e controvérsia | 65–80% | Quem perdeu? O que foi decidido contra ou a favor deles, por quem e quando? |
| Presente e fecho | 80–100% | O que eles são hoje, e qual a resposta à pergunta central? |

- **A espinha é a cadeia "como virou elite", não a cronologia.** Cada elo diz o tipo de vantagem
  (capital, rede, informação, regra, timing, risco, escala) e se liga ao anterior por causa que a ficha
  sustenta ("por isso", "graças a", "mas").
- **Ponte com o espectador:** "você" só com fato de `impact_today` que o sustente, com escala e data ("o
  produto X que você compra" exige ficha dizendo quanto do mercado de X é deles, e quando).
- **Controvérsia atribuída:** "segundo o órgão X", "o órgão X acusou a empresa Y em [ano]; a empresa
  recorreu". Nunca afirme crime, intenção ou caráter. Se houver contraponto documentado, dê a ele o
  mesmo peso; não invente um "vamos ser justos" sem fato.
- **Tom:** crítico e documentado, sem rótulo de herói nem de vilão, sem gíria de canal.

### Abertura de 60–90 s (teste do modelo)

Gancho de impacto → ponte (pergunta central em voz alta) → origem comprimida em 2 ou 3 viradas → promessa
do que o episódio vai mostrar, sem responder ainda. Serve para testar a retenção dos primeiros 30 s (§12).

## Método

1. **Pergunta central.** Uma pergunta que o vídeo responde e que o público quer ver respondida
   ("como uma fábrica falida virou a semente de um dos maiores grupos do país?"). Tudo que não ajuda a
   responder sai.
2. **Gancho.** Abra com o fato mais forte, mesmo fora da ordem cronológica; num perfil, de preferência
   `impact_today` ou um `number` de escala com comparação. Depois volte ao começo.
3. **Espinha de viradas.** Três a cinco `turning_point` em ordem. Entre elas, ligue por causa: "mas"
   (um obstáculo) ou "por isso" / "então" (uma consequência). Se só couber "e depois", falta um fato de
   causa ou a cena sobra. Só escreva causa que a ficha sustenta.
4. **Mecanismo.** Onde o público perguntaria "como?", use uma ficha `mechanism`. Contexto só o mínimo.
5. **Fecho com fato.** Responda à pergunta central com um fato, sem moral nem frase de efeito.
6. **Cenas.** Uma cena = um bloco de narração de 1 a 3 frases (5 a 12 s, cerca de 65 a 160 caracteres;
   a voz Charon fala ~13 caracteres por segundo, o Kokoro ~15; o ritmo da voz configurada está em
   `config/providers.toml`, e o `vp check` estima as cenas com ele).
   **Pausas na fala (ADR 015).** Para a voz respirar num ponto exato, escreva `<short pause>` na narração, com uma
   palavra e um espaço de cada lado: "Se você quer realmente `<short pause>` aprender sobre isso, você
   `<short pause>` deve começar pelo dinheiro." Use onde o ouvinte respiraria: antes da informação nova, depois de
   uma pergunta, antes de um número que pesa; no máximo uma a cada ~15 palavras e nunca no começo ou no fim da
   cena. Não use `<long pause>` (é do lote de cenas) nem outra tag. A `anchor` de um plano é escrita **sem** a
   marca (o texto que a tela vê não a tem) e pode atravessar uma pausa. Cada marca vale 10 caracteres no tempo.
7. **Planos.** Um plano a cada 2 a 4 s (26 a 52 caracteres de narração com a Charon). `anchor` é um trecho literal da
   narração, em ordem; o primeiro plano cobre o início da cena. Escolha pelo que a frase faz (formato e
   exemplo dos tipos da ADR 011 em `planos.md`, nesta pasta; campos completos em `app/pipeline/schemas.py`):

   | A frase... | Plano |
   |---|---|
   | apresenta uma pessoa | `photo` do retrato, seguido de `lower_third` (nome e papel) |
   | mostra algo que se possa fotografar ou filmar | `photo` ou `broll` |
   | diz um número | `number`: o valor como na ficha; o `label` diz o que ele mede |
   | compara dois valores | `compare`: `side`; `before_after` para antes e depois; `scale` na mesma unidade |
   | traz uma série no tempo (3 anos ou mais) | `chart` com `type: "line"` |
   | divide um todo em partes | `chart` com `type: "share"` |
   | compara categorias | `chart` com `type: "bar"` (`bar_horizontal` para rótulos longos) |
   | liga pessoas e instituições (controla, empresta, compra, avaliza) | `network`, um passo por trecho que traz um ator novo |
   | cita um documento | `quote` com `style: "document"` e o cabeçalho da fonte; `headline` para manchete real de jornal |
   | tem a data ou o lugar como ponto | `stamp` |
   | fala de lugares ou de um deslocamento | `map`; entre países, `scope: "world"` com `routes` |
   | conta uma sequência de eventos | `timeline`, com `when` (ano ou data ISO) em cada evento |
   | tem uma frase-chave | `keyword`: até 8 palavras copiadas da narração, uma por cena |
   | fala de parentesco | `family_tree` |

   - **Imagem por baixo:** a foto ou o B-roll de uma cena continua por baixo da tarja, do carimbo, do número
     e da frase que vêm depois dele. Planeje pelo menos um `photo` ou `broll` por cena, com `visual_need`
     correto (§2.4), `search_query` específica (pessoa, lugar, ano) e `asset_id: null` (a busca de ativos é
     outra etapa); quando nenhuma imagem for possível, anote a lacuna no outline.
   - **Destaque:** em `chart`, `highlight` é o ponto que a frase comenta; sem ele, nenhum ponto se destaca.
   - **Número na convenção do idioma:** o `value` do `number` e dos lados do `compare` segue o idioma do
     episódio: em pt-BR `1.500` e `4,2`; em inglês `1,500` e `4.2`. O `vp check` recusa a convenção trocada
     ("47,6" num episódio em inglês). Em inglês, o `chart` de barras só leva valores inteiros abaixo de mil
     (o `BarChart` do kit formata em pt-BR); para valores maiores use `number`, `compare` ou `line`.
   - **Quem disse** vai na narração ("segundo o relatório da empresa"); a fonte de cada plano com `claims`
     aparece sozinha no rodapé, e o `label` fica só com o que o valor mede.
   - **Variedade:** alterne os tipos e mantenha imagem na tela; os alertas do `vp check` apontam as
     repetições.
   - **Texto que cabe na tela:** a narração explica; a tela mostra o essencial. O `vp check` alerta quando
     um texto passa do que a peça mostra (`app/pipeline/text_fit.py`):

     | Texto | Cabe |
     |---|---|
     | `label` do `number` sobre a foto ou o B-roll | 1 linha, ~60 caracteres (com 2, o painel cobre a imagem e o crédito) |
     | `label` do `number` em tela cheia | 2 linhas de ~54 |
     | `label` de cada lado do `compare` | 2 linhas de ~44 |
     | `name` e `role` do `lower_third` | 1 linha de ~34; 2 linhas de ~60 |
     | `label` de cada evento da `timeline` | 3 linhas de ~31; somando todos os eventos, ~17 caracteres por segundo do plano (6 s, ~100 caracteres) |
     | nó da `network` de onde sai uma seta | nome e papel em 2 linhas (~23 e ~30 por linha); nome longo vira sigla, apresentada antes |
     | `label` e `value` de uma seta da `network` | ~40 e ~24 caracteres |

   - **Animação do texto na tela:** o padrão de entrada, de legenda palavra a palavra e de lista que acumula está em
     `docs/guia-animacao-de-texto.md` (rascunho; onde diz *decisão aberta*, pergunte ao dono). Você não escreve
     tempo de palavra nem animação no `scenes.json`: o `keyword` segue com até 8 palavras copiadas da narração, um
     por cena, e uma lista de passos não vira vários `keyword` na mesma cena.
8. **Toda afirmação tem trecho.** Narração que afirma fato → `claims` na cena; plano que mostra número,
   data, nome, cargo, citação ou gráfico → `claims` no plano. Use `source_ids` e `excerpt_ids` das
   evidências das fichas usadas; cada aresta de `network` tem as suas próprias `claims`. O texto na tela
   repete a ficha, com o valor exato; razão, variação e soma entram quando uma ficha as traz. **Conta feita na tela (ADR 020):** só em `explicar`, com a narração dizendo a conta
   inteira, cada insumo e a regra em fichas, e a claim do plano escrevendo a expressão com o resultado
   ("18,44 ÷ 395 × 195 = R$ 9,10").
9. **Narração para ser falada** em pt-BR (voz Kokoro `pm_alex`):
   - frases de até ~20 palavras, uma ideia por frase, alternando curtas e longas;
   - anos em algarismos; outros números escritos como devem ser ditos ("mil e quinhentos operários");
   - sigla por extenso na primeira vez; nomes próprios vão para `voice/glossary.json` se a pronúncia
     falhar;
   - sem "nesse vídeo", "você não vai acreditar", "fica até o final", "e isso muda tudo".
10. **Ritmo do formato:** média de 2 a 4 s por plano; nenhum abaixo de 1,5 s; gráfico, comparação, rede,
    cronologia e documento com pelo menos 4 s, o tempo de ler.

## Objetivo do vídeo (ADR 019)

Todo roteiro declara, no `scenes.json`, o que o vídeo se propõe a fazer. O objetivo vem da pauta ou do dono;
se não veio, pergunte antes de escrever. Não escolha por ele.

```text
"objective": {
  "kinds": ["explicar"],
  "promise": "A pessoa entende o que o contrato compra.",
  "question": "O que o governo comprou com esse contrato?"
}
```

`kinds` traz de um a três tipos, na ordem em que aparecem no vídeo. O primeiro é o principal e manda na
estrutura; os outros entram como partes menores. `promise` é uma frase: o que a pessoa sabe, entende ou pensa
depois de assistir. Toda cena serve à promessa; cena que não serve sai.

| Tipo | Campo a mais | Estrutura quando é o principal | O que não cabe |
|---|---|---|---|
| `noticiar` | `event_date`: quando o fato aconteceu | o fato novo e quem diz → o que muda → o que ainda não se sabe | opinião; fato com mais de 30 dias (o `vp check` avisa: aí o vídeo explica) |
| `explicar` | `question`: a pergunta que o vídeo responde | a pergunta → o mecanismo em passos, ligados por causa → a resposta | terminar sem responder à pergunta |
| `opinar` | `thesis` e `thesis_by`: a tese e de quem ela é | a tese → os fatos que a apoiam, com fonte → o melhor argumento contrário → a tese de novo | tese escrita pelo agente; opinião dita como fato |

- **A opinião é do dono.** `thesis` chega pronta, nas palavras dele. A narração a diz como opinião, na
  primeira pessoa ou atribuída ("eu acho", "para mim"), e nunca vira número, data ou citação na tela. Os fatos
  em volta dela seguem as fichas, como sempre.
- **Tipos combinados.** Num vídeo que noticia e depois opina, a parte de notícia termina antes de a opinião
  começar, e o `outline.md` diz em que cena a opinião entra. Não misture as duas na mesma frase.
- **No `outline.md`**, logo no começo: os tipos, a promessa e, para cada cena, a que parte ela pertence.
- Se as fichas não sustentam a promessa, pare e devolva ao dono: trocar a promessa é decisão dele.

## Resumo do radar: forma, nunca fato (ADR 018)

Se a pasta do episódio tem `radar-brief.json`, leia-o **antes** de escrever. É o resumo do reels-radar: o que
anda com mais ou menos compartilhamento nos Reels do nicho. Sem o arquivo, este bloco não se aplica.

- **O que ele é.** Observação de amostra pequena, sem causa: cada item traz `n_with`, `n_without` e `chance`.
  `strength: "pattern"` é o que tem base (5+ Reels de cada lado, acaso até 10%); `hint` é hipótese a testar;
  o que está em `no_basis` não diz nada. Leia também `caveats`.
- **Para que serve.** Decidir a **forma**: tipo e tamanho da abertura, se ela fala com quem assiste, duração,
  título na tela nos primeiros segundos, pedido de comentário e tamanho da legenda do post. Os cortes estão em
  `thresholds` e o perfil dos melhores em `top`.
- **Para que não serve.** Nenhuma afirmação sai dele. As palavras de `themes` são temas que andaram bem nas
  legendas, não fatos: só entram no roteiro se uma ficha sustentar a frase que as usa. Não invente a cena
  concreta ("o seu celular…") para caber num tema. Não copie frase, título nem imagem dos Reels citados em
  `evidence` e `top.watch`.
- **"Você" continua preso às fichas.** O resumo pode dizer que falar com quem assiste anda melhor; isso não
  libera afirmar algo sobre o espectador. Sem ficha de `impact_today`, a abertura fala com ele em forma de
  pergunta.
- **Quando a forma e as fichas brigam, as fichas vencem.** Se seguir um padrão exigiria um fato que não existe,
  não siga, e diga isso.
- **No `outline.md`**, uma seção "Radar" com uma linha por padrão do resumo: seguido, ou não seguido e por quê.
  O `vp check` compara o roteiro e a legenda com os padrões que dá para medir no texto e avisa; trate cada
  alerta `radar` como os de ritmo: corrija ou justifique na seção.

## Fechamento

- Passe a skill `humanizer-narracao` na narração.
- Rode `.venv/bin/vp check <id>` até zero erros; trate os alertas de ritmo, de variedade e de texto que não
  cabe na tela.
- Entregue para o agente `verificador` (contexto limpo) antes do gate 2.
