# O que a animação do Epifania faz e o que já temos para chegar perto (2026-11-01)

Pedido do dono: o Epifania tem uma sequência de animações que hoje não fazemos; explorar para ver como melhorar.
Base: as folhas de quadros de dois vídeos do Epifania Experiência já medidos
(`data/cache/nicho/Nicho recap de anime/{sqLo6C2WGi0,ITDek8wyNT4}_folha.jpg`), a classificação de imagem
(`analise/classificacao-imagem/classificacao.tsv`) e o catálogo do motion-kit (MCP `motion-kit`), conferido
contra a versão instalada em `video/` (0.7.1, tarball de `video/vendor/`). **Só vi quadros parados**: o movimento
vem do que a classificação registra ("em movimento"), não de ter assistido.

## O que o Epifania faz (observado nas folhas)

Dois estilos nos dois vídeos medidos, ambos com ilustração própria em ~60% do tempo:

| | ESTOICISMO (7,86 mi views, 2019, 8min36s) | NIILISMO (1,12 mi views, 2021, 8min57s) |
|---|---|---|
| Fundo | branco, "quadro branco" | preto |
| Motor visual | mão com caneta desenhando ícones e escrevendo citações; os ícones se acumulam num cartaz-resumo no fim | boneco palito branco que atua a ideia (olha galáxias, corda, balanço, estrada, penhasco, guitarra) |
| Citação | texto escrito na tela, autor embaixo | foto P&B do pensador ao lado da citação em papel rasgado |
| Rótulos | palavra-chave grande (ESTOICISMO, ABSURDO, NIILISMO × EXISTENCIALISMO) | idem |
| Fecho | ícones de redes | tabela comparativa e ícones de redes |

## O que o kit 0.7.1 já tem e o template do longo não usa

O template (`video/src`) só usa `ArchivalPhoto`, `CameraRig`, `DocumentPage`, `Host` e `KineticHeadline`. No kit instalado
existem, sem uso aqui:

- `PaperPiece`, `EdgeClip` (papel rasgado), `Tape`: o cartão de citação rasgado.
- `StyleImage` (`mono`, `noir`, `duotone`) e `CutoutPortrait`: o retrato P&B do pensador.
- `DrawPath` (caminho SVG que se desenha, com tremor de mão) e `Marker` (círculo, sublinhado, risco, seta com
  traço de caneta): o gesto de desenhar e de marcar.
- `Stepped` (animação em passos, estilo "quadro a quadro"), `Distress` (desgaste), `Highlighter` (marca-texto).
- `CameraPath` (câmera que viaja entre enquadramentos), `LottieAsset` (animações prontas), `Host` com pele de sprites
  em camadas (personagem próprio com poses e expressões).

## O que falta de verdade

1. **A mão que desenha.** Nenhum componente põe uma mão acompanhando o traço. Seria um sprite de mão (arte) seguindo o
   caminho do `DrawPath`.
2. **O boneco protagonista.** O `Host` de sprites aceita um personagem próprio, mas a arte não existe. A regra do
   projeto é personagem só de peça com licença aberta ou de ilustrador, e rascunhos à mão feitos por mim já foram
   reprovados. Um boneco palito geométrico (cabeça em círculo, traços) desenhado por código pode ser aceito,
   mas é **decisão do dono**.
3. **As ilustrações-metáfora** (galáxia, corda, balanço, estrada, penhasco): arte própria, imagem gerada com
   divulgação (Workers AI, teto de 12 por episódio) ou Lottie com licença verificada.
4. **Integração no schema:** os planos do longo não têm "cartão de citação com retrato" nem "ícone que se desenha".
   Mudar plano muda o contrato; vale pelo vídeo-régua (CLAUDE.md §1).

## Ordem proposta (do que não exige arte nova ao que exige)

1. **Cartão de citação com retrato e rótulo grande** (papel rasgado + retrato P&B de domínio público + palavra-chave).
   Só peças do kit; atende o que o Niilismo faz de mais reconhecível. Entra pelo vídeo-régua, uma mudança por vez.
2. **Ícones que se desenham + marcações de caneta** (`DrawPath` + `Marker`), com ícones de biblioteca de licença
   aberta (conferir `video/src/ICONS.md`). Dá o clima de quadro branco sem a mão.
