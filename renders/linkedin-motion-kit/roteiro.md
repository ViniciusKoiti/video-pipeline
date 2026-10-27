# Vídeo do LinkedIn: motion-kit com o pipeline por trás (roteiro, 2026-10-27)

Corte para o LinkedIn do Short 2 "um vídeo fazendo um vídeo" (`renders/short-making-of/roteiro.md`). Protagonista:
o **motion-kit**; o auto-play entra num bloco só, como o lugar onde o kit roda todo dia. Frase-guia: "eu construí".
Público: devs, tech leads, recrutadores. Rascunho para o dono validar: nada de voz nova nem render até lá.

- **Formato:** 4:5, 1080×1350, 30 fps, por volta de 70 s. O teaser (9:16) fica numa coluna à esquerda, perto de
  40% da largura; o painel dos passos e das gravações (16:9) à direita; o dono na janela flutuante desde o quadro 0.
  Legenda queimada embaixo, porque o feed começa sem som. Alternativa sem trabalho de layout: subir o Short 2 em
  9:16 como está e trocar só o fecho.
- **Composição:** nova (`LinkedInDemo`) em `~/projetos/motion-kit/examples/divulgacao/`, reaproveitando as peças do
  `MakingOfDemo.tsx` e de `pieces.tsx`. O bloco do pipeline usa o `<Pipeline stages>` do próprio kit
  (`COMPONENTS.md`, "Componentes de cena"), então o diagrama também é uma peça do kit.
- **Voz:** cinco falas reaproveitadas do Short 2 (`data/episodes/short-making-of/voice/*-ptbr-*.wav`) e quatro novas
  pela `chatterbox_modal`, no fluxo da skill `shorts-tec`.

## Batidas

| # | Batida | Tela | Fala | Voz | ~s |
| --- | --- | --- | --- | --- | --- |
| 1 | `capa` | Cartão "Esse teaser saiu de **uma frase**." legível no quadro 0; o teaser tocando, mudo; o dono na janela | Esse teaser saiu de uma frase. | **nova** | 3,5 |
| 2 | `frase` | #1 a frase sendo digitada, #2 o `content.json` linha a linha (gravação de tela 1) | Eu escrevi a frase no Claude Code. Ele escreveu o JSON: seis cenas, com os números do meu repositório. | Short 2 | 8,0 |
| 3 | `confere` | #3 os três avisos reais do `inspect`, #4 a grade dos seis quadros do `review` (gravação 2) | A ferramenta confere o JSON antes de renderizar. Avisa quando uma cena fica curta demais para ler, e gera um quadro de revisão de cada cena. | Short 2 | 10,5 |
| 4 | `render` | #5 o render, #6 as barras com o envelope da voz (gravação 3) | Depois, o render. A minha voz entra por cima, clonada numa GPU, e a boca da janela segue cada fala. | Short 2 | 8,5 |
| 5 | `resultado` | 6 s do teaser com o som dele, grande, sem a janela do dono | (o áudio do teaser) | teaser | 6,0 |
| 6 | `pipeline` | `<Pipeline>` com os estágios: fontes → fichas → roteiro → `vp check` → 4 aprovações → motion-kit → vídeo; o estágio aceso segue a fala | Por trás, o kit é o motor do meu pipeline de vídeo. Agentes do Claude Code escrevem o roteiro a partir das fontes, o código confere cada afirmação contra a fonte, e eu aprovo em quatro etapas. | **nova** | 13,0 |
| 7 | `provas` | Três cartões com contador: "322 commits · desde jul/2026", "821 testes", "5 ensaios em 7 dias · Cena e Conceito" | Trezentos e vinte e dois commits no kit desde julho, oitocentos e vinte e um testes no pipeline, e cinco ensaios longos em uma semana no meu canal, o Cena e Conceito. | **nova** | 11,0 |
| 8 | `biblioteca` | Montagem dos quadros de `docs/stills` do kit e dos 12 estilos, como no Short 2 | E a biblioteca desenha mais do que o JSON pede hoje: mapa, grafo, foto de arquivo, documento, tela dividida, janela flutuante. Quarenta e sete estilos prontos. | Short 2 | 10,6 |
| 9 | `fecho` | O dono grande, falando; cartão "motion-kit · link no 1º comentário" | ver variantes abaixo | **nova** | 4,5 |

