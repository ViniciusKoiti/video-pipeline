# 056 — Apresentador por cena no vídeo longo

- **Status:** proposta (2026-11-09). Implementada no código, a confirmar pelo dono; nenhum vídeo foi renderizado.
- **Data:** 2026-11-09
- **Etapa do roadmap:** frente do apresentador (continuação das ADRs 013 e 017)
- **Relaciona-se com:** ADR 013 (apresentador em janela), ADR 017 (pele `dono`), ADR 029 (pele em camadas e direção
  automática), ADR 037, 038 e 045 (layout de modelos, constantes e erros); precedente: `scene.host === false` no
  `motion-video` dos Shorts (`HOST_HIDDEN_TYPES`)

## Contexto

Pedido do dono (2026-11-09): usar a pele `dono` nos vídeos longos "entrando às vezes", para o vídeo ficar mais vivo.
Hoje o `host` é do episódio inteiro: `HostSpec` em `scenes.json` e `episode.json`, e o motor
(`app/render/remotion.py`) põe as props `host` em **todas** as cenas, com o canto girando em sentido horário
(`app/media/host.py`). Por cena só existe `host_corner`, que ajusta o canto. Não há como pôr o apresentador só em
algumas cenas.

`episode.json` é contrato (CLAUDE.md §6): mudar exige ADR. Dois cuidados pesam mais que o desenho:

- Quem não usa o campo novo não pode notar: as props de cada cena, o cache do Remotion (que é por props) e o
  `input_hash` ficam como estão. O `episode.json` também não pode mudar de bytes: o gate 4 carimba esse arquivo e
  recusa regravá-lo diferente.
- O template (`video/src/*.tsx`) não muda: qualquer mudança nele troca o `template_hash` e refaz todas as cenas de
  todos os vídeos.

## Opções consideradas

1. **Só um campo por cena (`host: true | false`), sem modo.** Para o uso "só às vezes" seria preciso marcar
   `host: false` em todas as outras cenas (12 de 14, por exemplo), e o padrão do episódio ficaria implícito.
2. **Só um modo no `HostSpec`, com a lista de cenas lá dentro** (`"scenes": ["S03", "S07"]`). Concentra a decisão,
   mas duplica ids, quebra quando uma cena é renomeada ou reordenada e fica longe da cena que o roteirista está
   escrevendo.
3. **Inferir o modo: se alguma cena tem `host: true`, as sem marca ficam sem apresentador.** Mínimo de campos, mas
   mágico: acrescentar uma marca muda todas as outras cenas.
4. **Um campo por cena e um modo no `HostSpec`** (escolhida). A marca fica na cena; o modo diz o padrão das cenas sem
   marca.

## Decisão

- **Contrato (campos opcionais, sem mudar `schema_version`).**
  - `HostSpec.show`: `"all"` (padrão) ou `"marked"`. `all` é o comportamento de sempre; `marked` só mostra o
    apresentador nas cenas marcadas `host: true`.
  - `Scene.host` (`scenes.json`) e `EpisodeScene.host` (`episode.json`): `true | false | ausente`. A marca da cena vale;
    sem ela vale o `show`. Regra única, em `HostSpec.shows(marca)`: `marca` se existe, senão `show == "all"`.
  - Uso "às vezes": `"host": {"skin": "dono", "show": "marked"}` e `"host": true` só nas cenas em que ele entra. As
    outras não levam campo nenhum. `host: false` serve para tirá-lo de uma cena no modo `all`.
  - `episode_build.build_scenes` copia `host` do roteiro para o `episode.json`, como já faz com `host_corner` e
    `delivery`.
- **Serialização que não muda o que já existe.** O `episode.json` só ganha `host` na cena quando ela tem marca, e
  `show` no `host` só quando é `marked`; os dois ficam de fora do JSON no valor padrão (serializador de modelo).
  Episódio sem o campo novo grava os mesmos bytes de antes.
- **Validação (`vp check` e leitura dos dois arquivos).** Erro, na leitura do `scenes.json` e do `episode.json`:
  - `host_corner` numa cena com `host: false`;
  - cena com `host: true` num episódio sem `host`;
  - `show: "marked"` sem nenhuma cena `host: true` (o apresentador não apareceria);
  - todas as cenas `host: false` com `show: "all"`.
  `host: false` num episódio sem `host` não diz nada e passa. A regra mora em `host_problems`
  (`app/pipeline/models/_schemas_types.py`), ao lado de `portrait_problems`.
- **Cantos.** `host_corners` não muda. O motor (`app/media/host_scenes.py`, `scene_corners`) a aplica **só às cenas
  que mostram o apresentador**: o sentido horário vale entre elas, e cena sem apresentador não ocupa nem reserva
  canto. Sem marcas e com `show: "all"`, é a lista de antes.
- **Render.** Nas cenas sem apresentador as props não têm `host`, e o `Scene.tsx` já só desenha a janela quando a
  prop existe: **nada muda em `video/`**. A primeira cena com apresentador depois de uma sem ele tem
  `fromCorner: null`, e a janela **entra** (o `HostWindow` já faz isso na primeira cena); entre cenas seguidas com
  apresentador ela é arrastada do canto anterior, como hoje. A boca (WAV) só é medida onde há apresentador.
  A montagem das props do apresentador saiu de `remotion.py` para `app/media/host_scenes.py` (o arquivo está na
  baseline do gate de tamanho e só pode encolher).
- **Fora desta ADR:** escolher automaticamente em quais cenas ele entra (decisão do roteirista ou do dono, na
  partitura ou no roteiro); janela entrando e saindo com animação própria no corte (hoje a saída é o corte da
  cena, como em todo o resto, e a entrada é a de `HostWindow`); o `host` no `motion-video` dos Shorts, que já tem
  o seu; perfil de cantos diferente por pele.

## Consequências

- **Compatibilidade:** episódio sem `show` nem `host` por cena renderiza com as mesmas props por cena, a mesma
  chave de cache do Remotion e o mesmo `episode.json`; `video/` e o `template_hash` não mudam. Testes em
  `tests/test_host_per_scene.py` (props iguais com `all` e com todas as cenas marcadas, JSON sem as chaves novas,
  corte, cantos, `vp check`).
- **Gate 2:** `host` é campo do `scenes.json`, que o gate 2 carimba por bytes. Marcar cenas num roteiro já
  aprovado pede `vp reopen --step script` (ADR 039); o `asset_id` continua a única exceção do carimbo.
- **Cache:** num vídeo já renderizado com `show: all`, passar a `marked` refaz só as cenas que perdem o apresentador
  (as props mudam); as que o mantêm refazem se o canto mudar, porque o sentido horário passa a contar só as cenas
  com ele.
- **Pele `dono`:** o `sprites_hash` entra só nas props das cenas com apresentador; um episódio `marked` sem nenhuma
  cena marcada é erro, então a conferência da pasta de sprites não corre à toa.
- **Dúvida registrada:** o nome `show` e os valores `all` e `marked` são a escolha mais curta que achei; se o dono
  preferir `appears` ou `scenes`, é só renomear. Também não decidi se `host: false` sem `host` no episódio deve ser
  erro; ficou como inócuo para não punir quem remove o apresentador e deixa as marcas de saída.
