---
name: vp-metadados-youtube
description: >
  Monte a embalagem de um vídeo do YouTube antes do gate 4: título final, descrição tirada da
  narração, hashtags, tags, links e a lista do Studio em publicacao.md. Use depois da prévia
  renderizada e antes de levar o gate 4 ao dono; não escreve post.json, não agenda nem aprova.
---

# Metadados do YouTube: da narração à lista do Studio

Leia [CLAUDE.md](../../../CLAUDE.md) e, em `data/episodes/<id>/`:

- `pauta.md`, seção "Promessa e título" (método em
  [promessa-e-titulo.md](../../../.claude/skills/pauta/promessa-e-titulo.md));
- `scenes.json`: narração, `objective`, `funnel`;
- `episode.json`: `title`, `language`, `format`, `music` e, por cena, `start_ms` e `audio`. O provedor da voz está
  no nome do WAV (`S01-azure_speech-….wav`);
- `credits.txt` ou `comentario-fixado.txt`, e `assets/*.json` (licença `Generated` = imagem gerada).

Escreva só `description.txt` e as seções "Pacote" e "No YouTube Studio" do `publicacao.md`. A seção "Pontos para
o dono no gate 4" é da skill `miniatura`. O `post.json` fica com a sessão principal, que tem os ids do upload, e
copia daqui o título, a descrição e as tags.

O hash do gate 4 cobre o render, `episode.json`, `captions.srt` e `legenda-post.txt`, e não cobre
`description.txt`. Com o gate 4 já decidido (`.venv/bin/vp status <id>`), grave `description-proposta.txt` e
leve ao dono como decisão nova: o `vp status` não vai avisar da troca.

## 1. Título final

Parta das opções de título da pauta e confira cada uma contra a narração pronta: cada palavra precisa de uma cena
que a entregue (promessa-e-titulo.md, "Promessa entregável"). Recomende um; com teste A/B de título, mais um ou
dois, cada um marcado com a pergunta (resultado, confiança, tempo, esforço) que ele puxa.

Pronto quando cada título proposto tem a cena que o entrega.

## 2. Descrição (`description.txt`)

Na ordem que o canal já usa (exemplo: `data/episodes/idade-media-ter-20-anos/description.txt`):

1. **Abertura:** as duas primeiras linhas, as que aparecem antes de "mostrar mais", trazem a palavra-chave e a
   promessa, com palavras da própria narração.
2. **Conteúdo:** um parágrafo do que o vídeo de fato percorre, só com o que a narração diz. Opinião vai como
   opinião (CLAUDE.md §5, Objetivo e Opinião).
3. **Avisos que o episódio pede:** CVV (188) quando a narração toca sofrimento ou saúde mental; reconstrução
   ilustrada na ficção histórica (ADR 055); voz sintética do Azure (ADR 058); voz clonada e imagem gerada por IA.
4. **Capítulos:** primeira marca em 0:00, tempos tirados do `start_ms` real das cenas, títulos curtos dos blocos.
5. **Comentários e chamada:** a pergunta dos comentários e a chamada do funil, as mesmas da última cena (ADR 026).
6. **Links:** cada link citado na narração, ao menos um link interno do canal (vídeo ou playlist, da pauta, em
   "Links internos") e os livros pelo `.venv/bin/vp export livros <id>`. Sem URL interna na pauta, peça ao dono.
7. **Créditos:** "Créditos no comentário fixado."
8. **Hashtags:** de 3 a 5 no fim, ligadas ao título e ao tema.

**Short cortado de um longo:** a descrição abre com a frase e o link do longo de CLAUDE.md §4, sem capítulos, com
um pedido só (ADR 028).

Pronto quando cada frase da descrição aponta para uma cena ou para um aviso obrigatório, e cada URL veio da
narração, da pauta ou do dono.

## 3. Tags

Pelo menos 3: o assunto, o pensador, a obra ou o período, a palavra-chave da busca e as variações que o público
digita. Elas vão no `publicacao.md`, para o `settings.tags` do `post.json`.

## 4. `publicacao.md`, seção "Pacote"

Uma tabela com: canal, formato (longo ou Short), data (decisão do dono), título recomendado e alternativas de
A/B, vídeo (`renders/final.mp4`), descrição, comentário fixado, miniaturas e plano do teste A/B, privacidade
do envio (privado ou não listado), "não é para crianças", plataformas, conteúdo alterado ou sintético (com a
regra do passo 5), tags, hashtags, **links citados na narração** e **links internos**. A dúvida cega confere a
legenda do post contra essas duas listas.

Nome do arquivo para envio manual pelo Studio: o título sem acento, em minúsculas e com hífens. Pelo Postiz a
mídia chega com nome próprio dele, e `renders/final.mp4` continua sendo o arquivo do gate 4.

## 5. `publicacao.md`, seção "No YouTube Studio"

A lista para o dono, com o valor deste episódio em cada item ou "decisão do dono":

1. **Playlist:** adicionar a uma playlist do canal (qual).
2. **Público:** "Não, não é conteúdo para crianças".
3. **Conteúdo alterado ou sintético**, pelo que o episódio usa de fato:
   - voz sintética do Azure: aviso na descrição e no Studio (ADR 058);
   - imagem gerada realista de fato histórico: marcar (CLAUDE.md §2.4);
   - voz clonada ou outra imagem gerada: marcar, como pede o [docs/postiz.md](../../../docs/postiz.md), salvo
     decisão contrária do dono para este episódio (o `death-note-fins-meios` dispensou a marcação da voz clonada);
   - nos demais casos, leve ao dono a regra do YouTube com o que o episódio usa.
4. **Capítulos e locais automáticos:** desligados; os capítulos da descrição valem.
5. **Tela final:** um só elemento de vídeo, em "Melhor para o espectador".
6. **Legendas:** enviar `captions.srt` no idioma do episódio ("Com sincronização"); depois adicionar as traduções
   automáticas em inglês, espanhol e hindi (no episódio em inglês: português, espanhol e hindi).
7. **Teste A/B:** Miniatura → "Testar e comparar" com `miniatura-final.jpg` e as `miniatura-final-ab-*.jpg`; título,
   se o dono escolheu testar.
8. **Visibilidade:** o envio sai privado ou não listado. Tornar público depois de pelo menos 1 hora, com o
   processamento em HD e as verificações de direitos autorais e anúncios conferidos. Decisão do dono.
9. **Comentário fixado, idioma e categoria:** publicar e fixar `comentario-fixado.txt`; idioma e categoria do canal.

Pronto quando os nove itens têm o valor do episódio ou "decisão do dono".

## Fechamento

Entregue ao dono, junto do pedido do gate 4: o título recomendado, os caminhos de `description.txt` e
`publicacao.md`, e as decisões dele agrupadas (data, privacidade, conteúdo sintético, teste A/B, URL interna
que faltar). Os gates e o agendamento são do dono (CLAUDE.md §2.5 e §2.8); depois do "pode", o fluxo segue em
`vp postiz pacote` ([docs/postiz.md](../../../docs/postiz.md)).
