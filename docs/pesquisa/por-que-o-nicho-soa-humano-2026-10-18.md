# Por que os vídeos do nicho soam mais humanos que o nosso

Rascunho de 2026-10-18 para o dono. Piloto `death-note-fins-meios`; nicho de ensaio sobre anime e filosofia em
pt-BR. Números de 40 vídeos (20 com anime, grupo **H**; 20 de filosofia sem anime, grupo **H0**) comparados por
terço de views.

## Resposta curta

- **Analisamos bem o texto e a edição de imagem. Não analisamos o som.** Ninguém ouviu os vídeos, e boa parte
  do "humano" está na voz, na trilha e no jeito de falar.
- Medindo o som hoje, apareceu a diferença mais clara até agora: **os vídeos de cima nunca ficam em silêncio**.
  Há trilha (ou fala emendada) o tempo todo. O nosso trecho fica em silêncio 19% do tempo, com 18 pausas por
  minuto, e não tem música.
- **O que não é o problema:** gíria e jeito de falar ("né", "cara", "tipo") quase não aparecem nos vídeos de
  cima. A entonação da sua voz clonada varia tanto quanto a deles.
- **O que só você pode dar:** opinião e experiência próprias no fecho, e ouvir 3 vídeos com a lista da seção 5.

## 1. Como foi feita a análise (e como você repete)

Tudo está na skill `analise-de-formato` (`.agents/skills/analise-de-formato/`). Os passos 1 a 3 são scripts:
mesma entrada, mesma saída.

| Passo | O que faz | Comando |
|---|---|---|
| 1. Amostra | Escolhe os vídeos de mais e de menos views por grupo, no máximo 2 por canal, com pelo menos 3 min | `python3 -I .agents/skills/analise-de-formato/amostra.py <csv> <pasta>/amostra.tsv --grupos H H0 --por-grupo 20` |
| 2. Download | Baixa com o **yt-dlp**: metadados (views, inscritos, duração), **a legenda** em português e uma cópia de 360p | `python3 -I .agents/skills/analise-de-formato/baixar.py <pasta>/amostra.tsv <pasta> --ytdlp <yt-dlp> --cookies cookies.txt` |
| 3. Medição | **Legenda** → transcrição limpa → palavras por minuto, "você", "eu", fonte citada. **Trocas de imagem** → o ffmpeg marca cada corte seco (mudança de cena acima de 0,3). Folha de 32 quadros por vídeo | `python3 -I .agents/skills/analise-de-formato/medir.py <pasta>` |
| 3b. Pandas | Cruza cada medida com as views, compara o terço de cima com o de baixo e traça a curva do vídeo em décimos | `analisar.py <pasta> <pasta>/amostra.tsv --episodio <episode.json>` |
| 3c. Folha densa | Um quadro a cada 0,1 s na abertura e no meio, para ver como o texto entra | `folha_densa.py <pasta>` |
| 4. Fichas | Agentes leem a transcrição e a folha de 8 vídeos e descrevem abertura, espinha, voz, imagem e fecho | subagentes, um a cada 2 vídeos |
| 5. Síntese | Tabela de padrões e recomendações no relatório do nicho | à mão |

**Resposta à sua pergunta:** sim, baixamos os vídeos, lemos as legendas (a transcrição do que o narrador fala) e
contamos as trocas de imagem (os cortes). O que faltava era o som. A medição de voz feita hoje
(`formato/analise/voz.py`) ainda não está na skill.

**O que você precisa para repetir:** o yt-dlp com Node.js, os cookies do YouTube (só com a sua autorização), o
ffmpeg e o pandas. Leva uns 30 min para 40 vídeos, quase todo o tempo no download.

## 2. O que a análise não viu

| Lacuna | Por que importa | Como fechar |
|---|---|---|
| **O som** (trilha, efeitos, voz) | É onde mora boa parte da sensação de "gente falando" | Medição de voz (seção 3) e você ouvindo (seção 5) |
| **Ninguém assistiu um vídeo inteiro** | As fichas leram transcrição e quadros soltos; piada, ironia e silêncio de efeito não aparecem no texto | Escuta guiada (seção 5) |
| **Retenção** | Temos só views, que dependem de miniatura, título e tamanho do canal. Não sabemos onde as pessoas desistem | Só com métrica própria, aos 7 e 28 dias do nosso vídeo |
| **Amostra pequena** | 20 vídeos por grupo; quase toda ligação com views é fraca (no máximo 0,3 a 0,6) | Tratar tudo como tendência |
| **Legenda automática** | Sem pontuação e com nomes errados; "pra" pode virar "para" | Conferir na escuta |

## 3. O que medimos hoje: conversa e som

### Marcas de conversa na fala (por mil palavras, mediana)

| | "né" | "cara/galera" | "tipo" | "olha/sabe" | "pra/tá" | "eu acho/pra mim" |
|---|---|---|---|---|---|---|
| H, terço de cima | 0 | 0,5 | 0 | 2,1 | 0,7 | 0 |
| H, terço de baixo | 0 | 1,0 | 0 | 1,0 | 1,7 | 0 |
| Nosso roteiro (rodada 13) | 0 | 0 | 0,5 | 2,1 | 0 | 0 |

**Leitura:** os vídeos de cima não soam humanos por gíria. Falam um português cuidado, como o nosso. Não vale
encher o roteiro de "né" e "cara".

### Som (3 janelas de 60 s por vídeo; o nosso é o `trecho-v2`, 2 min com a sua voz clonada)