3. **Cartaz-resumo no fim** (os ícones acumulados ou uma tabela comparativa): `compare`/`network` já cobrem parte.
4. **Mão e boneco:** só depois da decisão sobre arte.

## O que isto não prova

Não há dado nosso de que animação aumente retenção. O Estoicismo do Epifania tem 7,86 mi views num canal de 1,81 mi
inscritos, em 2019: as views medem assunto e tamanho do canal tanto quanto forma. Tratar como hipótese a testar:
mesma pauta e mesmo molde, mudando só o visual, medindo percentual médio assistido em D7. Com 2 inscritos no canal, a
medida só vale com distribuição comparável.

---

# Parte 2: dois vídeos recentes do Epifania (setembro e agosto de 2026)

Pedido do dono: ver vídeos recentes para ter parâmetros melhores (a Parte 1 só tinha folhas de quadros de 2019 e 2021).
O download do vídeo foi recusado pelo dono; a análise veio do `vidiq_video_watch` (25 créditos cada, 50 no total).
**É a descrição de um modelo do vidIQ, não quadro a quadro conferido por mim.** Nomes e timestamps podem ter erro e
não foram verificados contra os quadros.

## A Filosofia dos Idiotas (29/09/2026, 17min44s, 704 mil views)

- Traço branco de linha (line art) sobre fundo espacial escuro (nebulosa, estrelas) com brilho neon.
- Filósofos são rostos desenhados em linha branca, **parados, sem mexer a boca**; reaparecem com o mesmo desenho
  (Sócrates, Platão, Aristóteles, Sartre com óculos, Camus com cigarro e outros). Só uma foto real: o professor convidado.
- Técnica: escrita do traço (trim paths) revelando o contorno; quadro a quadro só em mãos, fumaça, líquido e fogo;
  texto com salto de escala e glitch RGB; zooms contínuos e cortes por escala.
- Planos de 1,5 a 3 s; 15 a 25 elementos novos por minuto; mais de 95% ilustração própria. De terceiros: loop de nebulosa
  e a foto do convidado.

## Toda História da Filosofia 2 (11/08/2026, 1h08, 434 mil views)

- Flat design vetorial 2D, cores sólidas, paleta quente. Cada pensador é um **personagem de recorte** (cabeça, braços,
  boca e sobrancelhas como peças que giram e se movem), com o mesmo desenho e a mesma roupa ao longo do vídeo.
- Poses e expressões variam; a boca alterna aberta/fechada, **sem sincronia labial**.
- Câmera com zoom lento e pans; texto com impacto e brilho; transições por forma deslizando, portas, janela e vidro
  quebrando.
- Planos de 3 a 7 s; 10 a 18 elementos novos por minuto; 100% ilustração própria, inclusive quadros famosos
  redesenhados em vetor (Delacroix).

## O que isso muda para o nosso pipeline

1. **Ninguém usa foto do filósofo.** Os dois redesenham tudo no estilo do canal. Foto de terceiros não é o caminho.
2. **O estilo da Filosofia dos Idiotas é o mais factível:** rosto em linha, parado, revelado por traçado, com brilho,
   sobre fundo escuro. Casa com `DrawPath` (escrita do traço) e `Marker` do kit 0.7.1, e fundo escuro com partículas.
   O estilo recortado da Toda História exige uma pele de sprites por personagem (`Host`), com arte por pensador.
3. **O maior abismo é a densidade, não o personagem:** 10 a 25 elementos originais por minuto contra os 4 a 7 por
   minuto do nosso padrão (20 a 35 entradas visuais em 5 a 7 min, CLAUDE.md §9). Arte original nessa quantidade é o custo real.
4. **Caminho de custo menor:** um elenco fixo de pensadores recorrentes, desenhado uma vez e reaproveitado entre
   episódios (a Toda História também reutiliza o mesmo desenho). A fonte do desenho tem de ser domínio público
   (gravura, pintura) ou arte original; redesenhar foto protegida (Sartre, Camus) é derivar de obra com direito autoral.
5. **Limite de verificação:** falta conferir os quadros. Para isso preciso de uns 12 quadros nos timestamps citados
   (ex.: 06:09 e 07:14 da Filosofia dos Idiotas), por download autorizado do dono ou prints dele.

