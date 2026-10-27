# Posts do teaser do motion-kit (pt e en), escritos em 2026-10-25

Produção do teaser (JSON do motion-video, narração, voz e renders) em `data/episodes/teaser-motion-kit/`, fora
do Git; o que se publica fica aqui em `renders/teaser-motion-kit/`: o MP4 a enviar (`teaser-D-pt-voz-v2.mp4`, 19,6 s,
voz clonada, boca presa à fala, sem os planos 2 e 8; a v1 fica como registro) e estes rascunhos. Movido do repositório do kit em 2026-10-25 para a cadeia do
`vp postiz` (ADR 025); o doc do teaser continua no kit, em `docs/divulgacao/teaser-15s-2026-10-25.md`.

Quatro rascunhos no formato nativo do Postiz, prontos para a cadeia do auto-play (`vp postiz upload` →
`pacote` → dúvida cega → `schedule`, ADR 025). Nada foi enviado nem agendado. Os três lugares a preencher
antes do `pacote`: `date` (ISO com fuso, futura), `image` (o `id` e o `path` que o `upload` devolve) e
`[LINK]` nas descrições do YouTube.

| Arquivo | Canal (id no Postiz) | Idioma |
| --- | --- | --- |
| `post-shorts-pt.json` | YouTube "Vinicius Koiti Nakahara", @viniciusnakahara (`cmqudfb0h0001lw83k1b8ugi7`) | pt-BR |
| `post-shorts-en.json` | o mesmo canal; vídeo `../teaser-D-en-voz.mp4` (18,8 s, voz clonada em inglês, −15,5 LUFS, 2026-10-25) | en |
| `post-instagram-pt.json` | Instagram "Desenvolvedor Plen", koiti.dev (`cmv8r4jw30001l2863lr8x1lo`), `post_type: post` (vídeo vira Reel) | pt-BR |
| `post-instagram-en.json` | o mesmo perfil | en |

Escolhas: o Instagram é o perfil de desenvolvedor (koiti.dev), não o de musculação nem os do Nabote; o
canal do YouTube é o pessoal, como pedido, e não um canal novo do kit (decisão anterior de 2026-10-25 no
auto-play). Dois posts no mesmo perfil com o mesmo vídeo em duas línguas podem parecer repetição no
Instagram: uma saída é o en só no YouTube.

## Antes de agendar

1. O vídeo final: `teaser-D-pt-voz-v2.mp4` tem a voz clonada e a boca presa à fala, mas não os planos 2
   (tela) e 8 (estilos); o dono ouviu a v1 e achou a voz dessincronizada (falas curtas com silêncio e a boca
   ciclando a cena inteira); a v2 corrige as duas coisas e espera a escuta dele. As falas desses planos estão em `data/episodes/teaser-motion-kit/voice/fora-*`.
2. `[LINK]` e "link na bio": o repositório é privado e o kit não está no npm. Sem o link público, "código
   aberto" na tela e na legenda não se sustenta.
3. A pele do apresentador está em `needs_review` (gerador não registrado). Registrar antes de publicar.
4. YouTube: marcar "conteúdo alterado ou sintético" no Studio depois de publicar (voz clonada e desenho a
   partir de fotos). O Postiz não tem esse campo.
5. A regra do canal: um Short por vez, horário à escolha do dono.

## Hipótese (a copiar para `metrics.json.hypothesis` quando houver metadados reais)

H: o molde "resultado na tela nos 2 primeiros segundos + entrada em segundos + troca de 47 estilos antes do
cartão" segura a retenção média do Short acima de 60% e traz mais cliques no link do que os Shorts anteriores
do canal. Variável: a forma do vídeo (molde da amostra do vidIQ de 2026-10-25). Medida: retenção média e
cliques do link no YouTube Studio aos 7 e 28 dias; no Instagram, alcance e salvamentos aos 7 dias.

## Textos

### YouTube Shorts, pt-BR

Título (98 caracteres):

> Descrevi 6 cenas em uma frase. O Claude escreveu o JSON, minha biblioteca renderizou em 47 estilos

Descrição:

```
Descrevi seis cenas em uma frase. O Claude escreveu o JSON e a minha biblioteca renderizou: número, gráfico, linha do tempo, comparação, e eu numa janela no canto. Mesmo conteúdo, 47 estilos.

O que é: motion-kit, uma biblioteca de componentes de vídeo para Remotion, com 47 estilos visuais prontos e uma ferramenta que monta o vídeo vertical a partir de um JSON com 15 tipos de cena. Quem escreve o JSON pode ser um agente, como o Claude Code; quem renderiza é a biblioteca, quadro a quadro.

Os números do vídeo são do repositório do kit (git log de 25/10/2026): 312 commits em 104 dias, 2 em julho e 272 em outubro; 10 tipos de cena em 10/10 e 15 hoje.

Código aberto (MIT): [LINK]

O apresentador é um desenho feito a partir de fotos minhas; a voz é a minha, clonada por IA.

#Shorts #motiongraphics #Remotion #ClaudeCode #IA #videoporcodigo
```

### YouTube Shorts, en

Título (96 caracteres):

> I described 6 scenes in one sentence. Claude wrote the JSON, my library rendered it in 47 styles

Descrição:

```
I described six scenes in one sentence. Claude wrote the JSON and my library rendered it: a number, a chart, a timeline, a comparison, and me in a window in the corner. Same content, 47 styles.

What it is: motion-kit, a library of video components for Remotion, with 47 ready-made visual styles and a tool that builds a vertical video from a JSON with 15 scene types. An agent such as Claude Code can write the JSON; the library renders it frame by frame.

The numbers in the video come from the kit's own repository (git log of 2026-10-25): 312 commits in 104 days, 2 in July and 272 in October; 10 scene types on Oct 10 and 15 today.

Open source (MIT): [LINK]

The presenter is a drawing made from my photos; the voice is mine, cloned by AI.

#Shorts #motiongraphics #Remotion #ClaudeCode #AI #opensource
```

### Instagram, pt-BR

```
Descrevi seis cenas em uma frase. O Claude escreveu o JSON e a minha biblioteca renderizou: número, gráfico, linha do tempo, comparação, e eu numa janela no canto. Mesmo conteúdo, 47 estilos.

É o motion-kit: componentes de vídeo para Remotion, 47 estilos prontos e um vídeo vertical montado a partir de um JSON com 15 tipos de cena. O agente escreve o JSON; a biblioteca renderiza quadro a quadro.

Os números são do repositório do kit (git log de 25/10/2026): 312 commits em 104 dias.

Código aberto, MIT. Link na bio.

Apresentador desenhado a partir de fotos minhas; voz clonada da minha por IA.

#motiongraphics #remotion #claudecode #ia #dev #videoporcodigo #opensource
```

### Instagram, en

```
I described six scenes in one sentence. Claude wrote the JSON and my library rendered it: a number, a chart, a timeline, a comparison, and me in a window in the corner. Same content, 47 styles.

This is motion-kit: video components for Remotion, 47 ready-made styles and a vertical video built from a JSON with 15 scene types. The agent writes the JSON; the library renders it frame by frame.

The numbers come from the kit's own repository (git log of 2026-10-25): 312 commits in 104 days.

Open source, MIT. Link in bio.

Presenter drawn from my photos; voice cloned from mine by AI.

#motiongraphics #remotion #claudecode #ai #dev #opensource #devtools
```

## Fatos usados e onde conferir

- 47 estilos: `packages/motion-kit/src/styles/catalog.ts` e o README do kit.
- 15 tipos de cena do JSON: `packages/motion-video/recipes/explainer.md` do kit (10 em 10/10/2026, pelo doc
  do teaser no kit).
- 312 commits em 104 dias (12/07 a 24/10/2026), 2 em julho e 272 em outubro: `git log` de 2026-10-25,
  registrado no doc do teaser no kit.
- MIT: `LICENSE` na raiz do repositório.
- Apresentador: `data/episodes/teaser-motion-kit/public/sprites/dono/origem.json` (desenho a partir de fotos do
  dono, 2026-10-12; licença pendente).
