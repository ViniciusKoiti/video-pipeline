# Vídeo do LinkedIn: como os vídeos funcionam por dentro (roteiro técnico, 2026-10-27)

Substitui `roteiro.md` (mesma pasta), que o dono reprovou: ele quer mostrar **como os vídeos funcionam
tecnicamente**. Fio único: **uma cena real do teaser**, a `numero` ("312 commits em 104 dias", em
`data/episodes/teaser-motion-kit/content.pt.janela.json`), seguida do JSON até o MP4. Cada passo mostra o código
ou a saída de verdade. Público: devs e tech leads. Quem apresenta, numa janela flutuante o tempo todo, é o
**a pele de sprites do dono** (a mesma do teaser), com a voz clonada dele. Troca pedida pelo dono em 2026-10-27,
depois de assistir à versão com o personagem azul A (pele de recortes do kit, folha
`apresentador-azul/FolhaAzulRest.png`), que fica como alternativa na composição.
Rascunho para o dono validar: nada de voz nem render até lá.

- **Formato:** 4:5, 1080×1350, 30 fps, por volta de 80 s, legenda queimada. Código em fonte mono grande, no
  máximo 10 linhas por quadro, com foco por passo (`<CodeWalkthrough>` do kit).
- **Composição:** TSX nova no kit (`examples/divulgacao/ComoFuncionaDemo.tsx`), com as peças de `pieces.tsx` (o
  terminal do `Cofre`) e o `<Pipeline>` no fecho. O teaser renderizado entra como vídeo.
- **Apresentador:** `createCutoutSkin` com a receita A de `~/projetos/motion-kit/examples/divulgacao/FolhaAzul.tsx`
  (`hair: 'crop'`, `outfit: 'jacket'`, `hands: 'mittens'`, casaco `#2f6fb3`, forro `#1f4778`, detalhe `#f2c14e`;
  `parts.backHair` = capuz levantado, `parts.head` = rosto sem orelhas), no `<Host>` dentro de uma `<FloatingWindow>`.
  A boca segue o envelope da voz quadro a quadro (`mouthLevels`, gerado por `shorts_tec.py boca`); aponta (`gesture:
  'point'`) quando a tela mostra código ou número. A pele de recortes só existe em TSX, o que já é o caso aqui.
- **Voz:** nove falas novas, voz clonada (`chatterbox_modal`), pelo fluxo da skill `shorts-tec`.

## Batidas