---

# Parte 3: componentes necessários, lacuna principal e se vale agora

## Os hits reproduzíveis de 2026 na nossa amostra não são animados

A amostra de 41 vídeos tem 27 de 2025–2026 (15 de 2025, 12 de 2026); o Epifania, na Parte 1, era de 2019 e 2021.
Os vídeos reproduzíveis de 2026 com mais de 400 mil views usam **imagem parada com zoom**
(`movimento = parado_zoom` em `classificacao.tsv`): A Psique (843 mil, 15/03/2026, pintura em 100% dos quadros),
A Odisseia Interior (729 mil, 05/03/2026, e 407 mil, 10/07/2026, ilustração própria + pintura) e Conexão Psíquica
(532 mil, 19/03/2026). O Epifania, o mais animado, teve 704 mil e 434 mil nos dois vídeos recentes analisados
(breakout 3,1x e 1,9x do próprio canal, bem abaixo dos 12,4x do Cinismo, de 2020). Conclusão: **animação não
é pré-requisito para 400–800 mil views neste nicho em 2026**; é um diferencial caro. Views medem assunto e tamanho
do canal tanto quanto forma.

## Componentes

| Situação | Peças |
|---|---|
| Já no template do longo | `ArchivalPhoto`, `CameraRig` (zoom em imagem parada), `DocumentPage`, `KineticHeadline`, `Host` |
| No kit 0.7.1, sem uso no template | `DrawPath` (escrita do traço; **não tem glow como prop**, daria por `style`/filtro CSS, não verificado), `Marker`, `PaperPiece`/`EdgeClip`/`Tape`, `StyleImage` (`ink`, `mono`, `duotone`), `CutoutPortrait`, `Highlighter`, `CameraPath`, `Stepped`, `Distress`, `GlitchText`/`NeonText`, `Particles`/`SceneBackground` (fundo cósmico), `LottieAsset`, `Host` com pele de sprites |
| Falta | (1) **arte original em volume**: elenco de pensadores em traço, ícones e metáforas, com registro de licença; (2) **caminho de imagem para SVG**: o `DrawPath` recebe o contorno como dado (`d`), e hoje não há etapa que converta um retrato de domínio público em contorno (ferramenta nova = dependência a justificar); (3) **tipos de plano no schema e no template** (retrato em traço, ícone que se desenha, cartão de citação em papel): muda contrato, pede ADR e vídeo-régua; (4) **planejamento de densidade**: planos de 2–4 s e 10–25 elementos por minuto contra 4–7 hoje; (5) animações quadro a quadro (mão, fumaça): Lottie ou sprites, último da fila |

## Lacuna principal

É a **cadeia de arte original**, itens 1 e 2: o kit já tem quase todos os mecanismos de animação, e o que não existe é o
desenho dos personagens e o caminho de produzi-lo com licença registrada. O item 3 vem logo depois (sem tipo de plano
no schema, nada do kit chega ao vídeo longo).

## Vale agora?

Sim, em etapas: o que já rende hoje é imagem parada com zoom bem feita (pintura de domínio público e ilustração
própria), que é o que os hits reproduzíveis de 2026 fazem. O traço animado entra como diferencial depois do teste de
viabilidade do item 2 (um retrato de domínio público virando contorno e sendo escrito pelo `DrawPath`).

---

# Parte 4 (2026-11-02): densidade medida por minuto e lacunas com caminho

## Correção da Parte 2

A Parte 2 dizia "planos de 1,5 a 3 s" e "15 a 25 elementos novos por minuto". Uma segunda análise do vidIQ, pedida
com contagem por minuto, de "A Filosofia dos Idiotas" (RTkg6coVWEk), deu outros números:

| Métrica (estimativa de olho, vidIQ) | Passada 1 (Parte 2) | Passada 2 (minuto a minuto) |
|---|---|---|
| Duração média do plano | 1,5 a 3 s | ~8,7 s (de 7,5 a 11 s por minuto) |
| Cortes por minuto | não informado | ~6,7 (de 4 a 8) |
| Elementos | 15–25 "novos" por minuto | ~16,7 "distintos" na tela por minuto (máx. ~22) |
| Personagens na tela | não informado | ~3,3 por minuto (máx. ~8) |
| Textos na tela | não informado | ~6,5 por minuto (máx. ~9) |

