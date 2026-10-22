---
name: analise-de-formato
description: |
  Analisa como os vídeos de um nicho são feitos (abertura, espinha da história, voz do narrador, imagem, ritmo de
  edição e fecho) a partir de uma amostra baixada e medida por scripts determinísticos, e devolve o que levar
  para o roteiro. Use depois da medição de demanda da `validacao-de-nicho`, ou quando o dono pedir para "ver como
  o nicho faz" antes de escrever ou reescrever um roteiro.
argument-hint: "<csv da medição de demanda ou lista de vídeos> [episódio a comparar]"
---

# Análise de formato: como o nicho faz os vídeos

A pergunta: **o que os vídeos que funcionam neste nicho fazem que o nosso roteiro ainda não faz?** A resposta
separa **medida** (sai dos scripts, igual a cada execução), **leitura** (a ficha de cada vídeo) e
**recomendação** (o que muda no nosso roteiro, dentro das regras do projeto).

Os passos 1 a 3 são determinísticos: mesma entrada, mesma saída. O julgamento começa no passo 4.

Saídas:
- material baixado em `data/cache/nicho/<Título>/`, fora do Git;
- fichas em `docs/pesquisa/research_notes/<Título>/formato/<video_id>.md`;
- o molde do nicho em números (`analise/molde.json`) e a partitura de um episódio (`partitura.md`, passo 4c);
- o veredito de reproduzível por vídeo e a amostra do topo reproduzível (`analise/reproduzivel/`, passo 4d);
- síntese como seção "Adendo: como o nicho faz os vídeos" no relatório do nicho em `docs/pesquisa/reports/`.

## 1. Amostra

```
python3 -I .agents/skills/analise-de-formato/amostra.py <csv> data/cache/nicho/<Título>/amostra.tsv \
  --grupos H H0 --por-grupo 4 --incluir <ids escolhidos>
```

- O CSV é o da `validacao-de-nicho` (`coleta.py`).
- Padrão: os 4 vídeos de mais views de cada grupo, um por canal, com pelo menos 3 min.
- `--incluir` serve para o concorrente direto do tema do episódio, mesmo com poucas views. Ele mostra o que não
  funcionou.

Pronto quando a amostra tem de 6 a 10 vídeos e o motivo de cada um está no TSV.

## 2. Download

```
python3 -I .agents/skills/analise-de-formato/baixar.py data/cache/nicho/<Título>/amostra.tsv \
  data/cache/nicho/<Título>/ --ytdlp "$YTDLP" [--cookies cookies.txt]
```

- Baixa metadados, legenda e uma cópia de 360p. Só o que falta é baixado.
- yt-dlp com `yt-dlp-ejs` e Node.js. Um ambiente fora do `.venv` do projeto: é ferramenta da skill, não
  dependência do pipeline.
- **Cookies só com autorização do dono, pedida na sessão.** O script usa uma cópia e a apaga no fim. O arquivo
  original fica fora do Git (`.gitignore`) e nunca tem o conteúdo impresso.
- Código 4: o YouTube pediu login. Pare e pergunte ao dono pelos cookies.

Pronto quando cada vídeo tem `info.json` e legenda. O vídeo pode faltar; a ficha então fica sem a seção 4.

## 3. Medição

```
python3 -I .agents/skills/analise-de-formato/medir.py data/cache/nicho/<Título>/
```

Grava a transcrição limpa (`<id>.txt`), a folha de 32 quadros (`<id>_folha.jpg`) e `medidas.csv`:
- palavras por minuto;
- cortes por minuto e plano médio;
- "você" e "a gente" por mil palavras;
- capítulos;
- o texto dos primeiros 60 s.

Também grava `janelas.csv`: palavras, cortes, "você", "a gente", "eu" e fonte citada a cada 30 s, com a posição
da janela no vídeo.

Pronto quando `medidas.csv` tem uma linha por vídeo e `janelas.csv` existe.

Para ver o movimento (como o texto entra, onde corta), a folha densa: 40 quadros, um a cada 0,1 s, com o tempo
escrito, na abertura e no meio de cada vídeo (`<id>_densa_00.jpg`, `<id>_densa_50.jpg`):

```
python3 -I .agents/skills/analise-de-formato/folha_densa.py data/cache/nicho/<Título>/ [--posicoes 0 0.5]
```

Leia as folhas com subagentes que não sabem as views de cada vídeo (lista de ids, sem grupo), e só depois cruze
com o terço de views.

Para olhar cena a cena (3 ou 4 vídeos de cima, 1 de baixo e o nosso trecho), a decupagem: um quadro por cena, com
o tempo e a fala daquele trecho (`<saida>/<id>/cenas.tsv` e `cenas-N.jpg`). Um subagente por vídeo descreve ritmo,
tipo de imagem, imagem × fala (mostra, clima, texto, piada), abertura, fecho e sinais de edição feita por uma pessoa.

```
python3 -I .agents/skills/analise-de-formato/decupagem.py <video.mp4> <legenda ou <id>.txt> <pasta>/decupagem/
```

## 3b. Análise com pandas

