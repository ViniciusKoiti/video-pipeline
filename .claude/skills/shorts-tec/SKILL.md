---
name: shorts-tec
description: |
  Monte Shorts técnicos sobre conceitos de programação ou ferramentas do dono com explicação animada
  e impacto visual em System Design: pauta → plano de animação → narração → JSON do motion-video →
  revisão → voz clonada → render → posts. Use para Shorts de Java, demonstrações técnicas e teasers
  de projetos do dono. Episódio longo do Cena e Conceito é `roteiro-explicativo`.
argument-hint: "<pasta do short>"
---

# Shorts técnicos: mecanismo, fluxo animado e System Design

O Short explica um conceito com uma demonstração própria ou mostra uma ferramenta que o dono construiu.
Conceitos de programação têm linguagem explícita e uma aplicação concreta que revela o impacto em System Design.
Para ferramentas do dono, a frase é "eu construí": o conteúdo e os números vêm do próprio repositório.
O primeiro caso é o teaser do motion-kit
(`data/episodes/teaser-motion-kit/`, posts em `renders/teaser-motion-kit/`, doc
`docs/divulgacao/teaser-15s-2026-10-25.md` no repositório do kit): copie a forma dele.

## Entrada

- Em todo vídeo técnico, explicar o impacto em System Design da aplicação e representá-lo
  com nossas animações: fluxo entre componentes, mudança de estado e benefício/limite sustentados.
  Ler os critérios em `renders/serie-conceitos/direcao-editorial.md` antes de planejar as cenas.
  Preencher o quadro obrigatório por tema na pauta e conferir antes de voz/render e depois da montagem;
  registrar lacunas e completar o conteúdo antes de avançar ou apresentá-lo como pronto.
- Para a série de conceitos, ler `renders/serie-conceitos/direcao-editorial.md` e `fila.md`:
  prioridade Java, explicação do mecanismo e plano de animação antes de gerar voz/render.
  Esses critérios da série não mudam a duração de um teaser de ferramenta pedido pelo dono.
- A pasta do short (o "projeto" do `motion-video`) em `data/episodes/<id>/`, fora do Git: JSON, narração,
  voz, a pele do dono e os renders. O que se publica vai para `renders/<id>/`, versionável.
- O que o dono decidiu: o canal e o perfil, os idiomas, se ele aparece na janela e a duração da pauta.
- Teasers usam os 15 a 20 segundos combinados; conceitos seguem a duração da pauta, com tempo para explicar
  o mecanismo e seu impacto. A presença do dono na janela é opcional segundo o formato aprovado.
- O código do exemplo ou repositório da ferramenta e as fontes primárias do mecanismo.
  Cada número precisa de origem registrada; tempos e resultados exigem medição própria.

## O que você escreve, na pasta do short

- `narracao.<idioma>.json`: uma fala por cena do JSON e as falas dos planos fora dele (formato no cabeçalho de
  `app/commands/short.py`).
- `content.<idioma>.json`: o vídeo por JSON do `motion-video` (tipos de cena e campos na receita
  `packages/motion-video/recipes/explainer.md` do kit; a janela do dono é o campo `host`).
- `plano-animacao.md`: trechos da fala, estados inicial/final, blocos, conexões, transições e fontes;
  incluir a sequência de impacto na aplicação e o quadro de controle da direção editorial.
- `posts/`: os rascunhos do Postiz e o `README.md` com os textos, a hipótese e a lista do que falta.
- O doc do short, com a origem de cada número, as variantes e o que cada `review` mostrou.

## Método

1. **A promessa em uma frase e a capa.** A abertura mostra a situação em 3 ou 4 quadros de formas geométricas e
   ícones nos primeiros 3 a 5 segundos, com a pergunta ou promessa escrita no último quadro (decisão do dono,
   2026-11-07; ver "Abertura em quadros" em `renders/serie-conceitos/direcao-editorial.md`). O primeiro quadro é a
   capa do Short. Sem personagem desenhado à mão. Use `hook` apenas no quadro de pergunta, com `cover: true`.
   A linguagem explícita nos conceitos de programação continua valendo.
   Quando houver números, cada um tem origem registrada no doc do short; não criar uma medição para a capa.