| # | Batida | Tela | Fala | ~s |
| --- | --- | --- | --- | --- |
| 1 | `gancho` | À esquerda, a cena "312 commits" do teaser rodando; à direita, o objeto JSON dela, campo a campo | Essa cena de quatro segundos é um objeto JSON com oito campos. Vou mostrar o caminho dela até o vídeo. | 6 |
| 2 | `contrato` | `content.schema.ts`, foco na linha do `number` (`z.strictObject`, `type: z.literal('number')`); ao lado, os 15 tipos de cena acendendo | Cada cena tem um tipo, e são quinze. Um schema em Zod valida o JSON, e um campo que o schema não conhece é erro. | 8 |
| 3 | `legivel` | Régua de quadros: 0 → 6 (o número entra) → 56 (para de rolar) → 86 (30 de leitura); embaixo, o aviso `SCENE_TOO_SHORT_TO_READ` como o `inspect` escreve | Antes do render, o inspect calcula em que quadro a cena fica legível. O número entra no quadro seis e rola por cinquenta. Com trinta quadros de leitura, essa cena precisa de pelo menos dois vírgula nove segundos, e abaixo disso ele avisa. | 11 |
| 4 | `mesmas-constantes` | Dois trechos lado a lado: `ready = TIMING.start + TIMING.roll` (`readable.ts`) e `<Odometer delay={TIMING.start} duration={TIMING.roll}>` (`ExplainerDemo.tsx`), com `TIMING` aceso nos dois | E a conta usa as mesmas constantes do componente que desenha a cena. Se o tempo da animação muda, o aviso muda junto. | 7 |
| 5 | `voz` | A linha da `narracao.json` → o arquivo `numero-chatterbox_modal-ptbr-49db73f1a2.wav`, com o hash aceso; um selo "GPU T4 · Modal" | A narração é uma fala por cena. Cada fala vira um WAV com a minha voz clonada, numa GPU no Modal, e o nome do arquivo leva um hash do texto, do modelo e da gravação. Se nada mudou, a fala não é gerada de novo. | 11 |
| 6 | `tempo` | Forma de onda do WAV com o `silencedetect` marcando começo e fim; depois o diff do JSON: `durationSec: 2.9 → 3.8` e `host.speaking: true → [0.0, 3.48]` | O ffmpeg acha onde a fala começa e termina. Ela dura três vírgula quarenta e oito segundos, então a cena cresce de dois vírgula nove para três vírgula oito, e a boca da janela só fala nesse trecho. | 10 |
| 7 | `render` | O teaser sendo renderizado (terminal do `render` com o contador de quadros, saída real); ao lado, a cena "312" quadro a quadro | O render é o Remotion. Cada cena é um componente React, e um Chrome sem tela tira um quadro de cada vez, trinta por segundo. Sai um MP4 mudo. | 9 |
| 8 | `juntar` | O filtro do ffmpeg quebrado em linhas: `adelay=2900\|2900` (o começo da cena), `amix=…:normalize=0`, `loudnorm=I=-14:TP=-1.5:LRA=11`, `aresample=48000`; depois a cena com o som | No fim, o ffmpeg põe cada fala no começo da cena dela, soma as falas e acerta o volume em menos quatorze LUFS. | 8 |
| 9 | `apresentador` | A receita A em código (`createCutoutSkin({ hair: 'crop', hands: 'mittens', parts: { backHair: capuz, head: rosto } })`), com o personagem ao lado montando peça por peça; depois as barras do envelope e a boca acompanhando | E até quem está falando é um componente do kit: uma função monta o personagem a partir de peças, e a boca segue a energia da minha voz, quadro a quadro. | 9 |
| 10 | `fecho` | O `<Pipeline>`: JSON → schema → inspect → voz → tempo → render → ffmpeg → MP4; o dono grande; cartão "link no 1º comentário" | O agente escreve o JSON, e o resto é código: confere, mede e renderiza. O kit vai ficar aberto, e o link para acompanhar está no primeiro comentário. | 7 |

Total previsto: ~86 s. Se passar de 85 s, juntar as batidas 3 e 4 (fica só a régua, sem os dois trechos lado a lado).

A batida 10 depende do link. A fala gravada é a da variante "vai ficar aberto"; se o kit estiver público no dia,
regenerar só ela ("É código aberto, e o link está no primeiro comentário.").

## Fatos usados (todos do código, conferidos em 2026-10-27)

- **Oito campos e quatro segundos:** `id`, `type`, `durationSec`, `value`, `from`, `label`, `note`, `host` na cena
  `numero` de `content.pt.janela.voz.json`, com `durationSec: 3.8`.
- **Quinze tipos e Zod estrito:** `headline`, `image_caption`, `animation`, `comparison`, `number`, `categories`,
  `share`, `trend`, `timeline`, `grid`, `hook`, `calculation`, `receipt`, `end_card` e `presenter`, cada um um
  `z.strictObject` em `motion-kit/packages/motion-video/composition/content.schema.ts` (o `number` na linha 61).
  O `strictObject` recusa chave desconhecida.
- **Quadros 6, 56 e 86:** `TIMING.start = 6` e `TIMING.roll = 50` (`composition/readable.ts:15-34`), e o caso do
  `number` é `ready = TIMING.start + TIMING.roll` (`readable.ts:136-138`). `MIN_READING_FRAMES = 30` (`readable.ts:49`).
  O aviso, em `src/production.mjs:467`, pede `ceil((56 + 30) / 30 × 10) / 10 = 2,9 s`, exatamente a duração que a
  cena tinha antes da voz (`content.pt.janela.json`).
- **As mesmas constantes:** o `<Odometer delay={TIMING.start} duration={TIMING.roll}>` de `ExplainerDemo.tsx:98`;
  o comentário de `readable.ts` diz que os tempos são os da composição.
- **Hash da fala:** "o hash cobre o texto, o provedor, o modelo, a gravação de referência e a entrega"
  (`scripts/provisorio/shorts_tec.py`, docstring). A narração diz "texto, modelo e gravação". **GPU T4:**
  `deploy/modal_chatterbox.py:47`.
