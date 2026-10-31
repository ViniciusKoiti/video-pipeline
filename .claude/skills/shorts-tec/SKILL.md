---
name: shorts-tec
description: |
  Short de tecnologia (até uns 20 s) sobre uma ferramenta do dono, montado por JSON no motion-video do kit,
  com o dono numa janela flutuante e a voz clonada dele: narração por cena → JSON → inspect e review → voz →
  tempos → render → junção → posts. Use quando o dono pedir um Short, teaser ou demo de um projeto técnico
  dele. Episódio do Cena e Conceito é `roteiro-explicativo`; Reel de pauta é `pauta`.
argument-hint: "<pasta do short>"
---

# Shorts tec: uma frase, um JSON, a voz do dono

O Short mostra uma coisa que o dono **construiu**, com os números do próprio repositório dela na tela e o dono
falando numa janela no canto. A frase é "eu construí", nunca "eu achei": é conteúdo original, o oposto do que a
política de conteúdo não original do YouTube derruba (CLAUDE.md §12). O primeiro caso é o teaser do motion-kit
(`data/episodes/teaser-motion-kit/`, posts em `renders/teaser-motion-kit/`, doc
`docs/divulgacao/teaser-15s-2026-10-25.md` no repositório do kit): copie a forma dele.

## Entrada

- A pasta do short (o "projeto" do `motion-video`) em `data/episodes/<id>/`, fora do Git: JSON, narração,
  voz, a pele do dono e os renders. O que se publica vai para `renders/<id>/`, versionável.
- O que o dono decidiu: o canal e o perfil, os idiomas, se ele aparece na janela, e os 15 a 20 segundos.
- O repositório da ferramenta, de onde saem todos os números (`git log`, catálogo, testes). Um número sem
  origem no repositório fica fora da tela.

## O que você escreve, na pasta do short

- `narracao.<idioma>.json`: uma fala por cena do JSON e as falas dos planos fora dele (formato no cabeçalho de
  `scripts/provisorio/shorts_tec.py`).
- `content.<idioma>.json`: o vídeo por JSON do `motion-video` (tipos de cena e campos na receita
  `packages/motion-video/recipes/explainer.md` do kit; a janela do dono é o campo `host`).
- `posts/`: os rascunhos do Postiz e o `README.md` com os textos, a hipótese e a lista do que falta.
- O doc do short, com a origem de cada número, as variantes e o que cada `review` mostrou.

## Método

1. **A promessa em uma frase e a capa.** O cartão de abertura (`hook`, `cover: true`) é a capa do Short e diz a
   promessa com números inteiros ("1 frase. 6 cenas. 47 estilos."). Pronto quando cada número da capa e das cenas
   tem a linha de origem no doc do short.
2. **A narração por cena.** Uma linha curta por cena, na ordem das cenas, mais as falas dos planos fora do JSON
   (gravação de tela, troca de estilos) com `scene: null`. Entrega da ADR 022: `hook` na abertura, `turn` na
   virada, `invite` no fecho. A voz clonada fala a ~2,5 palavras por segundo: uma linha de 8 palavras ocupa
   3 s, e a cena precisa ter esse tempo depois de pronta para ler. Passe a `humanizer-narracao` antes de gravar.
   Pronto quando nenhuma linha afirma o que o repositório não mostra.
3. **O JSON do motion-video.** `safeArea: "shorts"`, `footer` com a origem dos dados, `host` com a pele de
   sprites do dono (dado pessoal: a pasta fica no `.gitignore` do repositório onde o short mora) e `speaking`
   só nas cenas que a narração cobre. Pronto quando `inspect` sai válido e cada aviso `HOST_WINDOW_TIGHT` tem
   uma decisão escrita: `host: false` na cena, janela menor, ou aceitar o encolhimento.
4. **Review.** `review` do JSON e os quadros de leitura de todas as cenas abertos. Pronto quando cada cena foi
   conferida contra três defeitos: animação cortada antes do fim, janela sobre o conteúdo e texto sobre o rodapé.
5. **A voz.** `shorts_tec.py voz <pasta> narracao.<idioma>.json` gera as falas com a voz do vídeo final (a
   clonada do dono no Modal, ADR 024). É serviço externo: só com o pedido do dono na sessão, e a sonda
   `cpu_probe()` antes. Pronto quando o `narracao.<idioma>.voz.json` lista um WAV por linha e o dono ouviu.
6. **Tempos, render e junção.** `shorts_tec.py tempos` estica as cenas até a fala caber; o `render` do kit
   sai do `content.<idioma>.voz.json`; `shorts_tec.py juntar` põe cada fala no começo da cena. Pronto quando o
   `juntar` imprime o volume dentro do alvo e nenhuma fala passa do fim da cena.
   **Efeitos sonoros (ADR 035, opcional):** um `sfx.<idioma>.json` com um som do SFX Kit (`data/sfx/kit/`,
   CC0) por momento: no corte de cada cena e nas palavras que pesam (número que cai, item que entra, pedido
   final), ancorado como os planos (`scene` + `text` ou `offset_s`). Escolha pela tabela "On screen" do
   `GUIDE.md` do kit; nunca os sons que o kit marca "On top of speech" sobre a fala. `shorts_tec.py sfx` confere
   e lista onde cada som cai; `juntar --sfx=` mistura numa saída nova, sem tocar no MP4 carimbado. O dono ouve.
7. **Os posts.** Rascunhos no formato do Postiz para cada canal e idioma (`docs/postiz.md`), com data, mídia e
   link como lacunas explícitas até existir o que preencher, e a hipótese a medir aos 7 e 28 dias (CLAUDE.md
   §4). Pronto quando o `README.md` da pasta lista o que falta antes do `pacote`.
8. **Os gates são do dono, e ficam no auto-play.** `shorts_tec.py gate <mp4> <post.json> --episodio=<id>-<idioma>`
   monta a pasta de gate em `data/episodes/` (o render e `legenda-post.txt`); o dono assiste e carimba com
   `vp approve <id>-<idioma> --step preview`, que grava no `review.json` dele com o hash do MP4 e da legenda.
   O `vp postiz pacote --episode <id>-<idioma>` lê essa aprovação, e a dúvida cega a encontra. Pronto quando
   `vp status` mostra o gate 4 aprovado e válido para o MP4 que vai ser enviado. O agendamento segue a cadeia da
   ADR 025 (`pacote`, dúvida cega, `schedule` com a confirmação dele).

## Regras

- **Nenhum link prometido sem link público.** "Código aberto" e "link na descrição" só entram na fala e no
  texto quando o repositório estiver aberto ou o pacote publicado; até lá, `[LINK]` nos rascunhos.
- **Divulgação de IA:** voz clonada e apresentador desenhado a partir de fotos vão ditos na descrição, e o
  dono marca "conteúdo alterado ou sintético" no Studio depois de publicar.
- **A pele do dono** só vai a vídeo publicado com `origem.json` fora de `needs_review` (gerador e licença
  registrados, gate 3).
- **Um render por vez**, e nada de render ou chamada de voz que o dono não pediu na sessão.

## Fora da v1

Legenda queimada (o `motion-video` não tem campo de legenda; a `WordCaption` é do template do auto-play),
trilha (efeitos sonoros entraram na ADR 035; música ainda não), e a voz em inglês: a decisão entre a voz clonada em inglês e a dublagem automática do YouTube é do
dono, numa escuta cega.