```
uv run --no-project --with pandas python -I .agents/skills/analise-de-formato/analisar.py \
  data/cache/nicho/<Título>/ data/cache/nicho/<Título>/amostra.tsv --episodio data/episodes/<id>/episode.json
```

- **Desempenho:** cruza cada medida com log(views) e com views por inscrito (Spearman), por grupo.
- **Terços:** compara o terço de mais views com o de menos.
- **Curva:** traça o vídeo em décimos.
- **Nosso episódio:** mede o `episode.json` nas mesmas medidas, com planos por minuto no lugar de cortes.
- **Idioma:** só entram vídeos falados em português.
- **Saída:** `analise/resumo.md` e um CSV por tabela.
- **Amostra mínima:** para concluir, pelo menos 8 vídeos por grupo, de preferência 20. Com menos, o resumo avisa
  que é só descrição.

Pronto quando `analise/resumo.md` existe e o tamanho de cada grupo está escrito nele.

## 4. Fichas

- Um subagente para cada 2 vídeos, todos na mesma mensagem.
- Cada um preenche a [ficha-de-video.md](ficha-de-video.md) lendo só os arquivos do vídeo (`.txt`, folha,
  medidas).
- O prompt leva o caminho dos arquivos e da ficha, e nada do nosso roteiro: a ficha descreve o vídeo, não
  compara.

Pronto quando cada vídeo tem a ficha com as 6 seções. Seção sem material é marcada "sem dado".

## 4b. Batidas: a narrativa contada

As medidas do passo 3 contam palavras. A narrativa (o assunto, a tese, onde entra o caso, o conceito, "você" e
a confissão) só sai de leitura. Um agente marca as batidas e o script conta.

- **Marcação:** um subagente para cada 2 vídeos, todos na mesma mensagem, segue [batidas.md](batidas.md) e grava
  `research_notes/<Título>/formato/batidas/<id>.batidas.tsv`. Lê só a definição e a transcrição: nada de ficha,
  views ou roteiro nosso.
- **Nosso episódio:** a legenda (`captions.srt`) copiada com um id cego (`cego/V0N/V0N.srt`), marcada pelo mesmo
  método. Guarde qual id é qual na síntese.
- **Concordância:** um vídeo marcado por um segundo agente, em `batidas-concordancia/`. Abaixo de ~80% do tempo
  com o mesmo tipo, os tipos estão mal definidos: ajuste `batidas.md` antes de concluir.

```
python3 -I .agents/skills/analise-de-formato/narrativa.py medir <pasta>/batidas [--amostra amostra.tsv]
python3 -I .agents/skills/analise-de-formato/narrativa.py comparar <a.batidas.tsv> <b.batidas.tsv>
```

- **Saída:** `narrativa.csv` e `narrativa.md`, com a fatia do tempo em caso, conceito, "você" e narrador; o tempo
  de caso antes do conceito; quando "você" entra; confissões, ganchos e fecho; e a tese de cada vídeo.
- **`candidatos`:** procura frases típicas na transcrição. Na primeira rodada (2026-10-20) achou menos da metade
  das batidas do agente; serve só para conferir, não substitui a leitura.

Pronto quando cada vídeo da amostra e o nosso episódio têm o `.batidas.tsv`, e a concordância está escrita na
síntese.

## 4c. Molde e partitura: o nicho em números, no tamanho do episódio

O molde resume a amostra sem agente: para cada medida dos passos 3 e 4b, mediana, quartis e n (e o terço de mais
views contra o de menos, com 6 ou mais vídeos); para cada traço (confissão, gancho pago, fecho que volta, título
dito na fala, promessa explícita, bloco que abre com caso), em quantos vídeos aparece. `padrao` só com 8 ou mais
vídeos e 80% ou mais; o resto é `indicio`. Prevalência, não correlação com views: "12 de 13 fazem" é o que o
roteiro consegue seguir.

```
python3 -I .agents/skills/analise-de-formato/molde.py data/cache/nicho/<Título>/ \
  --notas docs/pesquisa/research_notes/<Título>/formato --grupo <grupo> [--assunto voce|obra|mundo|pensador]
python3 -I .agents/skills/analise-de-formato/partitura.py data/cache/nicho/<Título>/analise/molde.json \
  --duracao <min> --assunto <assunto> --episodio data/episodes/<id>
```

- `--grupo` escolhe o canal de referência do formato (o molde do ensaio é o grupo do Filosofatos, não a amostra
  inteira); `--assunto` restringe aos vídeos com batidas daquele assunto; `--amostra` troca o TSV de amostra
  (por exemplo o `amostra-topo.tsv` do passo 4d).
- **Dois moldes, não um.** O do canal de referência diz a forma que escolhemos; o do topo reproduzível do nicho
  (passo 4d) diz o que os vídeos mais vistos que a pipeline consegue refazer têm em comum. `comparar_moldes.py`
  põe os dois lado a lado: o que é `padrao` nos dois vai para a partitura sem discussão; o que diverge é
  decisão do dono.

