# Pauta: "Argumento padrão que guarda dados entre chamadas" (Short tec, mods do Claude Code), 2026-10-26

Segundo Short no molde do cofre-en (`renders/short-engenharia-reversa/`): uma demonstração real, saída de
ferramenta na tela, o resultado no começo e no fim. Pauta para validação do dono antes de voz ou render.
Nada renderizado; nada gravado com voz.

**Status:** a versão em C foi validada pelo dono em 2026-10-26 e foi trocada por esta, em Python, no mesmo dia,
a pedido dele. Esta versão aguarda o OK do dono.

## Por que este assunto

Bug de Python que não quebra: a função roda, devolve algo, e o resultado está errado só na segunda chamada. É
o tipo de erro que o público de dev reconhece, e o cenário é de código comum. O ângulo é o do cofre: o Claude
Code faz a análise, e a tela mostra a saída real. A frase que segura o vídeo é "roda sem erro, e o resultado
está errado": é verificável na máquina com `python3`.

## A demonstração (todas as saídas são reais, em `demo/saidas.txt`)

- Fonte `demo/lista.py`: `def adiciona(item, lista=[])`, duas chamadas com "pão" e "leite".
- `python3 lista.py`: `['pão']` e depois `['pão', 'leite']`, exit 0. Nenhum aviso.
- `ruff check --isolated --select E,F`: passa (o conjunto de regras de erro comum não vê o problema).
- `ruff check --isolated`: `B006 Do not use mutable data structures for argument defaults`, na linha 1.
- Correção `demo/lista_certo.py` (`lista=None`, lista criada dentro): `['pão']` e `['leite']`, ruff limpo.

Ferramentas na máquina: Python 3.12 e ruff 0.16.9 (o do projeto). Atenção: o ruff com regras padrão já avisa
B006; a frase do vídeo é sobre o interpretador, não sobre o linter. O texto não diz que o ruff não avisa.

## Mod (skill) do Short

`skill-exemplo/SKILL.md`, `achar-argumento-mutavel`: 6 passos, reproduzir, rodar sem esperar aviso, procurar com
B006, corrigir, conferir, e citar só linha de saída real.

## Plano visual (vertical, ~45 s, molde: pergunta → mod → análise → resultado → fecho)

| # | Batida | Painel de cima (terminal, comandos e saídas reais digitados) | Painel de baixo (o kit) | Fala |
| --- | --- | --- | --- | --- |
| 0 | gancho, 5 s | `python3 lista.py` → `['pão', 'leite']` | cartão "Sem erro. Resultado errado." | Roda sem erro, e o resultado está errado. |
| 1 | o mod, 7 s | o SKILL.md, passos 1 a 3 | o nome da skill | Um mod manda o agente achar a causa. |
| 2 | análise, 12 s | `ruff check` com B006 e a linha 1 destacada | a linha `def adiciona(item, lista=[])` marcada; cartão "lista criada uma vez" | A segunda chamada traz o pão da primeira... |
| 3 | resultado, 12 s | `python3 lista_certo.py` → `['leite']` | "Sem erro. Sem aviso." | Com None, sai só leite. |
| 4 | fecho, 6 s | — | o dono, cartão final | Só em código seu, ou de estudo. |

O dono fica na janela flutuante nas batidas 1 a 3. Peças do kit: `TerminalText`, `DocumentPage` (com a linha
marcada), `HookCard`, `EndCta`, `FloatingWindow` + `Host`, como no cofre.

## Títulos para pontuar no vidIQ depois da validação

- Python roda sem erro e o resultado está errado: o Claude Code achou a linha
- Argumento padrão mutável em Python: o Claude Code achou a causa
- Claude Code e o bug que o Python não avisa

Hipótese (a registrar no canal): o molde "pergunta → saída real → resultado" retém mais de 60% nos 30 s.
Medida: retenção média e inscritos aos 7 e 28 dias no Studio.

## O que falta

- OK do dono na versão Python.
- Narração: pt e en em `data/episodes/short-argumento-padrao/narracao.*.json` (revisadas à mão com os padrões
  da `humanizer-narracao`; a skill é para `scenes.json`, então não rodou direto). Sem voz gerada.
- Gravação da sessão do Claude Code: o painel de cima usa terminal com saídas reais, como no cofre; gravação só
  se o dono pedir.
- Content (`data/episodes/short-argumento-padrao/content.<idioma>.json`): feito e validado pelo
  `validateProduction` do motion-kit. **Desvio da pauta:** o motion-video não tem cena de terminal nem de código.
  O painel de cima (terminal com as saídas reais) e a linha destacada do `ruff` não entram ainda. Nesta versão,
  as saídas aparecem como texto nas cenas `grid` (`analise` e `resultado`). Para a versão da pauta, é preciso
  uma cena nova no kit (como o `CofreDemo` do Cena e Conceito, MR !37), decisão do dono.
- Pele do dono (`sprites/dono`, no `teaser-motion-kit/public`): usada nesta versão; a origem continua pendente
  (ver `needs_review` nos outros shorts).
- Voz (Modal, com pedido do dono), render, gates e posts.
