# 031 — Perfil de formato do nicho como entrada do roteiro longo

- **Status:** proposto (rascunho para o dono, 2026-10-18). A parte A (B-roll como textura) está implementada no
  PR que traz este texto. A parte B está implementada (2026-10-22) como `molde.json` + `partitura.md`, com
  prevalência e quartis no lugar da correlação com views (emenda abaixo); as partes C e D estão implementadas
  (2026-10-22: o roteirista lê a `partitura.md`; o `vp check` avisa pelo `molde.json`); a parte E espera a
  aprovação do dono.
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

*Emenda (2026-10-22, implementação da parte B).* O perfil é o `molde.json` gerado por `molde.py`, e a entrada do
roteiro é a `partitura.md` gerada por `partitura.py` (passo 4c da skill). Mudanças em relação ao texto acima:
a força sai da **prevalência** ("11 de 13 têm confissão"), não da correlação com views, porque com 13 a 20
vídeos a correlação quase nunca sustenta um `pattern` e prevalência é o que o roteiro consegue seguir; cada
medida leva mediana, q1, q3 e n, mais o terço de cima e o de baixo quando há 6 ou mais vídeos; entram as
medidas de estrutura das batidas (parte 4b) e as curvas por décimo; a partitura escala o molde para a duração
do episódio. `padrao` = 8 ou mais vídeos e 80% ou mais; o resto é `indicio`. São dois moldes (2026-10-22):
o do canal de referência, que é a forma escolhida pelo dono, e o do topo reproduzível do nicho (vídeos mais
vistos sem apresentador e com base de imagem que a pipeline faz; passo 4d da skill, `reproduzivel.py`), postos
lado a lado por `comparar_moldes.py`. O que é `padrao` nos dois vale sem discussão; o que diverge é decisão do
dono.

**C. Skill do roteiro lê o perfil.** Com o arquivo, o ritmo de planos e a duração vêm dele, não da regra fixa de
2 a 4 s; entram a regra do fio único (o conceito entra na cena que ele explica) e a textura em B-roll depois da
abertura. O `outline.md` ganha a seção "Formato": cada padrão seguido, ou não e por quê. Sem o arquivo, a skill
segue como hoje. "Você" continua preso às fichas (ADR 018): o perfil não libera afirmar algo sobre o espectador.

**D. Alertas no `vp check`.** Só os padrões do perfil que dá para medir no roteiro: duração, planos por minuto na
abertura e depois, "você" por mil palavras e no fecho. São alertas, nunca erros. Mais um alerta geral, com ou sem
perfil: frase afirmativa em cena sem `claims` (duas rodadas deste piloto foram isso).

*Emenda (2026-10-22, implementação das partes C e D).* `app/pipeline/molde.py` lê a cópia `molde.json` (com
as casas pedidas pela partitura em `episodio`) e avisa: duração estimada fora de 20% da pedida; planos que
trocam a tela nos primeiros 60 s acima do q3 do molde e, depois da abertura, acima do dobro do que o molde
troca por minuto; "você" por mil palavras fora de q1–q3; "você" e "eu" que o molde sobe no último décimo e o
roteiro não; e, só para traços `padrao`, confissão do narrador sem nenhuma frase de confissão no texto e fim
que não repete nenhuma expressão do primeiro minuto (os dois por expressão regular: são indícios, e a revisão
humana decide). O alerta geral de frase afirmativa em cena sem `claims` conta só frases com número ou nome
próprio e seis ou mais palavras, uma por cena, fora perguntas e primeira pessoa. Molde com menos de 8 vídeos
avisa que é só descrição. A skill `roteiro-explicativo` ganhou a seção "Partitura do episódio" e o
`outline.md`, a seção "Formato".

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
- Parte B: `.agents/skills/analise-de-formato/molde.py` e `partitura.py`, testes em
  `tests/test_molde_partitura.py`. Partes C e D: `app/pipeline/molde.py` (no molde de `app/pipeline/radar.py`),
  `app/pipeline/check.py`, skill `roteiro-explicativo` e agente `roteirista`, testes em
  `tests/test_molde_check.py`. Parte E: skills `pauta` e `checagem`, em PR próprio.
- B-roll longo pesa mais no render: medir o tempo no primeiro trecho, com a sonda de CPU antes.