**As duas passadas discordam, e nenhuma é medição.** Elas são estimativas do modelo, sem quadro conferido por mim.
A medida que decide é a contagem em quadros, que só sai com o arquivo do vídeo ou com prints do dono. Até lá, a
afirmação segura é: **o Epifania corta cerca de 6 a 7 vezes por minuto, com cerca de 2,5 elementos distintos por corte.**

## O que isso muda na comparação com o nosso padrão

- **Cortes por minuto:** nosso padrão é de 4 a 7 entradas visuais por minuto (20 a 35 em 5 a 7 min, CLAUDE.md §9).
  Os 6 a 7 cortes do Epifania ficam **dentro da mesma faixa**. A diferença de densidade **não é de número de cortes**.
- **Elementos por corte:** nosso plano tem **um** visual. O Epifania empilha ~2,5 (fundo, personagem, texto, ícone).
  Esse é o gap de densidade real: **camadas dentro de um plano**.
- **Texto:** o Epifania põe 6 a 9 textos por minuto na tela. Nosso `keyword` e `lower_third` cobrem isso só em parte.
- **Personagens:** 2 a 8 por minuto, não um só. Isso só faz sentido com elenco recorrente (ver lacuna K).

## Lacunas, com caminho e dificuldade

| # | Lacuna | O que já existe | Como fazer | Dificuldade |
|---|---|---|---|---|
| A | **Camadas num plano** (fundo + personagem + texto + ícone) | Template com um visual por plano; kit tem `Pane`, `SplitScreen`, `ParallaxLayer`, `FloatingWindow` | Plano composto no schema (lista de camadas) e montagem no template. Muda contrato: ADR + vídeo-régua | Média |
| B | **Texto com efeito** (neon, glitch, palavra grande) | `NeonText`, `GlitchText`, `KineticHeadline` (já no template) | Usar no template com tema escuro; sem arte nova | Fácil |
| C | **Fundo cósmico/textura** | `SceneBackground`, `Particles`, `MeshGradient` | Só código; muda a identidade visual: passa pelo vídeo-régua | Fácil |
| D | **Retrato em traço a partir de domínio público** | `DrawPath` (escreve o caminho); não há conversão de imagem para contorno | Teste: gravura ou pintura de domínio público → contorno (OpenCV, Apache-2) → `DrawPath`. Dependência nova: justificar | Média |
| E | **Traço que se desenha** (escrita, sublinhado, seta) | `DrawPath`, `Marker` (no kit 0.7.1, sem uso no template) | Plano novo `sketch` (`DrawPath` + `Marker`) | Média |
| F | **Personagem recortado com partes móveis** (Toda História) | `CutoutPortrait`, `Host` com pele de sprites | Precisa de uma imagem por parte (cabeça, braço, boca) por pensador: recorte manual. Arte em volume | Alta |
| G | **Mão que desenha** | Nada | Sprite de mão seguindo o `DrawPath`. Arte com licença (ou desenho próprio simples) | Média (arte) |
| H | **Movimento da boca (sincronia labial)** | `PixelHost` tem visemas, mas não é o estilo | **Não é lacuna a fechar**: nem o Epifania nem a Toda História sincronizam a boca | — |
| I | **Quadro a quadro** (fumaça, líquido, mão) | `Stepped`, `LottieAsset` | Lottie com licença verificada, ou sprites por quadro | Média |
| J | **Câmera (zoom, pan)** | `CameraRig`, `CameraPath` (já no template: `CameraRig`) | Usar mais | Fácil |
| K | **Elenco recorrente de pensadores** | `Host` de sprites com pele | Desenhar uma vez por pensador (PD ou arte própria) e reusar. Maior custo de arte | Alta (arte) |
| L | **Densidade de planos** (4–7 por minuto hoje) | `vp check` avisa por molde | Não exige mudar o número de cortes; exige A (camadas) | Média |

## Como fazer, em ordem

1. **Agora, sem arte nova e sem mudar o contrato:** B e J (texto com efeito e câmera). Só mudam o tratamento visual de
   planos que já existem. Passam pelo vídeo-régua, uma mudança por vez.
