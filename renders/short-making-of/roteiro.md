# Short "um vídeo fazendo um vídeo": roteiro (2026-10-25)

Vertical 1080×1920, 30 fps, por volta de 50 s. Mostra o teaser do motion-kit (`renders/teaser-motion-kit/
teaser-D-pt-voz-v2.mp4`) sendo montado: a frase, o JSON, a conferência, o render, a voz, e o que mais a biblioteca
desenha. Promessa: **o Claude montou este vídeo com a minha biblioteca**. Vale para o JSON e para o TSX, porque o
Short mostra o que de fato acontece. Molde: o dos vídeos de "motion graphics com Claude" da amostra do vidIQ de
2026-10-25 (resultado na tela, a entrada em segundos, o agente trabalhando, o resultado de novo, o link).

Produção em `data/episodes/short-making-of/` (narração, voz, `content.json` das batidas, `making-of.json` com o
envelope da boca, renders), fora do Git. Composição em TSX no kit: `examples/divulgacao/MakingOfDemo.tsx`
(`MakingOf` no Studio), com o material em `examples/public/divulgacao/` (fora do Git). Fluxo: skill `shorts-tec`.

## Batidas e narração (voz clonada do dono, `chatterbox_modal`)

| # | Batida | Tela | Fala | Mínimo |
| --- | --- | --- | --- | --- |
| 1 | `capa` | Em cima, o cartão "Este vídeo inteiro saiu de **uma frase**." (capa do Short, legível no quadro 0); embaixo, o teaser tocando a partir de 3 s, mudo | Este vídeo inteiro saiu de uma frase. | 3,5 s |
| 2 | `frase` | Em cima, **gravação de tela 1** (Claude Code: a frase e o agente escrevendo o `content.json`); embaixo, o `content.json` do teaser aparecendo linha a linha; o dono na janela, canto de baixo à direita | Eu escrevi a frase no Claude Code. Ele escreveu o JSON: seis cenas, com os números do meu repositório. | 8,0 s |
| 3 | `confere` | Em cima, **gravação de tela 2** (`inspect` e `review`); embaixo, os seis quadros de revisão do teaser entrando um a um | A ferramenta confere o JSON antes de renderizar. Avisa quando uma cena fica curta demais para ler, e gera um quadro de revisão de cada cena. | 10,5 s |
| 4 | `render` | Em cima, **gravação de tela 3** (`render`, `voz`, `tempos`, `juntar`); embaixo, o teaser pronto tocando, mudo | Depois, o render. A minha voz entra por cima, clonada numa GPU, e a boca da janela segue cada fala. | 8,5 s |
| 5 | `biblioteca` | Montagem dos quadros de documentação do kit (renders reais de `docs/stills`): mapa, mapa com zoom, grafo, foto de arquivo, documento, linha do tempo, tela dividida, janela flutuante, apresentador, a 0,7 s cada; depois 12 estilos a 0,27 s | E a biblioteca desenha mais do que o JSON pede hoje: mapa, grafo, foto de arquivo, documento, tela dividida, janela flutuante. Quarenta e sete estilos prontos. | 10,0 s |
| 6 | `fecho` | Em cima, o dono grande, falando; embaixo, o cartão final "motion-kit · link na descrição" | Código aberto. O link está na descrição. | 4,0 s |

A duração de cada batida é o máximo entre o mínimo e a fala mais 0,3 s (`shorts_tec.py tempos`); a boca do dono
segue o envelope real de cada fala (`shorts_tec.py boca`), na janela flutuante das batidas 2 a 5 e no painel da 6.

## O que é real e o que é espaço marcado

Real: o teaser inteiro, o `content.json`, os seis quadros do `review` (run `1792940636467-77e54616`), os quadros de
documentação, a voz. **Espaço marcado:** as três gravações de tela, desenhadas como um painel tracejado
"GRAVAÇÃO DE TELA" até o dono gravar. Elas precisam ser reais, não encenadas: é a promessa do vídeo.

## Gravações de tela, para o dono (Windows, terminal limpo, OBS ou a gravação do próprio Windows)

Gravar em 16:9, 1920×1080 ou maior; a composição recorta para o painel de cima. Três clipes, acelerados depois
se passarem do tempo da batida (8, 10 e 8 s):

1. `tela-1.mp4`, Claude Code: a frase "Descrevi seis cenas em uma frase…" no prompt e o agente escrevendo
   `content.json` (pode ser a sessão que escreveu o `content.pt.janela.json`, refeita ao vivo).