```
python3 -I .agents/skills/analise-de-formato/comparar_moldes.py <a.molde.json> <b.molde.json> \
  --nomes Filosofatos Topo --saida data/cache/nicho/<Título>/analise/moldes-lado-a-lado.md
```
- A partitura escala o molde para a duração do episódio: marcos dos primeiros segundos absolutos, abertura e
  blocos proporcionais, blocos do tamanho do molde (menos blocos, não blocos menores; `--blocos` fixa), último
  décimo como fecho. Traz a linha do tempo com as casas, o que vale dentro de cada bloco, as curvas por décimo já
  no tamanho do episódio e os alvos (q1–q3) para medir o rascunho depois.
- Com `--episodio`, grava `partitura.md` e a cópia datada do molde (`molde.json`) na pasta do episódio, no
  desenho do `radar-brief.json` (ADR 018). Não sobrescreve sem `--sobrescrever`. O roteirista lê a partitura
  antes do outline (seção "Partitura do episódio" da skill `roteiro-explicativo`) e o `vp check` compara o
  roteiro com o molde copiado (ADR 031, partes C e D).
- Forma, nunca fato: nada do molde vira afirmação no roteiro; "você" continua preso às fichas.

Pronto quando `analise/molde.json` existe com o n de cada medida, e o episódio em curso tem `partitura.md` e
`molde.json` na pasta.

## 4d. Reproduzível: quem do nicho a pipeline consegue imitar

Views medem tema e tamanho do canal tanto quanto forma, e parte do nicho vive de coisa que a gente não faz:
pessoa falando para a câmera, cena de anime em movimento, gameplay. Antes de medir "o topo do nicho", separa-se
o que é reproduzível. A leitura é por subagente, nas folhas de quadros; a regra é código.

- **Leitura:** um subagente para cada 6 vídeos, todos na mesma mensagem, lendo só a folha de 32 quadros e as
  duas folhas densas de cada um (lista de ids e caminhos, sem canal nem views). Grava um TSV com as colunas
  `video_id`, `apresentador` (`nenhum` | `real` | `desenhado` | `avatar`; personagem de anime ou foto histórica
  não é apresentador), `quadros_com_apresentador` (0–32), `base_principal` (`anime_movimento` | `anime_parado` |
  `gameplay` | `filme_live_action` | `banco_de_imagens` | `foto_arquivo` | `ilustracao_propria` |
  `texto_grafico` | `pintura` | `misto`), `pct_base_principal`, `base_secundaria`, `texto_na_tela`
  (`legenda_queimada`, `palavra_chave`, `citacao`, `titulo_de_bloco`, separados por `;`), `movimento`
  (`em_movimento` | `parado_zoom` | `misto`, pelas folhas densas) e `nota`.
- **Regra:** reproduzível é sem apresentador e com base em banco, foto de arquivo, pintura, texto, ilustração
  própria ou quadro parado; anime em movimento, gameplay e filme não são; `misto` é parcial. Ilustração própria
  é reproduzível em princípio, mas custa arte (Workers AI tem teto editorial de 12 imagens por episódio):
  separe pintura e foto de arquivo de ilustração na síntese.

```
python3 -I .agents/skills/analise-de-formato/reproduzivel.py data/cache/nicho/<Título>/ <leitura-*.tsv> \
  [--minimo-views 400000] [--grupo TOPO]
```

Grava `analise/reproduzivel/reproduzivel.tsv` (veredito por vídeo) e `amostra-topo.tsv`, a amostra dos
reproduzíveis em português acima do mínimo de views, para o `molde.py --amostra`. As batidas (4b) desses vídeos
dão a estrutura do segundo molde.

Pronto quando cada vídeo da amostra tem veredito e o `amostra-topo.tsv` lista o topo reproduzível com o motivo.

## 5. Síntese

Você, coordenador, escreve a partir de `analise/resumo.md` e das fichas:
- uma tabela de padrões: o que se repete nos vídeos de mais views e falta nos de menos. Número vem do pandas;
  leitura vem das fichas;
- o nosso roteiro ao lado, nas mesmas medidas;
- de 5 a 8 recomendações, cada uma com os vídeos que a sustentam e a cena do nosso roteiro que muda;
- o que não dá para copiar (cena em movimento da obra, rosto do narrador) e o substituto possível.

Pronto quando cada recomendação aponta para pelo menos duas fichas.

## 6. Fechar

- **Na conversa:** as 3 mudanças que mais pesam no nosso roteiro, com um antes e depois de uma cena. Pergunte ao
  dono antes de mandar reescrever, porque a reescrita reabre a checagem e o gate 2.
- **Material baixado:** fica em `data/cache/`, fora do Git. Apague quando o dono disser que a análise acabou.

## Limites

- **Uso do material:** os vídeos baixados servem só para análise. Nenhum quadro, trecho de áudio ou frase longa
  vai para o nosso vídeo.
- **Ficha cita pouco:** trechos de até duas frases, com o minuto, para mostrar a forma.
- **Ritmo de edição:** o limiar de 0,3 conta cortes secos. Fusão e zoom lento não contam. Vídeo de quadro parado
  com zoom aparece com poucos cortes, mesmo trocando de imagem.
- **Legenda automática:** não tem pontuação e erra nomes. A ficha confere o nome na folha de quadros ou no título.
