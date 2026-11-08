# 056 — Regime de fontes por vídeo, declarado pelo roteirista

- **Status:** aceita pelo dono em 2026-11-07 ("não precisamos sempre citar fontes em nossos vídeos; isso deve ser
  definido somente pelo roteirista, porque o vídeo pode ter o intuito de entreter"), com as duas recomendações
  registradas abaixo.
- **Data:** 2026-11-07
- **Relacionada a:** ADR 008 (claims), 009 (fichas), 011 (rodapé de fonte), 019 (objetivo), 020 (conta na tela),
  055 (ficção histórica declarada).

## Contexto

A ADR 055 e o §2.2 do CLAUDE.md já diziam que "a regra de fato do roteiro é de cada roteirista", mas o código
seguia presumindo um só regime: o schema exigia pelo menos uma `claim` em todo plano factual na tela (`number`,
`compare`, `quote`, `lower_third`, `chart`, `calculation`, `receipt`, `network`, `family_tree`), de modo que um
vídeo de entretenimento com uma citação ou um número na tela nem passava pela leitura do `scenes.json`; o
`vp check` alertava "frase afirmativa em cena sem claims" em todas as cenas, sem saber o propósito do vídeo
(116 alertas no `montaigne-desapego`, nenhum lido); e o rodapé de fonte saía das claims, o que para um ensaio
no molde dos canais de referência nem é desejável. O pedido do dono é que a decisão de citar seja do roteirista.

## Decisão

1. **O roteirista declara o regime de fontes no `scenes.json`**, no campo `sources_policy`, com um de três
   valores; sem o campo, vale `documental`, o comportamento de antes.

   | Regime | Fichas e claims | Rodapé e descrição | `vp check` |
   |---|---|---|---|
   | `documental` | obrigatórios: claim em toda afirmação de fato e em tudo o que vai à tela | fonte no rodapé do plano e na descrição | erro e alerta como antes |
   | `ensaio` | fichas obrigatórias; claim só no que vai à tela (número, data, citação, cargo, gráfico) | só na descrição; rodapé vazio | sem o alerta de frase sem claim |
   | `entretenimento` | dispensados, como na ADR 055 | nada | valida só as claims que existirem |

2. **O código obedece em vez de presumir.** A exigência de claim nos planos factuais sai do plano
   (`_FactualShot`) e vai para o `ScenesManifest`, que a aplica nos regimes `documental` e `ensaio`; o rodapé
   (`app/pipeline/attribution.py`, via `episode_build`) só sai no `documental`; o alerta de frase afirmativa sem
   claim só vale no `documental`; o `vp check` registra o regime na linha "regime de fontes: …" e o `vp status`
   o mostra junto do gate 2, para o dono saber o que está aprovando. Claims que existirem continuam conferidas
   em qualquer regime (fonte registrada, trecho existente e fichado, citação literal).

3. **Exceção fixa: pessoa viva e empresa ativa.** Fato sobre pessoa viva, empresa ativa ou produto (os Reels do
   Thiel, o perfil da Votorantim) exige ficha e fonte em qualquer regime, mesmo sem nada na tela: entreter não
   protege de difamação. O código não sabe quem está vivo; a regra é do roteirista, do verificador e do gate 2.
   O `vp check` só lembra dela quando o regime `entretenimento` vem com objetivo `noticiar`.

4. **Onde a fonte aparece não muda o que é verdade.** A pesquisa continua sem inventar (§2.2): o `pesquisador`
   só ficha trecho real. O regime decide a exibição e a obrigação de claim, não a permissão de afirmar o que não
   se sabe; a regra do `roteirista-ficcao-historica` ("não afirme com precisão o que não saberia sustentar") vale
   para todo `entretenimento`.

## Consequências

- `app/pipeline/models/_schemas_types.py` (`SourcesPolicy`), `scenes_manifest.py` (campo e validador),
  `_schemas_factual_shot.py` (claims sem mínimo), `app/pipeline/sources_policy.py` e
  `constants/sources_policy_constants.py` (o que cada regime muda), `check.py`, `episode_build.py`,
  `app/commands/status.py`; testes em `tests/test_sources_policy.py`.
- Skills: `roteiro-explicativo` declara o regime no item das afirmações; `roteiro-ficcao-historica` declara
  `entretenimento` e deixa de esperar o alerta de frase sem claim. O agente `roteirista` ganha a regra.
- A "pendência" da ADR 055 (marcador de ficção e ajuste do `vp check`) fica resolvida por esta: o marcador é o
  regime do vídeo, não da cena. Arestas de `network` continuam exigindo claim em qualquer regime: rede de relações
  entre pessoas ou empresas reais é afirmação documental.
- Episódios já publicados não mudam: sem o campo, o regime é `documental`.
- Fica para o roteirista, na pauta, dizer o regime antes de escrever; o dono o vê no `vp status` no gate 2.
