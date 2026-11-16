# Prompt: 3 Shorts cortados dos vídeos longos (para um agente GPT/Codex no repositório)

Escrito em 2026-11-11, a partir dos dois Shorts já montados (`idade-media-short-doenca` e `nietzsche-short-camelo`).
Cole o bloco abaixo numa sessão aberta em `~/projetos/auto-play`.

```
Você vai trabalhar no repositório ~/projetos/auto-play (pipeline de vídeo do canal Cena e Conceito). Leia primeiro
AGENTS.md e CLAUDE.md, em especial o §2 (regras inegociáveis), o §4 (Shorts cortados de um vídeo longo) e o §12
(conteúdo repetitivo). Eu sou o dono do canal.

OBJETIVO
Montar 3 Shorts verticais novos (1080×1920, 30 a 50 s), cada um cortado de um vídeo longo já aprovado, no mesmo
molde de dois Shorts que já existem. Trabalhe com calma, um Short por vez, e pare nos pontos marcados PARE para eu
verificar. Não publique, não agende e não envie nada ao Postiz.

OS DOIS MODELOS (leia antes de tudo; copie a forma, não o texto)
- data/episodes/idade-media-short-doenca/   → pauta.md, content.json, narracao.pt.json, montar.py
- data/episodes/nietzsche-short-camelo/     → pauta.md, content.json, content.render.json, narracao.pt.json, montar.py
A pauta.md de cada um tem o registro de produção com as decisões e os tropeços. O montar.py de cada um é o script
de montagem a adaptar.

MOLDE DE CADA SHORT
1. Abertura (3,5 a 5 s): um apresentador faz, com a minha voz clonada, uma pergunta que a primeira frase do corte
   responde. A pergunta também aparece escrita.
2. Corpo: um trecho contínuo do renders/final.mp4 do vídeo longo (só leitura), com a legenda por frase tirada do
   captions.srt do longo e queimada. Não regrave nem reescreva a narração do corpo.
3. Fecho (4 a 6 s): o apresentador chama para o vídeo completo no canal. A frase do fecho é diferente em cada Short.

FONTES PERMITIDAS PARA OS CORTES
- data/episodes/idade-media-ser-rico/ (já usados: cenas S19–S21 e S46–S48; não repetir)
- data/episodes/nietzsche-solo-leveling-sistema/ (já usado: trecho do camelo dentro da S07, 195,3–222,7 s; não repetir)
As cenas, com início e duração, estão em episode.json; o texto falado, em scenes.json; os tempos de cada frase, em
captions.srt. Nas cenas longas do Nietzsche o corte sai de dentro da cena, pelos tempos das frases.

ETAPA 1: PROPOSTA (não gera voz nem vídeo)
Leia os dois scenes.json e proponha 3 cortes. Para cada um, escreva:
- vídeo de origem, cenas, tempo de início e de fim, duração;
- a primeira e a última frase do corte, copiadas do scenes.json;
- a pergunta de abertura e a frase do fecho que você propõe;
- o texto escrito na tela na abertura e no fecho;
- por que o trecho se sustenta sozinho (não começa com "por isso", "ele", "essa" apontando para fora do corte).
Regras da proposta: a pergunta e o fecho não afirmam nada que o corte ou o vídeo longo não digam; não escreva fato
de memória. Cada fala nova deve ter pelo menos uns 3,5 s falados (frase muito curta não passa no nivelamento).
Pergunte também, uma vez só: qual apresentador usar em cada Short (o boneco de recortes do motion-kit, como no
Short da doença, ou o meu avatar, como no do Nietzsche).
PARE e espere a minha resposta.

ETAPA 2: MONTAGEM, UM SHORT POR VEZ (só depois da minha resposta)
Para cada Short aprovado, numa pasta nova data/episodes/<origem>-short-<assunto>/ :
a) Antes de qualquer render, rode a sonda de CPU: uv run python -c "from app.pipeline.bench import cpu_probe;
   print(cpu_probe())". Acima de 0,3 s a máquina está limitada: pare e me avise. Um render por vez.
b) content.json e narracao.pt.json no formato dos modelos (duas falas: "abertura" e "fecho", delivery "invite").
   Se o Short for do Nietzsche, copie voice/glossary.json do episódio longo para a pasta voice/ do Short.
c) Voz: uv run vp short voz <pasta> <pasta>/narracao.pt.json
   Isso chama a minha voz clonada na minha conta do Modal; está autorizado por este pedido, com no máximo 3
   chamadas por Short. Confira no resultado: volume final perto de −16 LUFS e a duração da fala. Se a fala do fecho
   passar de 6 s, veja com silencedetect se há pausa longa no meio antes de regerar.
d) Tempos: uv run vp short tempos <pasta> <pasta>/content.json <pasta>/narracao.pt.json
e) Render do apresentador, de dentro da pasta do Short:
   node ~/projetos/motion-kit/packages/motion-video/src/video.mjs render content.render.json
   onde content.render.json é uma cópia de content.voz.json sem o campo "locale" (a versão atual do kit o recusa).
   Não use dist/video.mjs e não rode npm install nem build no motion-kit. Imagens e sprites que o conteúdo cita
   ficam em <pasta>/public/. A janela flutuante do avatar sobre image_caption encolhe a imagem: não use.
f) Junção da voz: uv run vp short juntar <pasta> <pasta>/out/production/<execução>/video.mp4
   <pasta>/content.voz.json <pasta>/narracao.pt.json --saida <pasta>/personagem.mp4
g) Montagem final: adapte o montar.py do modelo (INICIO, FIM, pasta do longo, textos) e rode python3 -I montar.py.
   Se o trecho tiver cartão de citação ou texto na tela, use o quadro inteiro na largura, como no do Nietzsche.
h) Conferência: duração com ffprobe; volume com ffmpeg -af ebur128=peak=true; uma folha de 8 quadros (abertura,
   corpo, fecho) que você abre e olha. Corrija texto cortado, legenda fora do lugar ou imagem espremida.
i) Escreva <pasta>/pauta.md no formato dos modelos: origem e tempos do corte, tabela da estrutura, registro de
   produção com os números medidos, rascunho de título e descrição (a descrição abre com "Dê uma olhada na
   história completa na descrição ou entrando no canal" e deixa o link do vídeo longo como lacuna), e o que falta
   eu decidir. Diga com todas as letras o que você conferiu em quadros e que ninguém ouviu o áudio.
PARE ao fim de cada Short e me mostre: caminho do MP4, duração, volume, as duas falas e o que eu devo ouvir.
Só comece o próximo depois do meu ok.

O QUE NÃO FAZER
- Não rodar vp postiz, vp short gate nem vp approve: gate 4 e agendamento são meus.
- Não alterar nada dentro de data/episodes/idade-media-ser-rico/ nem de nietzsche-solo-leveling-sistema/.
- Não baixar nem gerar imagem nova; só ativos já aprovados no episódio de origem (review_status approved).
- Não usar quadro ou clipe do anime no Short sem me perguntar.
- Não chamar nenhum provedor além do Modal da voz. Custo zero.
- Não apagar arquivos: versão refeita vai em arquivo novo, e a anterior fica.
- Não alterar código em app/, video/ nem no motion-kit. Se algo do pipeline quebrar, pare e me descreva o erro.
- Não criar commits.

RELATO FINAL
Uma lista dos 3 Shorts com caminho, duração, volume, pergunta, fecho e pendências, mais qualquer coisa que tenha
saído diferente deste pedido.
```
