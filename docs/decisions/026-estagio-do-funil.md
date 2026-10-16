# 026 — Estágio do funil: topo, meio e fundo

- **Status:** aceito pelo dono em 2026-10-15 (onde fica, o que cada estágio significa e a classificação dos vídeos
  já feitos)
- **Data:** 2026-10-15
- **Etapa do roadmap:** pauta e roteiro
- **Relaciona-se com:** ADR 019 (objetivo do vídeo), ADR 025 (agendamento pelo Postiz),
  `workspace-video/docs/SPEC-WORKFLOW-FILA-E-LOOP.md` (fila de issues e `metrics.json`)

## Contexto

O dono pediu uma etapa de topo, meio e fundo de funil no fluxo dos vídeos. A fase atual é conteúdo antes de
produto: publicar conteúdo útil para um nicho, observar pedidos de planilha e modelo, testar uma solução pequena.
O objetivo do vídeo (ADR 019) diz o que o vídeo faz com o assunto (noticiar, explicar, opinar); nada dizia o que
ele pede a quem assiste, nem qual número mostra se deu certo.

## Decisão

O `scenes.json` ganha o campo opcional `funnel`, ao lado de `objective`:

- `stage`: `topo`, `meio` ou `fundo`.
- `cta`: a chamada final, como a narração a diz.
- `offer`: o que o vídeo oferece. Obrigatório no `fundo` e só existe nele.

| Estágio | Para quê | Forma | A chamada pede | Medida (em `metrics.json`, quando existir) |
|---|---|---|---|---|
| `topo` | alcance | tema amplo, gancho forte, pouco método | seguir ou compartilhar | visualizações, compartilhamentos, seguidores |
| `meio` | confiança | ensina a conta ou o método, com fonte | salvar ou comentar a dúvida | salvamentos, comentários |
| `fundo` | ação | oferece a planilha ou o modelo, grátis nesta fase | pedir (comentar a palavra, link na bio) | pedidos (`requests`) |

Regras:

1. **O estágio vem do dono**, pela pauta (skill `pauta`) ou direto, como o objetivo. O agente não escolhe.
2. **A chamada é dita.** O `vp check` avisa quando a `cta` não está na narração da última cena (acento, caixa,
   pontuação e pausas não contam) e quando ela não usa nenhum dos verbos do estágio (`FUNNEL_ASKS` em
   `app/pipeline/check.py`: `segu`, `compartilh`… no topo; `salv`, `coment` no meio; `coment`, `link`, `bio`,
   `ped`… no fundo). A conferência é por palavras: julgar se a chamada funciona fica no gate 2.
3. **Fundo nesta fase não vende.** A oferta é a planilha ou o modelo grátis; venda e preço são decisão do dono
   depois da medição. Sem produto, não há vídeo de fundo.
4. **Sem estágio, alerta.** Roteiros antigos continuam válidos; o `vp check` avisa que falta o estágio e, quando
   ele existe, mostra estágio, chamada e oferta.
5. **Na fila de issues**, cada reel leva o rótulo `funil:topo`, `funil:meio` ou `funil:fundo`, ao lado de `serie-*`
   e da etapa. Criar os rótulos no GitHub é do dono (`gh label create funil:topo` etc.).

## Classificação dos vídeos já feitos (decisão do dono em 2026-10-15)

| Vídeo | Estágio | Por quê |
|---|---|---|
| `confeitaria-ingrediente-pt` (reel 1, série 1) | meio | ensina a conta do custo do ingrediente e pede para salvar |
| `confeitaria-docinho-pt` (reel 2, série 1) | meio | ensina o custo por unidade e pede para salvar |
| Nabote: cortes 9:16 de "A Planilha é Tua" e "A Vinha Não é Sua" | topo | trecho curto para alcance, chama para o clipe |
| Nabote: clipes completos 16:9 | meio | a música inteira, para quem já chegou pelo corte |
| — | fundo | nenhum ainda; o primeiro candidato é um reel que ofereça a planilha de custo da série 1 |

Os `scenes.json` dos dois reels não ganham o campo agora: o gate 2 deles está aprovado e o arquivo aprovado é
imutável para o código (§2.6). A classificação fica aqui e nas issues (#128, #136). Os clipes do Nabote não são
episódios do pipeline (composição `Clipe`, fora do contrato do `episode.json`).

## Consequências

- `app/pipeline/schemas.py` (`Funnel`, `ScenesManifest.funnel`), `app/pipeline/check.py` (`FUNNEL_ASKS`,
  `funnel_warnings`, `funnel_summary`), `tests/test_funnel.py`; o roteiro de exemplo de `tests/test_research.py`
  passa a declarar o estágio.
- Skills `pauta` (o estágio é um item da pauta) e `roteiro-explicativo` (forma e chamada por estágio).
- O `episode.json` não muda: o estágio é do roteiro, não do render.
- `metrics.json` ainda não existe no código (D6 do spec da fila, com plano próprio); quando entrar, cada leitura
  se compara com as outras do mesmo estágio, nunca entre estágios.

## Emenda (2026-10-16, ADR 028)

- O `episode.json` ganha `series` (nome, parte e total), só para o selo do cartão final. O estágio do funil
  continua só no roteiro.
- O plano `end_card` mostra a chamada: `follow` no topo, `save` no meio, `next` quando a série continua. O `vp
  check` avisa quando a variante não é a do estágio e quando a `cta` não é dita durante o cartão. No fundo ainda
  não há cartão final.
