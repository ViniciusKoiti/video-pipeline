# Brief: qual estilo visual combina com cada vertical, e em quais verticais dá para atuar

Pasta do conselho: `/tmp/claude-1000/-home-viniciusk-projetos-auto-play/7494f80d-4e24-49a2-aa6f-11dbb3bce8e8/scratchpad/council/estilos-por-vertical/`.

## 1. Pergunta

O projeto produz vídeos animados narrados (Remotion e `@viniciusk/motion-kit`) para várias **verticais**. O dono tem uma lista de 50 estilos visuais e quer saber **qual combina com cada vertical**, para ver **em quais verticais o projeto pode atuar**. Responda:

1. Para **cada uma das 10 verticais** de `verticais.md`: os **3 estilos** da lista de `estilos.md` que combinam mais (em ordem), os **2 a evitar**, e por quê, em uma ou duas linhas. Diga também se o preset de hoje (`editorial`) basta ou deve ser trocado ou complementado.
2. Quais verticais ficam **bem servidas por estilos que dá para produzir agora** (os grupos A e B de `estilos.md`) e quais dependem de um estilo caro, arriscado ou que o projeto não pode produzir.
3. Existe um estilo, ou um par de estilos, que sirva a muitas verticais e reduza o custo de padronizar? Qual seria o conjunto **mínimo** de presets que cobre mais verticais?
4. O que você **não consegue avaliar sem ver um quadro renderizado** ou sem um teste com público?

Escolha só estilos da lista. Se achar que um estilo do grupo C vale a exceção, diga o custo e o risco.

## 2. Evidência (leia os arquivos)

- `estilos.md`: a lista dos 50 estilos, com o que o tema e o kit têm hoje e uma triagem em três grupos (feita pelo coordenador; pode estar errada).
- `verticais.md`: as 10 verticais, com formato, público, conteúdo, tom, risco e a fonte de cada fato.
- Relatórios completos, se quiser aprofundar: `/home/viniciusk/projetos/auto-play/docs/pesquisa/nichos-reels-animados.md`, `.../nichos-globais-2026-10.md`, `.../plataformas-monetizacao-2026-10.md` e as fichas em `.../nichos-globais-anexos/`.
- Regras do projeto: `/home/viniciusk/projetos/auto-play/CLAUDE.md`; ADRs em `.../docs/decisions/` (011, 013, 014); guia de animação de texto em `.../docs/guia-animacao-de-texto.md` (rascunho).
- Template e kit (para checar o que existe): `/home/viniciusk/projetos/auto-play/video/src/` e `/home/viniciusk/projetos/motion-kit/src/` (`theme/`, `fx/`, `motion/`, `pixel/`, `three/`, `editorial/`, `charts/`, `COMPONENTS.md`).

## 3. Critérios (proposta do coordenador; acrescente ou discorde)

1. **Credibilidade e tom:** o estilo combina com o que o público dessa vertical espera de uma fonte confiável? Um estilo lúdico numa vertical regulada ou séria enfraquece a prova.
2. **Legibilidade** de número, comparação e gráfico, em 9:16 (ou 16:9) e em tela pequena, com legenda queimada.
3. **Viabilidade com o kit e o tema:** grupo A, B ou C; dependência nova; ferramentas que faltam.
4. **Custo de render:** a máquina é limitada e o render conta (blur, 3D e partículas custam mais que formas chapadas).
5. **Licença e ativos:** fontes só com licença registrada (hoje Inter, OFL); nada de ilustração desenhada à mão; imagem só com licença da lista fechada.
6. **Diferenciação** diante de como a vertical costuma se apresentar (evidência fraca: ver abaixo).
7. **Risco de enfraquecer a prova:** decoração sobre fato, contraste baixo, ou conflito com regra de plataforma (por exemplo, a política do YouTube sobre conteúdo "com cara de template").

## 4. Restrições

- Custo zero; um render por vez em máquina limitada; **nenhum render ou clipe de teste neste conselho**.
- Perfil vertical: só os 8 planos de `verticais.md`; a tela não calcula; todo dado na tela tem ficha com fonte.
- Mudar `episode.json` exige uma ADR; um estilo deve ser configuração do template e do tema, não campo novo do contrato, salvo justificativa.
- Fontes e imagens só com licença registrada (lista fechada; sem CC-BY-SA nem NC). Não proponha uma fonte sem dizer que a licença precisa ser conferida.
- Sem pessoa em câmera; apresentador ilustrado opcional.

## 5. Fora de discussão

- Quais verticais são comercialmente melhores: já foram avaliadas (notas em `verticais.md`); aqui só se avalia **estilo × vertical** e a viabilidade de produzir o estilo.
- Copiar a identidade visual de um criador específico.

## 6. Não verificado

- Como os concorrentes de cada vertical **realmente parecem**: nenhum vídeo foi assistido; só há bios, legendas e texto alternativo.
- O gosto do público de cada vertical e qualquer métrica de retenção por estilo.
- O custo de render de cada estilo e a licença de qualquer fonte candidata.
- O que o dono quer: ele pediu "qual combina com cada produto" e ainda não disse se quer uma identidade única ou várias.

## 7. Formato da resposta

Até **650 palavras**. Comece por uma tabela `vertical | top 3 (em ordem) | evitar 2 | editorial basta? | razão`, depois responda as perguntas 2 a 4. Marque [F] o que leu num arquivo, [I] inferência, [H] hipótese.
