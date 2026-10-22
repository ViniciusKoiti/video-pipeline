# Dois moldes: o do canal de referência e o do topo reproduzível (2026-10-22)

A dúvida do dono: o molde do Filosofatos é o canal que escolhemos, mas são os canais de mais views que a
pipeline deveria imitar? Antes de responder, separou-se o que a pipeline consegue refazer. Sete subagentes leram
as folhas de quadros dos 41 vídeos medidos (`imagem/leitura-*.tsv`), sem saber canal nem views, e anotaram
apresentador e base da imagem; a regra de "reproduzível" é código (`reproduzivel.py`, passo 4d da skill): sem
apresentador e com base em banco, foto de arquivo, pintura, texto, ilustração própria ou quadro parado.

- **Pessoa em cena:** Ciência Todo Dia, Jean Alessandro, Tinocando TV, Tempero Drag, Eslen Delanogare e Inferno
  de Dante. Saem.
- **Sem rosto, mas em cima de anime em movimento ou gameplay:** Filosofatos, Pensador Geek, Relry, Nerd Tab e
  outros. A imagem deles não é reproduzível (regra 2.3 e emenda de citação da ADR 007); o texto, sim.
- **Reproduzíveis em português com 400 mil views ou mais (grupo `TOPO`, 9 vídeos):** Epifania Experiência
  (7,9 mi), A Psique (3,0 mi e 843 mil, pintura com zoom em 90–100% dos quadros), Coelho Branco (1,9 mi),
  Conexão Psíquica (756 mil), A Odisseia Interior (729 mil e 407 mil), Conceito Ilustrado (574 mil),
  SUPERLEITURAS (548 mil). Imagem parada com zoom em 9 dos 14 reproduzíveis; legenda queimada, título de bloco
  e citação na tela em metade ou mais. Ilustração própria é reproduzível em princípio, mas custa arte.

Batidas marcadas nos 9 (`batidas/`), concordância de 86,5% do tempo no vídeo repetido (`batidas-concordancia/`,
acima do corte de 80%). O `molde.py --grupo TOPO --amostra imagem/amostra-topo.tsv` gerou o segundo molde e
`comparar_moldes.py` pôs os dois lado a lado (`moldes-lado-a-lado-2026-10-22.md`).

| medida | Filosofatos (13) | Topo reproduzível (9) |
|---|---|---|
| duração | 22,8 min | 13,9 min |
| % do tempo em caso | 38,8 | 20,6 |
| % em conceito | 31,9 | 44,8 |
| % falando com quem assiste | 9,6 | 29,9 |
| % do narrador (confissão + opinião) | 13,8 | 3,7 |
| confissões por vídeo | 3 (11 de 13 têm) | 0 (0 de 9) |
| "eu" por mil palavras / 1º "eu" | 10,5 / 3 s | 1,6 / 221 s |
| palavras por minuto | 184 | 152 |
| cortes por minuto | 1,5 | 0,1 |
| bloco abre com caso | 50% dos blocos | 13% |
| fim retoma a abertura | 85% | 78% |
| chamada | 31% | 67% |

Leitura: os dois moldes quase não se cruzam. O Filosofatos é caso, narrador presente e confissão; o topo
reproduzível é conceito, "você" e narrador ausente, falado mais devagar e sobre imagem parada. Concordam em
pouco: seis blocos, fim que retoma a abertura, promessa raramente dita, título de bloco dito em mais da metade.
Nenhum traço é `padrao` nos dois. A análise de replay de 2026-10-21 pesa contra o segundo molde (aplica e
opinião são os trechos menos reassistidos no Filosofatos), e as views do topo medem tema e tamanho do canal tanto
quanto forma: é indício, não prova.

**Decisão do dono:** qual molde alimenta a partitura do próximo ensaio, ou uma combinação (estrutura e imagem do
topo, voz do narrador do Filosofatos). Esta nota é a síntese do passo 5 da skill para este adendo; o relatório
do nicho em `docs/pesquisa/reports/` fica fora do Git e recebe o mesmo texto quando o dono quiser.
