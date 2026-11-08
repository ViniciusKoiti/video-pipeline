# Nota: traço e desenho na série "Educação Financeira Ilustrada" e o que falta no motion-kit

Data: 2026-11-03. Canal: Manual da Evolução. Material: 13 vídeos (a playlist e 3 destaques), medidos e com folhas
de 32 quadros; quadros densos (0,1 s em janelas de 4 s) em `3uwj`, `98KJ` e no nº 1. Material de terceiros: só
para análise, fora do Git (`data/cache/nicho/Educacao-financeira-ilustrada/`).

## 1. Limites

- O que está aqui vem de quadros, não de medida de pixel. A espessura do traço **não foi medida**.
- Cada janela densa cobre 4 s. O comportamento de um vídeo inteiro é uma amostra.
- Os 13 vídeos são de um canal só. O padrão pode ser do canal, não do nicho.

## 2. Dois modos de cena

"Somente em uma cena" descreve bem o que se vê: o desenho ao vivo não ocupa o vídeo todo.

- **Modo A, desenho ao vivo.** Uma mão desenha no quadro. A linha aparece, depois entra a cor.
  Exemplo: `3uwj`, 451 a 455 s, a pilha de livros: linha a lápis preto e, depois, as cores vermelha, verde e roxa.
- **Modo B, cartão parado com micro-movimento.** Texto e caixa ficam parados; as figuras se mexem pouco.
  Exemplo: `98KJ`, 312 a 316 s, "EQUILÍBRIO FINANCEIRO": quadros quase idênticos por segundos.

A mão aparece em trechos curtos do modo A, não o tempo todo. Em `3uwj`, ela aparece em 451 s e some na maior parte
de 452 a 455 s.

## 3. Mecânica do traço (observada)

1. **Linha antes da cor.** O contorno sai primeiro, em preto; a cor chapada vem depois, em outro momento.
2. **Pausa.** Por segundos o quadro não muda. Só se mexe quando há desenho ou uma figura se move.
3. **Apagar e trocar.** No nº 1 (276 a 280 s), uma borracha apaga o pote "RECURSOS" antes de desenhar a citação.
4. **Caixas de rótulo.** Texto em caixa-alta dentro de um contorno preto, como "PENSE COMO PRODUTOR" (`3uwj`) e
   "EQUILÍBRIO FINANCEIRO" (`98KJ`).
5. **Duas linguagens de cor.** O nº 1 usa linha preta e cor só em destaques. `3uwj` e `98KJ` usam figuras de cor
   chapada (azul, verde, vermelho, amarelo) sobre a linha.
6. **Títulos de fase na tela.** `3uwj` põe "Fase 1…", "Fase 2…", "Fase 3…" em caixa no topo. O nº 1 não tem isso.

## 4. Componentes do motion-kit: o que existe e o que falta

Status: **existe** (usar como está), **parcial** (usar com ajuste), **falta** (criar). Peças conferidas nos
arquivos do checkout 0.7.3; o template renderiza 0.7.1.

| # | Comportamento | Onde aparece | Peça no kit | Status | Ação |
|---|---|---|---|---|---|
| 1 | Traço que se desenha | todos | `DrawPath` (`at`, `duration`) | existe | — |
| 2 | Traço que afina nas pontas | linha a lápis | nada | falta | `InkStroke` (`taper`) |
| 3 | Cor que entra depois da linha | `3uwj` (livros) | `DrawPath.fill`: aparece junto com o traço, pelo progresso | parcial | `fillAt` e `fillDuration` separados |
| 4 | Ponta que segue o traço no lugar da mão | modo A | nada | falta | `PenTip`, sem mão (regra do projeto) |
| 5 | Apagar um elemento | nº 1, borracha | `SoftMask` (frente que avança) | parcial | `Erase` |
| 6 | Pausa com quadro parado | `98KJ`, `3uwj` | `Stepped` | existe | — |
| 7 | Micro-movimento de cartão parado | `98KJ` | `motion/drift.ts` (hoje em `CameraRig` e `ParallaxLayer`) | parcial | aplicar a elementos, não só à câmera |
| 8 | Caixa de rótulo com borda que se desenha e texto dentro | `98KJ`, `3uwj` | `StampMark`, `Tape`, `Callout` | parcial | `LabelBox` |
| 9 | Texto que se escreve, títulos de fase | `3uwj` | `CaptionText` (texto por palavra) | parcial | `TextReveal` (máscara de escrita) |
| 10 | Pote ou balde que enche | `98KJ`, nº 1 | nada (`Gauge` é radial) | falta | `FillLevel` |
| 11 | Setas que se desenham | `3uwj`, `98KJ` | `DrawPath` + `arrowHead` | existe | — |
| 12 | Números que contam | nº 1, `98KJ` | `Odometer`, `useCountUp` | existe | — |
| 13 | Pilha que cresce (livros, caixas) | `3uwj` | nada | falta | `StackBuild` (pequeno) |
| 14 | Figura de linha com membros que se mexem | `3uwj`, `98KJ` | nada | falta | `StickLimbs`; depende da decisão sobre o corpo |
| 15 | Quadro que persiste entre cenas | modos A e B | nada | falta | `Board` |
| 16 | Papel com grão e manchas | todos | `StyleTexture` | existe | — |
| 17 | Cor chapada desalinhada | `3uwj` (confirmar) | `Overprint`, `misregister` | existe | — |
| 18 | Hachura de sombra | pouco aparece | `PatternFill` | existe | verificar se é usada |

**Prioridade**

- **P1 (essencial para o modo A):** `InkStroke` (2), `fillAt` (3), `LabelBox` (8), `Erase` (5), `FillLevel` (10) e `PenTip` (4).
- **P2:** `TextReveal` (9), `Board` (15) e `StackBuild` (13).
- **P3, depende de decisão:** `StickLimbs` (14). Depende de arte, e a decisão sobre o corpo ainda está aberta.

## 5. O que não copiar

- Mão, figuras e composições do canal. Copiamos só a mecânica: linha antes da cor, pausa, apagar e trocar.
- As caixas e os títulos de fase são estrutura do vídeo, não obra. Podemos usar o formato sem o texto.

## 6. Próximos passos

1. Confirmar a mecânica em mais janelas: abertura, meio e fim de três vídeos, não só do `3uwj`.
2. Medir a espessura do traço com um recorte de quadro, para decidir os parâmetros do `InkStroke`.
3. Decidir a ordem das peças P1 com o dono.
