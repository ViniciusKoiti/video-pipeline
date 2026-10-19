# 031 — Perfil de formato do nicho como entrada do roteiro longo

- **Status:** proposto (rascunho para o dono, 2026-10-18). A parte A (B-roll como textura) está implementada no
  PR que traz este texto; as partes B a E esperam a aprovação do dono.
- **Data:** 2026-10-18
- **Etapa do roadmap:** roteiro (#28), épico #164 (piloto `death-note-fins-meios`)
- **Relaciona-se com:** ADR 009 (agentes e `vp check`), ADR 011 (planos editoriais), ADR 018 (resumo do radar nos
  Reels, que esta repete para o vídeo longo), ADR 019 (objetivo e opinião do dono)

## Contexto

O roteiro do piloto `death-note-fins-meios` passou na checagem (rodada 8), mas o dono achou a história pouco
natural. A skill `analise-de-formato` mediu 40 vídeos em pt-BR do nicho de ensaio (20 sobre anime, 20 de filosofia
sem anime) e leu 8 deles em ficha; o adendo está em `docs/pesquisa/reports/Nicho recap de anime.md`. Os vídeos de
mais views seguem um fio só (a vida do personagem em ordem, ou uma pergunta que abre e fecha), põem o conceito na
cena que ele explica, falam com quem assiste ("você" ~8 por mil palavras, ~34 no fecho), cortam rápido só na
abertura e depois seguram uma imagem **em movimento** (0 a 4 cortes por minuto). As ligações são fracas
(|ρ| ≤ 0,3 com 20 vídeos por grupo): são tendências, não regra.

A fábrica de roteiros não tinha como receber isso. A skill `roteiro-explicativo` tem um formato só, escrito à mão
para o perfil de poder e os Reels: gancho fora de ordem, espinha de viradas, um plano a cada 2 a 4 s, e o
`vp check` avisa todo plano acima de 6 s. A análise terminava num relatório que nenhum agente lia. O roteiro
reescrito à mão na ordem da história (rodadas 9 a 13) precisou de cinco checagens, e um erro de ficha (F77) só
apareceu depois do roteiro, reabrindo o gate 1.

## Opções consideradas

1. **Escrever as regras do nicho na skill.** Simples, mas a skill passa a ter um formato por nicho, e o número
   que muda com a amostra fica preso no texto.
2. **Perfil medido por nicho, copiado no episódio (escolhida).** O mesmo desenho da ADR 018: um arquivo de forma,
   datado, que o roteirista lê e o `vp check` compara. Muda a amostra, muda o arquivo; a skill fica geral.
3. **Não mudar a fábrica; o dono corrige caso a caso.** Foi o que aconteceu neste piloto: funciona, mas custa
   rodadas e depende de o dono notar.

## Decisão

O perfil de formato do nicho é uma **entrada do roteiro longo**, sempre como forma e nunca como fonte (§2.2), em
cinco partes:

**A. B-roll como textura (implementado).** Segurar uma imagem em movimento depois da abertura é o ritmo do
formato. O render passa a:
- continuar o mesmo vídeo de onde parou quando mídias seguidas usam o mesmo arquivo, também de uma cena para a
  seguinte, sem o fade entre elas (`startFrom`, `fadeOut: false`);
- recomeçar o clipe quando o plano é mais longo que ele (`loopFrames`).

As duas coisas são calculadas das props (`footage_continuity`, `app/render/remotion.py`); o `episode.json` não
muda. O `vp check` não avisa mais `broll` acima de 6 s. Cena do anime em movimento continua fora: a regra 2.3 e a
emenda de citação da ADR 007 só admitem quadro parado. Gameplay e filme de terceiros também ficam fora (licença
fora da lista fechada).

**B. Perfil copiado no episódio.** A skill `analise-de-formato` grava, além do relatório, um
`formato-brief.json` do nicho; um script copia a versão datada para `data/episodes/<id>/`. Cada medida traz o
valor dos vídeos de mais views, o do terço de baixo, `n` e a força (`pattern` só com amostra e ligação que
sustentem; o resto é `hint`): duração, ritmo da fala, trocas de imagem por minuto na abertura e depois, "você" e
"eu" por mil palavras no meio e no fecho, fonte citada na fala, texto na tela e o tipo de espinha.

**C. Skill do roteiro lê o perfil.** Com o arquivo, o ritmo de planos e a duração vêm dele, não da regra fixa de
2 a 4 s; entram a regra do fio único (o conceito entra na cena que ele explica) e a textura em B-roll depois da
abertura. O `outline.md` ganha a seção "Formato": cada padrão seguido, ou não e por quê. Sem o arquivo, a skill
segue como hoje. "Você" continua preso às fichas (ADR 018): o perfil não libera afirmar algo sobre o espectador.

**D. Alertas no `vp check`.** Só os padrões do perfil que dá para medir no roteiro: duração, planos por minuto na
abertura e depois, "você" por mil palavras e no fecho. São alertas, nunca erros. Mais um alerta geral, com ou sem
perfil: frase afirmativa em cena sem `claims` (duas rodadas deste piloto foram isso).

**E. Antes do roteiro.** A skill `pauta` pergunta ao dono se ele quer dizer algo seu no fecho (vai como opinião
marcada, ADR 019). O verificador confere as fichas logo depois do fichamento, antes do gate 1, para erro de ficha
não reabrir o gate depois do roteiro.

## O que fica de fora

- **Fato do perfil.** Títulos, frases e imagens dos vídeos medidos não entram no roteiro nem no vídeo; o material
  baixado fica em `data/cache/`, fora do Git.
- **Indício vira alerta.** Só `pattern` gera alerta; com 20 vídeos por grupo, quase tudo ainda é indício.
- **Retenção.** A amostra só tem views. Copiar a forma é aposta, não prova; a métrica própria aos 7 e 28 dias
  (§12) é o que decide.

## Consequências

- Parte A: `app/render/remotion.py`, `video/src/{Editorial,Scene,ShotView,types}.tsx|ts`, `app/pipeline/check.py`,
  testes em `tests/test_remotion_props.py` e `tests/test_editorial_shots.py`. O vídeo-régua não muda (nenhum plano
  dele ganha `startFrom`, `loopFrames` ou corte sem fade). Cinco rascunhos de Reels com B-roll mais longo que o
  clipe passam a repetir o clipe em vez de parar no fim.
- Partes B a E: `.agents/skills/analise-de-formato/` (gera o perfil), skills `roteiro-explicativo`, `pauta` e
  `checagem`, `app/pipeline/check.py` e um módulo do perfil no molde de `app/pipeline/radar.py`. Um PR por parte.
- B-roll longo pesa mais no render: medir o tempo no primeiro trecho, com a sonda de CPU antes.