- **Silencedetect e 2,9 → 3,8:** `speech_bounds` e `fit_durations` (`shorts_tec.py`):
  `max(duração, fala + 0,3)` arredondado ao décimo acima, ou seja, 3,48 + 0,3 = 3,78 → 3,8. O antes e o depois estão
  em `content.pt.janela.json` (`2.9`, `speaking: true`) e `content.pt.janela.voz.json` (`3.8`, `[0.0, 3.48]`).
- **A boca nesse trecho (batida 6):** no JSON do teaser, a janela usa `<Host speaking>` enquanto o quadro está
  dentro de `host.speaking` (`ExplainerDemo.tsx`, `HostPane`).
- **O apresentador (batida 9):** `createSpriteSkin` monta a pele a partir de um manifesto de peças em camadas
  (`packages/motion-kit/src/host/sprites.ts`); o `sprites.json` do dono tem 3 camadas (base, olhos, boca) e 8
  desenhos (6 bocas, olhos fechados, base). Na versão azul era `createCutoutSkin`, com `parts` por callback. `mouthLevels` é o "envelope
  RMS da narração" e vence `speaking` (`packages/motion-kit/src/host/state.ts:47-49`); os níveis saem de
  `app/media/envelope.py` (RMS por quadro, normalizado pelo percentil 95 da cena) via `shorts_tec.py boca`. Os
  desenhos incluídos na fábrica são MIT (mesma seção); o capuz e o rosto sem orelhas da receita A são peças
  originais escritas em 2026-10-27 (`FolhaAzul.tsx`), só formas geométricas.
- **Remotion, Chrome sem tela, 30 fps, MP4 mudo:** README do `motion-video` ("Chrome Headless Shell do Remotion";
  "Os vídeos são verticais (1080×1920) e silenciosos") e `fps: 30` no JSON.
- **O filtro:** `mix_filter` (`shorts_tec.py`). `adelay=2900` porque a cena `gancho` dura 2,9 s = 87 quadros, e a
  `numero` começa no quadro 87 (`scene_starts`). Alvo de −14 LUFS: `TARGET_LUFS` (`app/media/loudness.py`).

## Material a capturar (real, nada encenado)

1. A saída do `inspect` de uma cópia do JSON com a `numero` em 2,0 s, para o aviso aparecer de verdade na batida 3
   (sem alterar os arquivos do teaser).
2. O terminal do `render` do teaser (log já existe em `data/episodes/teaser-motion-kit/out/render-janela-voz-pt-v2.log`;
   conferir se ele mostra o contador de quadros, senão gravar de novo).
3. A forma de onda do `numero-chatterbox_modal-ptbr-49db73f1a2.wav`, desenhada a partir do próprio arquivo.

Nenhum desses itens precisa de gravação de tela pelo dono: tudo sai de arquivo ou de comando.

## Post (rascunho, pt)

> Como uma cena de 4 segundos sai de um JSON de 8 campos.
>
> Eu construí o motion-kit, uma biblioteca de vídeo em React sobre o Remotion, e um fluxo em que o agente escreve
> o JSON e o código faz o resto. O caminho de uma cena:
>
> 1. Um schema em Zod valida o JSON (15 tipos de cena; campo desconhecido é erro).
> 2. O inspect calcula, sem renderizar, em que quadro a cena fica legível, com as mesmas constantes do componente
>    que a desenha, e avisa se ela acaba antes.
> 3. A fala vira um WAV com a minha voz clonada numa GPU; o nome leva um hash, e fala que não mudou não é gerada
>    de novo.
> 4. O ffmpeg mede a fala, e a cena cresce até ela caber.
> 5. O Remotion renderiza quadro a quadro num Chrome sem tela.
> 6. O ffmpeg põe cada fala no começo da cena dela e acerta o volume em −14 LUFS.
>
> [link: código aberto (MIT) no primeiro comentário, ou "o código vai ficar aberto"]
>
> O apresentador é um desenho meu, feito a partir de fotos minhas; a voz é a minha, clonada por IA.
>
> #Remotion #TypeScript #React #ffmpeg #ClaudeCode

