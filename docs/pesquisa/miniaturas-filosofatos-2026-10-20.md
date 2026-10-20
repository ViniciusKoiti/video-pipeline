# Miniaturas do Filosofatos (2026-10-20)

Canal de referência do nicho que o dono indicou: **Filosofatos** (`@filosofatosx`, 465 mil inscritos). Vídeos de ~20 min,
filosofia e psicologia contadas com personagens de anime; quase todo título termina em "(pra ouvir enquanto faz outra
coisa)". Amostra: os 30 vídeos mais recentes da aba Vídeos, com as miniaturas atuais e as visualizações do dia.
As folhas ficaram fora do Git (imagens de terceiros).

## Visualizações da amostra

| Faixa | Vídeos (miniatura) |
|---|---|
| 300 mil ou mais | casal de anime sobre pôr do sol na cidade + "BASICO" (520 mil); Luffy e Chopper em cadeiras de plástico num bananal real, sem texto (477 mil); Eren de mangá em cinza sobre vermelho chapado, sem texto, "Como se fabrica um fascista?" (361 mil) |
| 200 a 300 mil | Morty de terno num campo ao pôr do sol (227 mil); busto de Maquiavel em cinza sobre vermelho (219 mil); Mob com a mão no rosto (208 mil); Marco Aurélio num campo + "PENSE" (204 mil); "FLOW" (211 mil) |
| abaixo de 100 mil | Eren colorido sobre vermelho, "Por que ninguém muda de voto" (67 mil, 4 dias); casal de Tokyo Revengers + "ENTENDA POR QUE DÓI" (71 mil) |

Visualização depende do tema, do título e da idade do vídeo; a amostra mostra o padrão visual, não prova qual
miniatura rende mais. O canal testa títulos: o vídeo do voto trocou de título entre duas consultas na mesma hora
("O experimento que fez eleitores trocarem de lado sem perceber").

## O padrão

1. **Um personagem só, recortado do fundo**, de busto ou meio corpo, no centro. Quase sempre personagem conhecido
   (One Piece, Jujutsu Kaisen, One Punch Man, Attack on Titan, Chainsaw Man). Às vezes dois, nunca mais.
2. **Três tipos de fundo:**
   - **paisagem real** (campo, pôr do sol, céu, floresta): 11 dos 30, os temas de vida e sentimento;
   - **vermelho chapado**: os temas de política e poder (voto, fascismo, Maquiavel);
   - **preto ou branco**, com o personagem em traço de mangá.
3. **Personagem em cinza de mangá** nos temas pesados (o Eren do fascismo, Chainsaw Man, Geto), às vezes com linhas
   horizontais finas.
4. **Texto: metade não tem.** Quando tem, é **uma palavra**, enorme, numa fonte larga sem serifa, branca, de ponta a
   ponta, em cima ou embaixo. O personagem fica **na frente** de parte das letras, e às vezes metade da palavra é só
   contorno. A palavra completa o título, não repete ("PENSE", "PASSADO", "DINHEIRO", "REAL").
5. O canal usa quadros e páginas de muitas obras. **Isso não vale para nós:** aqui só entra quadro oficial com crédito
   (ADR 007, emenda de citação).

## Como aplicar no `kira-voto-brasil`

- **Fundo vermelho chapado**, porque é o que o próprio canal usa em voto, fascismo e Maquiavel.
- **Light recortado em cinza de mangá**, sem texto ou com uma palavra larga atrás dele. O quadro oficial
  `crunchyroll-de-trailer-light-gravata` serve: meio corpo, gravata, mão erguida. Ele está em 480p ampliado, e o cinza
  com contraste esconde a falta de nitidez.
- **Recorte:** o ffmpeg não separa o personagem da cortina. Precisa de remoção de fundo: rembg com o modelo de anime,
  num ambiente separado, ou recorte à mão.
- **Fonte larga:** a Inter Display Black (OFL) já está instalada. Esticada na horizontal, chega perto da fonte do
  canal sem baixar nada.