Total previsto: ~76 s. Se passar de 75 s, encurtar a batida 8 (só os estilos, 4 s) antes de mexer nas outras.

### Fecho: variantes, de acordo com o link

- **A, kit público** (GitLab aberto ou npm): "É código aberto. O link está no primeiro comentário."
- **B, kit ainda fechado:** "Vou abrir o código em breve. O link para acompanhar está no primeiro comentário."
  O link seria o `github.com/ViniciusKoiti/baixo-nivel-demos` ou o perfil.

## Fatos usados (conferir de novo no dia do render)

- "Esse teaser saiu de uma frase": a batida 1 do Short 2 dizia "Este vídeo inteiro". Aqui não vale, porque este
  vídeo também tem TSX e o bloco do pipeline; a frase fica presa ao teaser que aparece na tela.
- "322 commits no kit desde julho": `git rev-list --count HEAD` no motion-kit em 2026-10-27, primeiro commit em
  2026-07-12. Refazer a conta no dia do render.
- "821 testes no pipeline": `uv run pytest --collect-only -q` em 2026-10-27 (821 de 827; os 6 lentos ficam fora).
- "cinco ensaios longos em uma semana": `death-note-fins-meios`, `kira-voto-brasil`, `historia-vencedores`,
  `epicteto-na-sua-mao` (20 a 23/10) e `montaigne-desapego` (26/10), todos agendados pelo Postiz
  (`data/publicacoes/registro.jsonl`). Agendado não é publicado: **conferir no YouTube Studio** que os cinco saíram;
  se algum não saiu, trocar o número.
- "Agentes do Claude Code escrevem o roteiro a partir das fontes": ADR 009 (agentes em `.claude/agents/`).
  "o código confere cada afirmação contra a fonte": `vp check` confere a citação literal de cada ficha (§6 do
  CLAUDE.md). "aprovo em quatro etapas": os 4 gates (§2.5).
- Batidas 2 a 4 e 8: os fatos estão no roteiro do Short 2.

## Post (rascunho, pt)

> Esse vídeo foi montado pelo Claude Code com uma biblioteca que eu construí.
>
> O motion-kit é uma biblioteca de componentes de vídeo para Remotion. O agente escreve um JSON com as cenas, a
> ferramenta confere o JSON antes de renderizar e gera um quadro de revisão por cena, e o render sai sem editor de
> vídeo. A voz é a minha, clonada numa GPU, e a boca da janela segue cada fala.
>
> O kit é o motor de um projeto maior: um pipeline em que agentes escrevem o roteiro a partir de fontes, o código
> confere cada afirmação contra o trecho de onde ela saiu e eu aprovo em quatro etapas. Na semana passada saíram
> cinco ensaios longos por ele no meu canal, o Cena e Conceito.
>
> 322 commits no kit, 821 testes no pipeline, 47 estilos visuais.
>
> [variante A] É código aberto (MIT); o link vai no primeiro comentário.
> [variante B] Vou abrir o código em breve; o link para acompanhar vai no primeiro comentário.
>
> Apresentador desenhado a partir de fotos minhas; voz clonada da minha por IA.
>
> #Remotion #ClaudeCode #motiongraphics #TypeScript

## Pendências antes de publicar

1. Validação do dono: este roteiro, o 4:5 e a variante do fecho.
2. As três gravações de tela (instruções no roteiro do Short 2); sem elas as batidas 2 a 4 ficam com espaço marcado.
3. O gerador e a licença da pele do apresentador: `data/episodes/teaser-motion-kit/public/sprites/dono/origem.json`
   está com `gerador: null` e `needs_review`.
4. Os cinco ensaios conferidos no Studio (batida 7 e post).
5. Depois do render: gate 4 por `shorts_tec.py gate` + `vp approve`, e a cadeia do `vp postiz` (pacote, dúvida
   cega, confirmação). Conferir se o LinkedIn está conectado no Postiz: o rascunho do Short 2 tem um `integration.id`,
   mas isso não confirma a conexão.