## Pendências antes de publicar

1. **A licença da pele do dono:** `data/episodes/teaser-motion-kit/public/sprites/dono/origem.json` está com
   `gerador: null` e `needs_review`. Falta o dono informar a ferramenta (e o plano) que gerou a folha; sem isso a
   pele vale só para prévia (§2.3). O ativo do personagem azul (`assets/apresentador-azul.json`) ficou sem uso.
2. Gate 4: o dono assiste `linkedin-pt-voz-dono-2.mp4` e aprova (`vp approve linkedin-motion-kit --step preview`).
3. O link do primeiro comentário (o post diz "o código vai ficar aberto"); o comentário é feito à mão.
4. Data e hora (proposta: 28/10 9h); com a data e o gate, refazer `vp postiz pacote` e a dúvida cega.

Feito: LinkedIn conectado no Postiz; vídeo enviado (mídia `0f93c8ac-…`); post em
`posts/post-linkedin-pt.json`; primeiro pacote e dúvida cega ("não segue": gate 4 e o roteiro ainda falando do
personagem azul, corrigido aqui).

## Produção (2026-10-27)

- **Narração e batidas:** `data/episodes/linkedin-motion-kit/` (`narracao.pt.json`, `content.json` com as batidas,
  fora do Git). Voz clonada (`chatterbox_modal`) pelo `shorts_tec.py voz`: 10 falas, 98,1 s de fala; `tempos` levou
  as batidas de 86,0 s para **101,8 s** (a fala saiu mais lenta que a estimativa; maior: `legivel`, 14,8 s).
- **Legenda por frase:** `captions.srt` (47 blocos), com as fronteiras nos silêncios do WAV de cada fala
  (`app/media/captions.py`), na posição que o `juntar` dá à fala.
- **Composição:** `ComoFunciona` no kit (`examples/divulgacao/ComoFuncionaDemo.tsx`, com a pele do dono pelo
  `manifest` dos dados e o azul de `apresentadorAzul.tsx` como alternativa, registrado em `examples/Root.tsx`), dados em `examples/public/divulgacao/linkedin.json`
  (batidas, boca, legenda e os trechos reais). Nada commitado no kit.
- **Saídas reais na tela:** o aviso do `inspect` numa cópia do JSON pré-voz com a `numero` em 2,0 s ("A cena fica
  pronta para ler no frame 56 e dura 60: sobram 4 de leitura. Use pelo menos 2.9 s."); o log do render do teaser
  (588 quadros, 230 s); o filtro do `mix_filter` com os tempos do teaser (`adelay=2900|2900`).
- **A pele do dono fora do quadro:** o teaser traz a janela com o rosto do dono (y 416–673 de 1920). O trecho da cena
  `numero` entra recortado acima de 42% da altura, só com o número.
- **Versão com a pele do dono (2026-10-27):** `linkedin-pt-voz-dono-2.mp4` (101,8 s, −15,1 LUFS), mesmas falas;
  painéis de código sem quebra no meio da palavra. O trecho do teaser segue recortado, então a janela do teaser
  não aparece; a pele do dono aparece na janela do vídeo, na batida 9 e no fecho.
- **Pronúncia (2026-10-27):** glossário `voice/glossary.json` (JSON → "jêison", ffmpeg → "éfe éfe ém pég" etc.),
  aplicado pelo `shorts_tec.py voz`; 8 falas novas, aprovadas pelo dono na prévia `pronuncia-previa.m4a`.
  Saída `linkedin-pt-voz-dono-3.mp4` (108,2 s, −15,0 LUFS), enviada ao Postiz (mídia `3c7f22c7-…`); o gate 4
  aprovado antes valia para a `-dono-2` e precisa de nova aprovação.
- **Kit público (2026-10-27):** o GitLab `ViniciusKoiti/motion-kit` já está `public` com MIT no `main` (npm ainda
  não). Fecho regravado ("O kit é aberto, e o link está no primeiro comentário.") e post com "é código aberto
  (MIT)"; link do 1º comentário: https://gitlab.com/ViniciusKoiti/motion-kit. Saída
  `linkedin-pt-voz-dono-4.mp4` (105,9 s, −15,0 LUFS), no Postiz como mídia `de1eeac7-…`.