2. **Plano de animação e narração por cena.** Antes de gerar a voz, definir no `plano-animacao.md` o fluxo
   entre componentes, o elemento ativo em cada etapa e a mudança de estado que explica o mecanismo.
   A sequência deve mostrar também a decisão de System Design, seu benefício e seu limite na aplicação.
   Referência de forma: `renders/short-concorrencia/fluxo/plano-animacao.md` e
   `renders/short-concorrencia/final.pt.fluxo.mp4`; os fatos e números desse exemplo são de C.
   Uma linha curta de narração por cena, na ordem das cenas, mais as falas dos planos fora do JSON
   (gravação de tela, troca de estilos) com `scene: null`. Entrega da ADR 022: `hook` na abertura, `turn` na
   virada, `calm` para acompanhar contas/fluxos, `neutral` na explicação e `invite` no fecho.
   Pela ADR 053, idioma + `delivery` escolhem a gravação em `[chatterbox.references]`; não inserir caminhos
   pessoais no roteiro. Planejar a intenção e as pausas junto dos estados da animação.
   **Música planejada junto do plano de animação (obrigatório; pedido do dono em 2026-11-05).** Todo Short de
   conceito tem a trilha decidida **antes da voz**, numa seção "Música" do `plano-animacao.md` (e, se o vídeo
   leva faixa, um `music.json` no formato da skill `trilha`, na pasta do short). A seção responde, por cena:
   fundo, silêncio ou transição; faixa do `data/music/catalog.json` (nunca fora dele; `vocals: false`); nível
   (`low` por padrão); entrada e saída ancoradas em cena + trecho literal da fala; fade; e o motivo (`why`).
   O clima segue a `delivery`: `hook` entra já no primeiro quadro; `calm`/fluxo animado = fundo baixo, sem
   competir com a leitura dos blocos; `turn` = troca de faixa ou silêncio curto; a frase que fecha a lição e o
   resultado medido ficam sem música ou com o fundo já saindo; `invite` pode trazer a faixa da abertura de volta.
   Faixa com duração menor que o vídeo não serve (o catálogo não tem loop); preferir uma só faixa por Short.
   Efeito sonoro (ADR 035) e música não disputam o mesmo instante: o SFX do corte vence, a música abaixa ou já
   saiu. Sem música só por decisão escrita na pauta ou no plano, com o motivo (ex.: o Short é só demonstração
   em silêncio); "sem música" por esquecimento é lacuna do controle editorial.
   **Direitos:** as faixas da YouTube Audio Library só valem no YouTube (`data/benchmarks/termos-musica.md`).
   As saídas YouTube (pt, en) levam a faixa; o Reel do Instagram sai sem ela, ou com faixa de licença
   registrada para esse uso. A descrição do YouTube leva o crédito (`attribution_text` quando a faixa é CC).
   A rotina nunca baixa faixa nem aprova ativo: `vp music usar` copia a faixa para o episódio e o gate 3 da
   faixa (`vp approve ... --step assets --asset <faixa>`) é do dono, que também ouve na prévia.
   **Lacuna atual:** `vp short juntar` mistura voz e SFX, não música (ADR 035; a ADR 030 só cobre o `vp render`
   do longo). Enquanto não houver mistura de música no Short, o plano é entregue e a mistura fica registrada como
   pendência (`música planejada, mistura pendente`); não declarar um vídeo "com música" sem ela, e não inventar
   um `ffmpeg` avulso que o dono não pediu.
   A voz clonada fala a ~2,5 palavras por segundo: uma linha de 8 palavras ocupa
   3 s, e a cena precisa ter esse tempo depois de pronta para ler. Passe a `humanizer-narracao` antes de gravar.
   Pronto quando as afirmações se apoiam no código, nas fontes registradas ou na medição. Com medição própria (ADR 034), escreva o
   `medicao.json` (cada número dito ou mostrado, o trecho literal do `resultado.txt`, os medidos e a tolerância
   do arredondamento; nome e contagem levam só a `nota`) e rode `vp medicao <id>` até sair limpo: o gate 4 exige.
3. **O JSON do motion-video.** `safeArea: "shorts"`, `footer` com a origem dos dados, `host` com a pele de
   sprites do dono (dado pessoal: a pasta fica no `.gitignore` do repositório onde o short mora) e `speaking`
   só nas cenas que a narração cobre. Pronto quando `inspect` sai válido e cada aviso `HOST_WINDOW_TIGHT` tem
   uma decisão escrita: `host: false` na cena, janela menor, ou aceitar o encolhimento.
   Para mostrar um fluxo, usar blocos conectados, setas e valores/estados que mudam junto da explicação.
   O tipo `animation` aceita Lottie original: conferir o contrato do kit, registrar licença/hash e
   ajustar os keyframes às falas. O gerador `renders/short-concorrencia/fluxo/gerar_animacoes.py` é referência;
   adaptar o desenho e a semântica ao tema. Uma sequência de cartões de texto não substitui o fluxo pedido.
4. **Review.** `review` do JSON e os quadros de leitura de todas as cenas abertos. Pronto quando cada cena foi
   conferida contra três defeitos: animação cortada antes do fim, janela sobre o conteúdo e texto sobre o rodapé.
   Nos fluxos, abrir também antes/durante/depois das transições: conferir valor transportado, elemento ativo,
   espera, conclusão e impacto no desenho da aplicação. Registrar o resultado do controle obrigatório.
   Conferir números e textos internos de Lottie visualmente: eles não entram na leitura do `vp medicao`.
