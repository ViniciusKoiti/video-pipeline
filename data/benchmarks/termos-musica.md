# Termos de música de fundo — YouTube Audio Library

Consulta em 2026-10-17 da página oficial [Use music and sound effects from the Audio Library](https://support.google.com/youtube/answer/3376882?hl=en).
A página não traz data de atualização (só "©2026 Google"). Este arquivo é a base da ADR 030 e da emenda de licença
de música na ADR 007.

## O que a página diz

- **Acesso:** no YouTube Studio, menu à esquerda, **Audio library**, ou direto em `youtube.com/audiolibrary`. É
  possível buscar e filtrar por título, gênero, clima (*mood*), artista, atribuição e duração.
- **Uso no YouTube:** "Music and sound effects from the YouTube Audio Library are copyright-safe."
- **Monetização:** quem está no YPP pode monetizar vídeos com essas faixas. As faixas baixadas "won't be claimed by a
  rights holder through the Content ID system".
- **Creative Commons:** o crédito ao artista na descrição do vídeo é obrigatório. O texto sai do ícone CC na coluna
  "License type", botão Copy. O filtro "Attribution not required" mostra as faixas que dispensam crédito.
- **Fora do YouTube:** a página não diz que licença vale e afirma que o YouTube "can't give legal guidance,
  including guidance on issues with music that can occur off the platform".
- **Outras fontes:** "Only music and sound effects from the Audio Library are known to YouTube to be
  copyright-safe."

## Como o projeto usa (proposta da ADR 030)

- **Só em vídeo publicado no YouTube.** Corte para Reels, TikTok e afins sai sem essas faixas, porque o uso fora da
  plataforma não está coberto.
- **Preferir o filtro "Attribution not required".** Faixa CC entra com `author` e `attribution_text`, como as outras
  CC-BY.
- **Origem:** o dono baixa as faixas à mão pelo Studio, porque não há API. Cada faixa entra no catálogo com a página
  de origem, o tipo de licença mostrado na coluna "License type", o `sha256` do arquivo e a data do download.
