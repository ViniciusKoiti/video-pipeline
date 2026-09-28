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
6. **Cenas.** Uma cena = um bloco de narração de 1 a 3 frases (5 a 12 s, cerca de 75 a 180 caracteres;
   a voz fala ~15 caracteres por segundo).
7. **Planos.** Um plano a cada 2 a 4 s (30 a 60 caracteres de narração). `anchor` é um trecho literal da
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
   - **Quem disse** vai na narração ("segundo o relatório da empresa"); a fonte de cada plano com `claims`
     aparece sozinha no rodapé, e o `label` fica só com o que o valor mede.
   - **Variedade:** alterne os tipos e mantenha imagem na tela; os alertas do `vp check` apontam as
     repetições.
8. **Toda afirmação tem trecho.** Narração que afirma fato → `claims` na cena; plano que mostra número,
   data, nome, cargo, citação ou gráfico → `claims` no plano. Use `source_ids` e `excerpt_ids` das
   evidências das fichas usadas; cada aresta de `network` tem as suas próprias `claims`. O texto na tela
   repete a ficha, com o valor exato; razão, variação e soma entram quando uma ficha as traz.
9. **Narração para ser falada** em pt-BR (voz Kokoro `pm_alex`):
   - frases de até ~20 palavras, uma ideia por frase, alternando curtas e longas;
   - anos em algarismos; outros números escritos como devem ser ditos ("mil e quinhentos operários");
   - sigla por extenso na primeira vez; nomes próprios vão para `voice/glossary.json` se a pronúncia
     falhar;
   - sem "nesse vídeo", "você não vai acreditar", "fica até o final", "e isso muda tudo".
10. **Ritmo do formato:** média de 2 a 4 s por plano; nenhum abaixo de 1,5 s; gráfico, comparação, rede,
    cronologia e documento com pelo menos 4 s, o tempo de ler.

## Fechamento

- Passe a skill `humanizer-narracao` na narração.
- Rode `.venv/bin/vp check <id>` até zero erros; trate os alertas de ritmo e de variedade.
- Entregue para o agente `verificador` (contexto limpo) antes do gate 2.