2. **Teste de viabilidade do traço (D + E):** uma gravura de domínio público de um pensador → contorno → `DrawPath`,
   em um plano de teste, sem publicar. Responde se a conversão imagem→traço fica boa o bastante. Precisa de sua aprovação
   para a dependência de visão computacional e de um render de teste (sonda de CPU antes, CLAUDE.md §3).
3. **Camadas (A):** só depois do teste D+E, porque a camada precisa de um tipo de elemento que o template ainda não tem.
   Pede ADR.
4. **Arte (F, G, K):** só com decisão sua sobre quem desenha e sob qual licença. O caminho de custo menor é elenco
   fixo de poucos pensadores em domínio público, reusado entre episódios.
5. **Não fazer:** H (sincronia labial). Nem o modelo de referência usa.

## Possibilidade, em uma frase

As peças de movimento já estão no kit. O que falta é (1) o plano com camadas e (2) arte de personagem com licença.
Sem a arte, dá para chegar a um visual parecido com o Epifania na parte de texto, câmera e fundo, mas não no traço
de personagens.

## Lacuna do método

Frame a frame ainda não foi feito. Para medir, é preciso o arquivo do vídeo (download de baixa resolução, que você
recusou antes) ou prints de alguns quadros. Sem isso, a densidade acima é estimativa do modelo, e a comparação com o
Epifania fica como hipótese.

---

# Parte 5 (2026-11-02): quadros reais de "A Filosofia dos Idiotas" (RTkg6coVWEk)

Método: a skill `analise-de-formato` (download em 360p, `medir.py`, `folha_densa.py`, `decupagem.py`), mais um quadro a
cada 10 s do vídeo inteiro (106 quadros, em folhas de 20). Pasta: `data/cache/nicho/Epifania-animacao/` (fora do Git).
A contagem é **minha leitura visual** das miniaturas de 480×270, não de quadros em tamanho cheio. Ícones pequenos
e textos finos podem estar subcontados.

## Por que o script não conta a animação

`medir.py` conta 2,0 cortes por minuto neste vídeo, e o vidIQ estimava 6,7. Não é divergência de dados: o script só
conta corte seco (limiar 0,3). Traço que se desenha, zoom lento e troca de elemento dentro do quadro não entram. O
`decupagem.py` achou 22 cenas em 17,7 min, com algumas de mais de 4 min. Para animação, o número que importa é
elementos por quadro, e isso só sai de amostragem fixa.

## Elementos visíveis por quadro (amostra de 10 s)

| Trecho | Quadros | Elementos médios por quadro | Observação |
|---|---|---|---|
| 0:00–3:20 | 20 | ~2,5 | logo, Sócrates, livros, mapa, linha do tempo; alguns quadros vazios |
| 3:20–6:40 | 20 | ~2,2 | Einstein, Descartes, Marx; texto com efeito neon; copo com camadas |
| 6:40–10:00 | 20 | ~1,7 | Sócrates, mãos, cerca com animais, rótulos "IDIOTA" |
| 10:00–13:20 | 20 | ~2,3 | pódios, perguntas em balão, linhas manuscritas; propaganda do curso começa ~11:40 |
| 13:20–16:40 | 20 | ~2,5 | grupo de rostos (8 a 10 elementos), ícones em círculo, cartão de preço |
| 16:40–17:44 | 6 | ~1,5 | fim da propaganda: relógio em contagem, código de defesa do consumidor |

**Média geral: cerca de 2,2 elementos por quadro.** Picos de 5 a 10 em listas de rostos, grupos de pessoas e
ícones. Metade dos quadros tem texto na tela.

## Variedade de componentes (contados nos 106 quadros)

Pelo menos 14 tipos distintos: traço branco de personagem (com e sem contorno), texto neon com brilho, texto
manuscrito (fonte de caligrafia), mapa em linha, livro ou pergaminho em linha, logo com glow, balão de fala, texto
em vermelho desenhado à mão, rede de nós e arestas, interface de vídeo ou comentário, ícones em círculo, relógio,
fotografia real (o professor convidado), cartão de preço, mãos em linha.

## O que isso confirma e corrige

1. **Confirma o gap de camadas:** cada quadro do Epifania tem ~2,2 elementos. Nosso plano tem um. Isso já estava na
   Parte 4 e agora está medido em quadros.
