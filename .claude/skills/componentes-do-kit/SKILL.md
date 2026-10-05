---
name: componentes-do-kit
description: |
  Consulta o motion-kit pelo MCP `motion-kit` antes de escolher um componente ou passar uma prop no template
  do formato explicativo (`video/`): componente para o objetivo de uma cena, props e defaults de um
  componente, conferência contra a versão do kit que o `video/` realmente renderiza.
argument-hint: "<objetivo da cena ou nome do componente>"
---

# Componentes do kit: consultar antes de escrever

O template (`video/src/ShotView.tsx` escolhe o componente por `kind` do plano; `video/src/Editorial.tsx` monta
as peças) usa o `@viniciusk/motion-kit`. O servidor MCP `motion-kit` responde sobre esse kit **a partir do
checkout** em `~/projetos/motion-kit`: lê os exports, o catálogo `src/COMPONENTS.md` e as fontes TypeScript, sem
executar nada. Tipos importados ou herdados podem faltar na resposta: prop que não aparece se confirma no arquivo
do componente antes de ser dada como inexistente.

## Ferramentas (só leitura)

| Ferramenta | Entrada | Devolve |
|---|---|---|
| `describe_component` | `{}` | os componentes públicos, com importação e descrição |
| `describe_component` | `{"component": "Nome"}` | assinatura, tipos, defaults literais, trecho do catálogo e exemplos |
| `recommend_components` | `{"goal": "..."}` | componente indicado e motivo para o objetivo |

Objetivos de `recommend_components`: `headline`, `image_caption`, `comparison`, `trend`, `categories`,
`timeline`, `map`, `presenter`, `relationships`, `number`, `share`, `document`, `photo`, `stamp`, `lower_third`.
A lista é curada à mão no kit; um objetivo fora dela vira erro. Trate a recomendação como pista e confirme em
`describe_component`.

## Método

1. **Escolher.** Parta do `kind` do plano que você mexe e veja o componente atual no `switch` de
   `ShotView.tsx`. Para um objetivo novo, chame `recommend_components` com o `goal` mais próximo.
   Pronto quando há **um** componente candidato, com o motivo da escolha.
2. **Conhecer.** Chame `describe_component` com o nome. Anote importação, props, defaults e o exemplo mais
   próximo do uso. Pronto quando **toda prop que você vai passar** consta no tipo devolvido ou no arquivo do
   componente; prop que o kit não tem se resolve num PR dele, e não no `video/`.
3. **Cruzar com o pin.** O servidor responde pelo checkout; o `video/` renderiza o SHA de
   `video/package.json` (`sha=` da URL do `@viniciusk/motion-kit`). Compare com
   `git -C ~/projetos/motion-kit rev-parse HEAD`. Pronto quando os SHAs são iguais, ou quando a diferença está
   dita no PR e você conferiu no `git diff <pin> HEAD` que a prop usada existe nas duas versões.
4. **Escrever.** Altere o template; render e comparação seguem a regra do vídeo-régua (CLAUDE.md §1): um PR de
   visual gera uma versão nova e muda só os planos que pretendia.

## Quando o MCP não responde

Sem as ferramentas `mcp__motion-kit__*` na sessão (o Claude Code carrega servidores ao iniciar) ou com o
servidor desconectado (`claude mcp get motion-kit`), leia a mesma fonte direto: `src/COMPONENTS.md` e o arquivo do
componente em `~/projetos/motion-kit/src/`. O passo 3 vale igual.

## Fora do escopo

As ferramentas de render do servidor (`review_video`, `start_render`) fazem outro formato: vídeo vertical,
silencioso, de três tipos de cena. O render do nosso explicativo é o do `app/render/remotion.py`.
