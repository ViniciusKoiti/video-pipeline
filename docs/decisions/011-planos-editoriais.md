# 011 — Planos editoriais do explicativo (motion-kit 0.2)

- **Status:** proposto
- **Data:** 2026-09-28
- **Etapa do roadmap:** #69 (sugestões #70–#80); teste num episódio curto
- **Relaciona-se com:** ADR 001 (motor por formato), ADR 007 (licenças), ADR 008 (lista de planos: esta ADR
  acrescenta tipos e campos), ADR 009 (`vp check` e agentes)

## Contexto

A prévia `votorantim-completo-previa` (128 planos) ficou com cara de sequência de cartões: 95 planos gráficos
sobre o mesmo fundo liso, 29 de 47 cenas sem nenhuma imagem e 32 carimbos (25%), muitos usados só para atribuir
a fonte (#69). O motion-kit 0.2.0 (PR #83) trouxe as peças que faltavam: documento com trecho marcado,
comparação, gráficos de linha e de participação, rede que cresce, mapa-múndi com rotas, cronologia em escala
real, frase na tela, tarja, selo de data, fonte no rodapé, foto de arquivo e o tema `editorial`, com as mesmas
cores do template.

Um componente só chega ao vídeo se passar pela cadeia inteira: o roteirista escolhe o plano (skill), o
`scenes.json` o descreve (contrato), o `vp check` confere o que aparece na tela (§2.2), o `episode.json` o leva
ao template e o template chama o componente. Hoje a cadeia só conhece os 10 tipos da ADR 008, e mudar o
`episode.json` exige ADR (CLAUDE.md §6).

## Opções consideradas

1. **Só template.** Os tipos atuais passam a usar as peças do kit (tarja, selo, foto de arquivo, hodômetro,
   cronologia). Barato e sem mudar o contrato, mas o roteiro continua sem documento, comparação, rede e frase
   na tela, e os carimbos de atribuição ficam.
2. **Tipos e campos novos no contrato, só acrescentando (escolhida).** Os episódios existentes continuam
   válidos, o roteirista ganha os planos que faltam e o `vp check` confere cada um.
3. **Um plano genérico "componente + props".** Flexível, mas o agente passaria a escrever props visuais
   livres (ícone, cor, logo), e o `vp check` não saberia o que é afirmação na tela. Descartada.

## Decisão

1. **Só acréscimos; `schema_version` continua 2.** Nenhum campo existente muda de sentido e os campos novos
   têm padrão. Tudo o que aparece na tela e afirma algo exige `claims` (§2.2), como na ADR 008.

2. **Tipos novos**

   | Tipo | Campos | Componente do kit | Afirmação na tela |
   |---|---|---|---|
   | `compare` | `left` e `right` (`value`, `label`); `mode`: `side` \| `before_after` \| `scale`; `emphasis?`: `left` \| `right` | `ValueCompare` | `claims` obrigatórias |
   | `network` | `root`; `nodes` (`id`, `label`, `role?`, `kind`); `edges` (`from`, `to`, `label?`, `value?`, `style`: `solid` \| `dashed`, `flow`, `claims`); `steps` (`anchor`, `nodes`, `highlight?`); `layout`: `radial` \| `layered` | `ExpandingNetwork` | `claims` no plano **e em cada aresta** |
   | `keyword` | `text` (até 8 palavras); `highlight?` | `KineticHeadline` | o texto é cópia literal da narração da cena, já coberta pelas `claims` da cena |

   - `compare.value` segue a regra do `number`: o texto como aparece na tela ("69 mil", "R$ 47,6 bi"). O
     template separa prefixo, número e sufixo para o hodômetro. `emphasis` só muda o peso da fonte; o outro
     lado não apaga.
   - `network`: `kind` do nó é `person`, `family`, `company`, `bank`, `government` ou `other`. **O ícone vem do
     `kind`, no template**: o roteiro não escolhe ícone, cor nem logo. `label` e `role` dos nós são cobertos
     pelas `claims` do plano; cada relação (aresta) tem as suas.
   - `network.steps[].anchor` é trecho literal da narração, em ordem, depois da âncora do plano: a rede cresce
     e a câmera se afasta no ritmo da fala. No `episode.json`, cada passo ganha o tempo relativo ao plano,
     calculado como o dos planos (posição da âncora sobre a duração real do WAV, `app/pipeline/shots.py`).

3. **Campos novos em tipos existentes**

   | Tipo | Campo novo | Componente | Regra |
   |---|---|---|---|
   | `chart` | `type`: `bar` \| `bar_horizontal` \| `line` \| `share` (padrão `bar`); `highlight?` (rótulo de um ponto); `y_from_zero` (só `line`, padrão `true`); `rest?` (rótulo do que sobra, só `share`) | `BarChart`, `LineChart`, `ShareChart` | sem `highlight`, nenhum ponto em destaque; em `line`, os rótulos são anos (`1927`) ou datas ISO |
   | `quote` | `style: "document"`, com `document` (`title`, `issuer?`, `date?`) e `variant`: `report` \| `newspaper` \| `letter` | `DocumentPage` | `headline` passa a usar a página de jornal, com `document` opcional |
   | `map` | `scope`: `region` \| `world` (padrão `region`); `highlight` (códigos de país ou de estado); `routes` (`from`, `to`: nomes de `places`) | `GeoMap` | com `highlight` ou `routes`, `claims` obrigatórias |
   | `timeline` | `when` em cada evento (ano ou data ISO) | `YearTimeline` | com `when` em todos os eventos, escala proporcional; senão, espaçamento igual. `date` continua sendo o texto na tela |

4. **Sem mudança no contrato, com peça do kit no template:**
   - `photo` de arquivo (`historical_exact`) → `ArchivalPhoto`;
   - `photo` de banco ou ilustração → `ImageBackground`, e `broll` → `FootageBackground`, os dois sóbrios;
   - `number` → `Odometer` (texto que não for reconhecido como número fica estático);
   - `lower_third` → `LowerThird`;
   - `stamp` → `DateStamp`: no canto quando há mídia na cena, grande quando não há;
   - `family_tree` continua com o componente do template.

   Tudo fica dentro do `MotionThemeProvider` com o preset `editorial`.

5. **Camadas no template** (generaliza a emenda da ADR 008). Foto ou B-roll continua por baixo dos planos
   seguintes da cena até a próxima mídia (#70). Por cima dela entram `lower_third`, `stamp`, `number` e
   `keyword`. Em tela cheia, sobre o fundo do tema, ficam `chart`, `compare`, `quote`, `network`, `map`,
   `timeline` e `family_tree`. A legenda some enquanto um `keyword` está na tela.

6. **Fonte no rodapé, sem campo no roteiro (#74).** Na montagem do `episode.json`, cada plano com `claims`
   ganha `source` (texto) e `source_flag`, derivados do `sources.json` **sem editá-lo** (editar derrubaria o
   gate 1):
   - com `authors`: os sobrenomes (o que vem antes da vírgula), "A e B" para dois, "A e outros" para três ou mais;
   - sem `authors`: o `title` até o primeiro " — ", com no máximo 60 caracteres;
   - fontes com os mesmos autores viram um rótulo só; no máximo dois rótulos por plano, separados por "; ";
   - `Source.interested` → `source_flag: "fonte interessada"`.

   O template mostra com o `SourceTag`. O crédito da foto continua vindo do ativo.

7. **A tela não calcula.** Razão, variação percentual e soma só aparecem se estiverem numa ficha. O
   `ValueCompare` roda com `showRatio` desligado, e o template nunca converte moeda nem corrige valor.

8. **`vp check`, erros novos:**
   - `quote`, em qualquer estilo: `text` literal num dos trechos citados, com a mesma regra das fichas
     (`quote_in_excerpt`: cortes com "..." ou "[...]", partes em ordem);
   - `keyword`: `text` literal na narração da cena, e `highlight` dentro do `text`;
   - `compare` com `mode: "scale"`: os dois valores reconhecidos como número, com o mesmo prefixo e sufixo
     (mesma unidade);
   - `network`: ids únicos; arestas e passos só com nós existentes; `root` existente; todo nó é a raiz ou entra
     em algum passo; cada aresta com `claims`; âncoras dos passos em ordem na narração;
   - `chart`: `highlight` é um dos rótulos; `line` só com anos ou datas; `share` sem valor negativo;
   - `map`: `routes` só entre `places` do plano; códigos de `highlight` existentes nos contornos do template;
   - `timeline`: quando `date` tem um ano de quatro dígitos, `when` tem o mesmo ano.

9. **`vp check`, alertas (#75)**, que não bloqueiam:
   - mais de 4 planos gráficos seguidos sem mídia;
   - `stamp` em mais de 10% dos planos;
   - `lower_third` sem mídia antes, na mesma cena;
   - o mesmo tipo duas vezes seguidas;
   - `chart`, `compare`, `network`, `timeline` e `quote` com `document` com menos de 4 s;
   - `chart` de barras com 2 pontos (use `compare`);
   - mais de um `keyword` por cena.

10. **Ícones:** Lucide (`react-icons/lu`, licença ISC), um ícone fixo por `kind` de nó, com a licença
    registrada em `video/src/` como a da fonte Inter. Font Awesome (CC BY 4.0, exige crédito) e Simple Icons
    (marcas) ficam de fora.

11. **Fora desta ADR:** retrato recortado (#82: dependência e direito de derivar em aberto), trilha e efeitos
    (#81), relação de afinidade na árvore da família, várias séries e anotações no gráfico de linha, tempo por
    palavra vindo do alinhamento (#17).

## Consequências

- **Etapas, um PR cada:**
  1. **Contrato:** `schemas.py`, `video/src/types.ts`, `source`/`source_flag` e tempo dos passos no
     `episode.json`, erros e alertas do `vp check`, testes.
  2. **Template:** tema `editorial`, peça do kit por tipo, camadas, câmera e transições (#70–#72), contornos
     do mundo (Natural Earth, domínio público) e ícones; conferência em quadros parados.
  3. **Skills:** tabela de escolha no `roteiro-explicativo` (dois números comparados → `compare`; série no
     tempo → `chart` `line`; parte de um todo → `chart` `share`; relação entre pessoas e instituições →
     `network`; frase de documento → `quote` `document`; data que é o ponto da frase → `stamp`; a fonte vai
     para o rodapé sozinha) e os tipos novos na `checagem`.
  4. **Episódio de teste** de cerca de 90 s, reaproveitando as fontes e fichas do `votorantim-completo`, com
     cada tipo novo pelo menos uma vez.
- O `vp check` passa a conferir a citação literal dos `quote` que já existem, e roteiros aprovados podem
  mostrar erros novos. A aprovação não cai por isso (ela depende do hash do conteúdo), mas o erro aparece.
- `CLAUDE.md` §6 (lista de tipos de plano) muda quando esta ADR for aceita.
- Fica mais difícil: o roteirista tem mais tipos para escolher. A tabela da skill e os alertas do `vp check`
  seguram a escolha, e o gate 2 continua decidindo.