5. **A voz.** `vp short voz <pasta> narracao.<idioma>.json` (`--voz NOME` troca a voz) gera as falas com a voz do vídeo final (a
   clonada do dono no Modal, ADR 024). É serviço externo: só com o pedido do dono na sessão, e a sonda
   `cpu_probe()` antes. Pronto quando o `narracao.<idioma>.voz.json` lista um WAV por linha e o dono ouviu.
   Conferir também `reference.file`, `reference.sha256` e `reference.remote_name` por fala; o manifest
   registra a identidade de referência/entrega inclusive no reuso do cache. Gravação ausente ou divergente
   no Modal deixa a cena pendente; não trocar por outro tom. O cadastro e a sincronização das referências
   são descritos em `docs/guia-gravacao-referencias-voz.md`; a rotina não envia novas gravações pessoais.
   Com o banco ativo, `voz` nivela cada fala em uma cópia `voice/leveled/` antes de `tempos` (ADR 054).
   Conferir `level.input_lufs`, `level.output_lufs` e `level.true_peak_dbtp` no registro: alvo −16 LUFS,
   teto −1,5 dBTP. A montagem usa o `wav` do registro; não voltar ao bruto por nome de arquivo.
   Falha de nivelamento deixa a cena pendente; retomar reaproveita a síntese bruta já pronta.
6. **Tempos, render e junção.** `vp short tempos <pasta> content.<idioma>.json narracao.<idioma>.json` estica as cenas até a fala caber; o `render` do kit
   sai do `content.<idioma>.voz.json`; `vp short juntar <pasta> <mudo.mp4> content.<idioma>.voz.json narracao.<idioma>.json --saida <mp4>` põe cada fala no começo da cena. Pronto quando o
   `juntar` imprime o volume dentro do alvo e nenhuma fala passa do fim da cena.
   **Efeitos sonoros (ADR 035, opcional):** um `sfx.<idioma>.json` com um som do SFX Kit (`data/sfx/kit/`,
   CC0) por momento: no corte de cada cena e nas palavras que pesam (número que cai, item que entra, pedido
   final), ancorado como os planos (`scene` + `text` ou `offset_s`). Escolha pela tabela "On screen" do
   `GUIDE.md` do kit; nunca os sons que o kit marca "On top of speech" sobre a fala. `vp short sfx` confere
   e lista onde cada som cai; `juntar --sfx` mistura numa saída nova, sem tocar no MP4 carimbado. O dono ouve.
7. **Os posts.** Rascunhos no formato do Postiz para cada canal e idioma (`docs/postiz.md`), com data, mídia e
   link como lacunas explícitas até existir o que preencher, e a hipótese a medir aos 7 e 28 dias (CLAUDE.md
   §4). Pronto quando o `README.md` da pasta lista o que falta antes do `pacote`.
8. **Os gates são do dono, e ficam no auto-play.** `vp short gate <mp4> <post.json> --episodio <id>-<idioma>`
   monta a pasta de gate em `data/episodes/` (o render e `legenda-post.txt`); o dono assiste e carimba com
   `vp approve <id>-<idioma> --step preview`, que grava no `review.json` dele com o hash do MP4 e da legenda.
   O `vp postiz pacote --episode <id>-<idioma>` lê essa aprovação, e a dúvida cega a encontra. Pronto quando
   `vp status` mostra o gate 4 aprovado e válido para o MP4 que vai ser enviado. O agendamento segue a cadeia da
   ADR 025 (`pacote`, dúvida cega, `schedule` com a confirmação dele). Logo depois do `schedule`, o
   `metrics.json` de cada saída nasce de `vp metricas iniciar <id>-<idioma> --platform youtube --format short
   --hypothesis "..."`, que puxa data, canal e post do registro; nunca escrito à mão (fora do contrato ele sai
   como INVÁLIDO no `vp metricas pendentes` e a janela de 7 dias passa em branco).

## Regras

- **Nenhum link prometido sem link público.** "Código aberto" e "link na descrição" só entram na fala e no
  texto quando o repositório estiver aberto ou o pacote publicado; até lá, `[LINK]` nos rascunhos.
- **Divulgação de IA:** voz clonada e apresentador desenhado a partir de fotos vão ditos na descrição, e o
  dono marca "conteúdo alterado ou sintético" no Studio depois de publicar.
- **A pele do dono** só vai a vídeo publicado com `origem.json` fora de `needs_review` (gerador e licença
  registrados, gate 3).
- **Um render por vez**, e nada de render ou chamada de voz que o dono não pediu na sessão.

## Fora da v1

Legenda queimada (o `motion-video` não tem campo de legenda; a `WordCaption` é do template do auto-play) e
a **mistura** da música no `juntar` (efeitos sonoros entraram na ADR 035; o **plano** da música já é
obrigatório, no passo 2). A voz clonada em inglês foi aprovada
pelo dono na versão de concorrência em C; referências novas ainda exigem escuta da prévia gerada.
