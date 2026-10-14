# 011 — Planos editoriais do explicativo (motion-kit 0.2)

- **Status:** aceito (2026-09-28)
- **Data:** 2026-09-28
- **Etapa do roadmap:** #69 (sugestões #70–#80); teste num episódio curto
- **Relaciona-se com:** ADR 001 (motor por formato), ADR 007 (licenças), ADR 008 (lista de planos: esta ADR
  acrescenta tipos e campos), ADR 009 (`vp check` e agentes)

O dono aceitou em 2026-09-28 as recomendações dos quatro pontos em aberto: a tela não calcula razão nem
variação (decisão 7), `y_from_zero` ligado por padrão (decisão 3), ícones Lucide (decisão 10) e os limites
dos alertas (decisão 9).

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
   `timeline` e `family_tree`. ~~A legenda some enquanto um `keyword` está na tela.~~ Emendada pela ADR 021
   (2026-10-14): a legenda fica visível junto com o `keyword`.

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
   *Ressalva de 2026-10-14 (ADR 020):* a conta dita inteira na narração, com insumos e regra em fichas, pode
   mostrar o resultado; o template continua sem calcular.

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

## Emenda de 2026-09-29: texto que cabe na tela

**Contexto.** No vídeo-régua (`votorantim-dinheiro`), três defeitos vieram de texto maior que a peça:
- o valor da seta da rede ficou atrás do nome de um nó de duas linhas (corrigido no template, #92);
- o texto de um número sobre a foto ocupou duas linhas, e o painel cresceu por cima do crédito da foto;
- a linha do tempo tinha texto demais para o tempo do plano.

Nada avisava antes do render.

**Decisão.** O `vp check` ganha alertas de texto que não cabe (`app/pipeline/text_fit.py`). São alertas, não erros, como os da decisão 9: a revisão humana decide.
- Cada limite é a largura da caixa no template e no motion-kit dividida pela largura média de um caractere da Inter. Os valores foram conferidos nos quadros da v3 do vídeo-régua.
- Número sobre a imagem: 1 linha. Em tela cheia: 2 linhas.
- Comparação: 2 linhas por lado.
- Tarja: nome em 1 linha, cargo em 2.
- Evento da linha do tempo: 3 linhas.
- Nó da rede de onde sai uma seta: nome e papel em 2 linhas. Nas camadas, o nó sem seta saindo fica de fora, porque o nome dele não pende sobre nenhuma seta.
- Texto e valor de uma seta: ~40 e ~24 caracteres.
- A linha do tempo também recebe um alerta de tempo de leitura: o texto de todos os eventos somado, lido a ~17 caracteres por segundo, dentro da duração estimada do plano.
- A skill `roteiro-explicativo` traz a mesma tabela, para o roteirista escrever dentro dos limites.

**Consequências.**
- Contar caracteres é aproximado ("WWW" ocupa mais que "iii"). A conferência automática da tela, que mede o texto desenhado em 1080p, é a próxima medida e vai recalibrar estes números.
- Os roteiros aprovados passam a mostrar alertas novos (o `votorantim-completo` tem 19), sem derrubar a aprovação.

## Emenda de 2026-10-07: número por idioma

**Status:** proposta; vale com o merge do PR que a traz. Não muda o `episode.json`: `language` já existe.

**Contexto.** O pipeline aceita `language: en` (ADR 008), mas os números da tela só funcionavam em pt-BR:
- `screen_number` (Python) e `screenNumber` (template) liam "." como milhar e "," como decimal: "US$ 1,500" virava 1,5, "$4.2 bn" virava 42 e "15.3%", 153;
- o hodômetro do `number` e o `ValueCompare` tinham os separadores fixos em pt-BR;
- o adaptador não levava o idioma ao template (`SceneProps` não tinha idioma);
- a validação do `compare` em escala (decisão 8) lia o número em pt-BR e recusava "US$ 1,234,567" como "não é número";
- o `BarChart` do motion-kit fixado (`527c708`) formata em pt-BR e não tem a prop `locale`; `LineChart`, `ShareChart` e `ValueCompare` têm.

Achado ao ler o código para as verticais em inglês (`docs/pesquisa/nichos-globais-2026-10.md`), antes de qualquer vídeo em inglês.

**Decisão.**
1. O `value` de `number` e de cada lado de `compare` segue a convenção numérica do idioma do episódio: em pt-BR, "1.500,5" (milhar ".", decimal ","); em inglês, "1,500.5" (milhar ",", decimal "."). O mesmo texto vale outro número no outro idioma ("1,500" é 1.500 em inglês e 1,5 em português): quem escreve responde pelo idioma, e o `verificador` confere o valor contra a ficha.
2. `screen_number(valor, idioma)` lê na convenção do idioma (padrão pt-BR). `screen_parts` separa prefixo, dígitos e sufixo sem ler o número, e a regra de unidade do `compare` em escala passa a usá-lo: a unidade não depende do idioma.
3. O adaptador leva `language` às props de cada cena **só quando não é pt-BR**: as props e o cache dos vídeos em português ficam como estavam. O template escolhe os separadores do hodômetro e do `ValueCompare` pelo idioma e passa `locale` ao `LineChart` e ao `ShareChart`.
4. `vp check`, erro novo: `value` de `number` ou de `compare` fora da convenção do idioma quando isso é inequívoco ("47,6" ou "1.234.567" em inglês; "4.2" ou "1,234,567" em português). "1,500" e "1.500" são escritas válidas nos dois idiomas, com valores diferentes, e passam.
5. **Limite temporário, erro:** em inglês, o `chart` de barras (`bar` e `bar_horizontal`) só aceita valores inteiros abaixo de mil, onde o `BarChart` fixado escreve igual nas duas convenções. Sai quando o kit ganhar `locale` no `BarChart` e o pin subir (PR do kit, separado).
6. **As palavras do próprio template e do rodapé também seguem o idioma.** A fonte do rodapé sai de `app/pipeline/attribution.py` no idioma do episódio: "A e B" e "A e outros" em português, "A and B" e "A et al." em inglês; "e outras" vira "and others"; a ressalva "fonte interessada" vira "interested source". O template escreve o resto em `video/src/labels.ts`: o "Fonte" do rodapé (`label` do `SourceTag`) vira "Source", o "em {unidade}" do subtítulo do gráfico vira "in {unidade}", "Manchete" e "Citação" do plano `quote` viram "Headline" e "Quote", e as duas frases-padrão do `ValueCompare` em escala (`ratioWord`, `clampNote`) são trocadas por prop. O texto que o roteiro escreve (narração, rótulos, `unit`, nomes) já vem no idioma do episódio.

**Consequências.**
- Os vídeos em português não mudam: os mesmos casos rodam em Python e em TypeScript (`tests/fixtures/screen-numbers.json`), e as props em pt-BR continuam idênticas.
- Em inglês, números maiores que mil em barras esperam o PR do kit; `number`, `compare`, `line` e `share` já servem.
- Conferido nos pacotes do kit fixado (`527c708`) que o Reel usa (`editorial`, `charts`, `host`, `fx`, `motion`, `theme`): os únicos textos em português visíveis na tela são o "Fonte" do `SourceTag` e as duas frases do `ValueCompare`, todos com prop. As outras peças (rede, mapa, cronologia, documento) não foram auditadas.
- A skill `roteiro-explicativo` traz a regra para o roteirista.