| | Variação da entonação (semitons) | Pausas por minuto | Tempo em silêncio | Vídeos com som contínuo* |
|---|---|---|---|---|
| H, terço de cima | 4,6 | 1,0 | 4% | 7 de 7 |
| H, terço de baixo | 4,5 | 3,3 | 4% | 5 de 7 |
| H0, terço de cima | 4,3 | 0 | 0% | 7 de 7 |
| H0, terço de baixo | 3,9 | 7,0 | 8% | 3 de 7 |
| **Nosso trecho** | **5,1** | **18** | **19%** | **não** |

\* Menos de 4 pausas por minuto: há trilha por baixo da voz, ou a fala foi editada sem respiro. A medida não
separa os dois casos; a escuta separa.

**Leitura:**
- **Silêncio.** É a diferença mais forte que achamos. No grupo H, menos pausa e volume mais constante andam com
  mais views (ρ = −0,34 e −0,42). Todos os 14 vídeos do terço de cima, nos dois grupos, têm som contínuo. O
  nosso tem silêncio entre as frases e entre as cenas, sem trilha. Isso soa como leitura, não como conversa.
- **Entonação.** A sua voz clonada varia 5,1 semitons, mais que a mediana deles (4,6). Pela medida, a voz não é
  monótona. A ressalva é que a música por baixo atrapalha a medida deles.
- **Cuidado:** são medidas de computador sobre o áudio, não de ouvido. Confirme na escuta.

## 4. O que faz um vídeo soar humano: o que temos e o que falta

| O que os vídeos de cima fazem | Nosso roteiro novo | Falta |
|---|---|---|
| Um fio só: a história em ordem | sim (rodada 13) | — |
| Falam com quem assiste ("você"), mais no fecho | sim (35 por mil no fecho) | — |
| Imagem em movimento segurada depois da abertura | não (109 fotos paradas) | B-roll como textura: o código está pronto (PR `broll-textura`), falta o plano de imagens |
| **Som contínuo: trilha por baixo, sem buraco de silêncio** | **não** | **Trilha (ADR 030) e menos pausa entre cenas** |
| **Narrador com opinião e lembrança própria** ("pra mim…", "eu lembro quando…") | **não: o narrador não diz "eu"** | **Frases suas** |
| Fecho que volta à sensação da abertura, sem lição | em parte (devolve a pergunta) | depende das frases suas |

## 5. O que você pode fazer

Em ordem de peso, do que só você decide:

1. **Ouvir 3 vídeos (cerca de 45 min) com esta lista**, anotando sim ou não e um minuto de exemplo:
   - `d3VxGiFa-aE`, Filosofatos, "Eren Yeager é o Super-Homem do Nietzsche…" (278 mil views, 23 min)
   - `h1V5XGdqBjs`, Pensador Geek, "A Filosofia de vida de kakashi (estoicismo)" (67 mil, 8 min)
   - `dtkIdnNMPek`, Relry, "EREN YEAGER e o efeito LÚCIFER" (27 mil, 5 min)
   - Para comparar, um de baixo: `mP4SXHGfJKk`, Entre Mundos, "Como entender as pessoas? - Monster…" (1,4 mil)

   Perguntas da escuta:
   - A voz é de gente ou de máquina? Dá para saber?
   - Tem música o tempo todo? Ela muda de clima nas viradas?
   - O narrador ri, hesita, se corrige, faz piada?
   - Quando ele diz "eu", é opinião, lembrança ou confissão?
   - Em que minuto você teria parado de assistir, e por quê?
   - O que o de baixo faz diferente?

2. **Decidir a trilha.** A ADR 030 (trilha escolhida por um agente `diretor-musical`, faixas da YouTube Audio
   Library) está proposta. As 36 faixas em `MUSICAS/` precisam ter o tipo de licença confirmado por você. Sem
   trilha, o buraco de silêncio continua.

3. **Escrever 2 ou 3 frases suas**, em primeira pessoa, que vão como opinião marcada (ADR 019):
   - **No fecho:** o que você acha da pergunta. Light estava certo em algum momento? Você torceu por ele?
   - **Opcional, na abertura:** uma lembrança real ("a primeira vez que vi Death Note…").

   Eu não posso inventar isso, porque a voz é a sua.

4. **Escolher a voz das partes pessoais:**
   - (a) a voz clonada lê as suas frases, como o resto;
   - (b) você grava só a abertura e o fecho, e a voz clonada faz o meio.

   A opção (b) é a mais humana e custa uns 10 min de gravação.

5. **Aprovar o caminho da fábrica de roteiros** (ADR 031) e o PR do B-roll.

## 6. O que eu faço depois das suas respostas

1. Ponho a medição de voz na skill `analise-de-formato` (passo 3d), para os próximos nichos já saírem com som
   medido.
2. Escrevo o plano de imagens com B-roll como textura, trecho por trecho, para você validar antes de baixar.
3. Com a trilha decidida, monto de novo o trecho de 2 min com:
   - menos pausa entre as cenas (a ADR 015 já controla as pausas);
   - trilha por baixo;
   - as suas frases.

   Assim dá para comparar com o `trecho-v2`.
4. Repito a medição de som no trecho novo e ponho os números lado a lado nesta tabela.

## Arquivos

- Medidas de voz: `docs/pesquisa/research_notes/Nicho recap de anime/formato/analise/voz.csv` (script `voz.py`
  na mesma pasta)
- Texto na tela: `formato/analise/texto-na-tela.tsv`; medidas de fala e corte: `formato/analise/medidas.csv`
- Relatório do nicho com o adendo de formato: `docs/pesquisa/reports/Nicho recap de anime.md`
- Os vídeos baixados ficam em `data/cache/nicho/Nicho recap de anime/`, fora do Git, só para análise