2. **Corrige a densidade de cortes:** o número de cortes não é o gap. Cortes ficam perto de 6 a 7 por minuto nos dois
   lados; o que muda é a quantidade de elementos dentro do quadro.
3. **Mostra um detalhe que não copiamos:** cerca de 40% do vídeo (a partir de ~11:40) é propaganda de um curso pago do
   próprio canal. Não entra em nenhuma comparação de formato, nem como "ritmo do nicho".

## Próximo passo, se você autorizar

- Amostragem igual no vídeo de 2025 (`HvWsUDbAAgs`) e no de 1h08 (`WEe6L5HVMwk`), que já estão baixados.
- Quadros em tamanho cheio nos trechos com mais elementos (copo, rostos, rede), para confirmar a contagem.
- Medir a mesma coisa no nosso `episode.json` (planos por minuto e elementos por plano), para comparar com números
  e não com estimativas.

---

# Parte 6 (2026-11-02): os três vídeos contados da mesma forma

Método: um quadro a cada 10 s no vídeo de 2025 (13 min, 80 quadros) e no de 2026 (106 quadros), e a cada 30 s no de
1h08 (137 quadros). Folhas em `data/cache/nicho/Epifania-animacao/quadros/`. A contagem é **minha leitura visual** de
miniaturas de 480×270, por bloco de 200 s (ou 600 s no de 1h08). Não é medida exata.

## Resultado

| Vídeo | Quadros | Elementos por quadro (média) | Tipos distintos | Estilo |
|---|---|---|---|---|
| A Filosofia dos Idiotas (2026, 17,7 min) | 106 | ~2,2 | ~14 | traço branco sobre fundo escuro, neon, texto manuscrito |
| Toda História da Filosofia 2 (2026, 1h08) | 137 | ~3,0 | ~8 | flat design em tons quentes; personagens recorrentes; texto grande |
| O mito de Sísifo digital (2025, 13,3 min) | 80 | ~2,1 | ~10 | flat amarelo; barras de progresso, fotos reais de podcast e Senado, prints de comentários |

## O que os números mostram

1. **O vídeo mais longo tem mais elementos por quadro, mas menos tipos.** Na Toda História, o mesmo personagem reaparece
   em poses diferentes, e isso conta como elemento. Ou seja: **elenco recorrente é o que dá densidade barata.** Com um
   elenco fixo, cada quadro tem personagem, fundo e texto sem precisar de arte nova a cada minuto.
2. **O de 2025 usa foto real e print de tela.** Fotos de podcast, de audiência pública e de comentários do YouTube
   aparecem em vários quadros. Isso é uso de material de terceiros, e não entra no nosso padrão (CLAUDE.md §2.3 e §2.4).
3. **O de 2026 é o único com efeito de texto neon e traço que se desenha**, e também o que tem mais propaganda do
   próprio canal (cerca de 40% do tempo, a partir de 11:40, não contada acima).
4. **Nenhum dos três tem sincronia de boca** (já registrado na Parte 2). Não é lacuna a fechar.
5. **Em nenhum dos três quadros se vê a mão que desenha** no 2025 e no 1h08. A mão só aparece no de 2026, em
   trechos de escrita.

## Comparação com o nosso padrão

Nosso plano tem, por desenho, **um visual por plano** (ADR 001 e 008). Por isso a nossa média é perto de 1 elemento por
quadro, sem medir ainda os nossos episódios: falta rodar a mesma contagem sobre um `episode.json` (ou sobre o render),
para ter número contra número. A lacuna que aparece de forma consistente nos três vídeos é a **camada**: texto, fundo e
personagem juntos no mesmo quadro.

## Ressalvas

- Contagem por olho de miniaturas, não de quadros em tamanho cheio. Ícones pequenos ficam subcontados.
- Amostragem de 10 s (ou 30 s no de 1h08): transições rápidas e trechos de 1 ou 2 s não entram.
- O script de cortes (`medir.py`) não serve para essa comparação: conta corte seco, e esses três vídeos são animação
  contínua. Os números de cortes da Parte 5 estão nessa limitação.
- Três vídeos de um único canal. Não é amostra do nicho.
