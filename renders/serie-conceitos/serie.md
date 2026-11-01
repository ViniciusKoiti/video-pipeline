# Série "eu medi": um conceito por semana em Short, 2026-11

Decisão do dono (2026-10-31): uma série semanal de Shorts técnicos explicando um conceito com uma demonstração
medida na máquina dele, no molde do `short-lista-ligada` (ADR 033, 034 e 035). Pautas aprovadas em lote, o mesmo
horário toda semana, três saídas por Short. O fluxo é o de hoje (`docs/pipeline-hoje.mermaid`), em série.

## Calendário

| # | Sábado, 12h (BRT) | Conceito | Pauta | Demonstração medida |
|---|---|---|---|---|
| 1 | 2026-11-07 | Memory leak | `pautas/01-memory-leak.md` | RSS de um programa em C que aloca sem liberar, lido do `/proc` a cada segundo, contra a versão com `free` |
| 2 | 2026-11-14 | Concorrência | `pautas/02-concorrencia.md` | Dois threads somando num contador sem mutex e com mutex: o total e o tempo |
| 3 | 2026-11-21 | Árvores | `pautas/03-arvores.md` | Busca em lista ligada contra árvore binária; a árvore degenerada pela inserção ordenada |
| 4 | 2026-11-28 | Índices | `pautas/04-indices.md` | SQLite: a mesma consulta sem e com índice, tempo e `EXPLAIN QUERY PLAN` |

Horário herdado do Short da lista ligada (31/10, 12h). Ordem: do conceito mais visível (a memória que só sobe)
ao mais abstrato (o índice). Cada Short tem 35 a 45 s de fala, sem música (decisão de 2026-10-30 mantida na
série, para a hipótese medir só a demonstração).

## Saídas por Short

| Saída | Canal (id no Postiz) | Idioma | Apresentador na janela |
|---|---|---|---|
| YouTube Short | `@viniciusnakahara` (`cmvx0omyy0005l26yggavdqpu`) | pt-BR | não (como o da lista ligada) |
| YouTube Short | `@baixo.nivel.dev.s` (`cmvx0nn9g0003l26yf4npmb66`) | en | não |
| Instagram Reel | `koiti.dev` (`cmv8r4jw30001l2863lr8x1lo`, `post_type: post`) | **en** (decisão do dono, 2026-10-31) | **sim: a pele do dono** (ADR 029), só depois do item 1 de "O que trava" |

O Reel é o mesmo `content.en.json` com o campo `host` ligado (`speaking` nas cenas com fala) e um render próprio;
a voz e os efeitos são os mesmos. Sem música em nenhuma saída, então a licença da YouTube Audio Library (só
YouTube) não entra em jogo. A legenda do Instagram, em inglês, traz a mesma origem dos números e a mesma divulgação ("my voice, cloned
with AI; the presenter is drawn from my photos").

## O fluxo de cada Short (o de hoje, nesta ordem)

1. Pauta aprovada (este lote) → **medição própria** na máquina do dono: `demo/` com o programa, `resultado.txt`
   com ambiente, versão e data, `cpu_probe()` antes. Roda local, sem custo; só depois do ok do lote.
2. `roteiro.md` com a origem de cada número → `narracao.pt.json` e `narracao.en.json` (humanizer no pt) →
   `content.pt.json` e `content.en.json` → `medicao.json` → `vp medicao` limpo nas duas pastas.
3. Tradução em pasta própria (`-en`, `traducao.json`) → `vp traducao` → `vp approve <id>-en --step translation`.
4. `validate`, `inspect` e `review` do kit; o dono olha os quadros.
5. Voz clonada no Modal (`shorts_tec.py voz`, só com o pedido do dono na sessão) → `tempos` → `render` dos três
   vídeos (pt, en, pt com a janela) → `sfx.json` → `juntar --sfx` → `conferir_audio.py`.
6. Gate 4 por saída (`vp approve <id>-pt|-en|-ig --step preview`), com `VP_REVIEWER` assinando.
7. Três `post.json` → `vp postiz pacote` → `duvida-cega` → `vp postiz duvida` → `vp postiz schedule`, com a
   confirmação do dono em cada um. Pasta do código no `baixo-nivel-demos` público **antes** do agendamento.
8. Depois de sair: Studio e Instagram à mão (conferir, comentário fixado, rótulo de conteúdo sintético);
   `metrics.json` por saída, leituras aos 7 e 28 dias.

Prazo que cabe numa semana: pauta e medição na segunda, roteiro e JSON na terça, revisão e tradução na quarta,
voz e render na quinta, gates e agendamento na sexta. O que atrasar empurra o Short, não o horário. **Lote aprovado pelo dono em 2026-10-31.**

## Hipóteses

- **Por Short** (copiada para o `metrics.json`): um Short com demonstração própria e número medido na abertura
  retém mais do que um Short de explicação genérica do mesmo tema. Variável: o número medido no gancho. Medida:
  retenção e views aos 7 e 28 dias, comparadas com o `short-lista-ligada`.
- **Da série:** a cadência semanal no mesmo molde faz os inscritos e as views do segundo Short em diante subirem em
  relação ao primeiro. Medida: inscritos e views aos 7 dias de cada um, na ordem. Uma amostra não decide; a decisão
  é depois dos quatro (CLAUDE.md §12).
- **Do Instagram:** o mesmo Short com o apresentador na janela alcança mais no Instagram do que o YouTube pt sem
  janela. É comparação entre plataformas, confundida pelo público de cada uma; registra-se, não se conclui.

## Regras da série

- Só o que a medição mostra. A fala não explica a causa (cache, escalonador, página de memória) sem fonte
  registrada; o fecho pergunta o porquê ao público ("Comenta aqui") e o primeiro comentário fixado traz a medida.
- Cada número da fala e da tela com entrada no `medicao.json`; o gate 4 não abre sem o `vp medicao` limpo.
- Concorrência vista só como forma (o canal Bytada e afins): nada de roteiro, imagem ou título alheio.
- Divulgação da voz clonada em toda legenda; do apresentador, na do Instagram.
- Título pontuado no vidIQ antes do `post.json` (5 créditos por título; só com o pedido do dono).

## O que trava

1. **A pele do dono está em `needs_review`** (`host/dono/origem.json`): a folha de sprites foi gerada em
   2026-10-12 a partir de fotos do dono, e **o gerador não foi informado**. Sem o gerador e os termos dele, a
   licença não entra na lista fechada da ADR 007, e o ativo não vai a vídeo final nem a publicação (gate 3). O
   Reel com o personagem depende de o dono dizer qual ferramenta gerou a folha; aí registro `gerador`,
   `license_id` e `usage_notes`, e ele aprova o ativo. Até lá, o Instagram sai sem a janela ou não sai.
2. **Cada medição é do dono:** o Short diz "medi na minha máquina"; nada de rodar a demo em outro lugar.
3. **Modal (voz) e Postiz** só com o pedido do dono na sessão, Short a Short.

## O que o dono aprova agora

- As quatro pautas, o ângulo recomendado em cada uma (ou outro), a ordem e o horário.
- Com o lote aprovado, começo pela medição do Short 1 (memory leak) na máquina dele, sem perguntar de novo.