2. `tela-2.mp4`, no auto-play com `T=data/episodes/teaser-motion-kit`:
   `MOTION_VIDEO_PROJECT=$T MOTION_VIDEO_PUBLIC=$T/public node ~/projetos/motion-kit/scripts/video.mjs inspect content.pt.janela.voz.json`
   e o mesmo com `review`. O `inspect` mostra os avisos `HOST_WINDOW_TIGHT`; o `review` escreve os quadros.
3. `tela-3.mp4`: o `render` do mesmo JSON e, no auto-play, `shorts_tec.py voz`, `tempos` e `juntar` do teaser.

Depois, copiar os três para `~/projetos/motion-kit/examples/public/divulgacao/` e escrever os nomes em
`recordings` do `making-of.json` (`{"frase": "tela-1.mp4", "confere": "tela-2.mp4", "render": "tela-3.mp4"}`),
renderizar de novo (`npx remotion render examples/index.ts MakingOf … --public-dir examples/public`) e juntar a voz.

## Fatos usados

- "seis cenas, com os números do meu repositório": o `content.pt.janela.json` tem seis cenas; os números vêm do
  `git log` do kit (teaser, doc `docs/divulgacao/teaser-15s-2026-10-25.md` no kit).
- "avisa quando uma cena fica curta demais para ler" e "um quadro de revisão de cada cena": `SCENE_TOO_SHORT_TO_READ`
  e os quadros `start`, `read` e `end` do `review` (`packages/motion-video/recipes/explainer.md`).
- "clonada numa GPU" e "a boca da janela segue cada fala": ADR 024 do auto-play (Chatterbox numa T4 do Modal) e
  `host.speaking` por trecho (motion-video 0.3.1, MR !36).
- "mapa, grafo, foto de arquivo, documento, tela dividida, janela flutuante": `GeoMap`, `ExpandingNetwork`,
  `ArchivalPhoto`, `DocumentPage`, `SplitScreen`, `FloatingWindow` (`packages/motion-kit/src/COMPONENTS.md`).
- "quarenta e sete estilos prontos": `packages/motion-kit/src/styles/catalog.ts`.
- "código aberto": `LICENSE` (MIT); o link depende de abrir o repositório ou publicar no npm.

## Resultado (2026-10-25)

`renders/short-making-of/making-of-pt-voz.mp4`: 45,1 s, H.264 1080×1920, AAC 48 kHz, −15,0 LUFS. Batidas: capa 3,5 s,
frase 8,0, confere 10,5, render 8,5, biblioteca 10,6 (esticada pela fala), fecho 4,0; 40,3 s de fala. Composição
`MakingOf` do kit na MR !37 (`feat/divulgacao-making-of`); render silencioso e voz juntados pelo
`shorts_tec.py` (`tempos`, `boca`, `juntar`). Segundo render corrigiu a batida 4: o teaser encostado à esquerda e a
janela do dono com 27% da largura, para a janela não cobrir o texto do teaser. Quadros conferidos nas seis
batidas (`data/episodes/short-making-of/out/q-*.png`).

## v3 (2026-10-25): os quatro ajustes da validação com o vidIQ, aprovados pelo dono

Sem mudar a narração nem gerar voz de novo (`validacao-vidiq-2026-10-25.md`):

1. **Dois cortes por batida e passos numerados** no painel de cima: #1 a frase (a frase sendo digitada embaixo),
   #2 o JSON (as linhas do `content.json`), #3 inspect (os três avisos reais, um a um), #4 review (a grade dos
   seis quadros), #5 render (o teaser mudo), #6 a voz (barras com o envelope real da narração). Os cortes caem
   na virada de cada fala: 3,5 s, 6,0 s e 3,0 s dentro das batidas 2, 3 e 4.
2. **Cartões com os números reais do teaser:** "6 cenas · 19,6 s", "3 avisos", "564 quadros · 1080×1920",
   "8 falas · GPU T4", "boca presa a cada fala", "−15,3 LUFS", "fala 0,08 s depois do corte".
3. **O dono desde o quadro 0:** a janela já está pousada na capa, ao lado do teaser (encostado à esquerda, a 80%
   da altura do painel).
4. **O resultado com som:** batida nova `resultado`, 6 s do teaser com a própria voz, entre a montagem e o
   fecho, sem a janela (o teaser já tem a dele). O `juntar` passou a misturar o áudio que o render traz.

A frase da batida 1 (`prompt` no `making-of.json`) é a que o dono vai digitar na gravação real; trocar ali e
renderizar de novo se a frase gravada for outra. Duração prevista: 51 s.

## Pendências antes de publicar

A escuta e a leitura do dono; as três gravações de tela; o link público; o gerador da pele do apresentador
(`origem.json` em `needs_review`); a divulgação de IA na descrição e no Studio (voz clonada, desenho a partir de
fotos). Os posts seguem o modelo de `renders/teaser-motion-kit/posts/`.
