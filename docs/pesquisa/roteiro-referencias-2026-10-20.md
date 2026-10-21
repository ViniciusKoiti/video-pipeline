# Como escrevem os canais de referência: Filosofatos e Inferno de Dante

Análise de 2026-10-20 para o dono, feita com a skill `analise-de-formato`. A pergunta é como os dois canais
escrevem e editam, e o que muda nas skills `roteiro-explicativo` e `humanizer-narracao`. Nenhum episódio foi
reescrito.

Acompanha a [análise do som de 18/10](por-que-o-nicho-soa-humano-2026-10-18.md) e a
[decupagem de 18/10](decupagem-cena-a-cena-2026-10-18.md).

## Resposta curta

- **Som.** É a maior diferença medida. Nenhum dos 23 vídeos fica em silêncio: de 0 a 0,5% do tempo. Os nossos
  ficam em silêncio de 9 a 10% do tempo, com 8 a 9 buracos por minuto. Uns 60% desses buracos estão na troca de
  cena, o que é montagem e não roteiro.
- **Abertura.** Nenhum dos 23 abre com um dado, e nenhum anuncia um mapa das partes. O Filosofatos abre com uma
  cena, uma confissão ou uma provocação. O Inferno de Dante abre com uma tese sobre a ficção e guarda o nome da
  obra por 1 a 2 minutos.
- **Fala sem fonte.** Os dois canais dizem o nome do pensador, mas quase nunca "segundo" ou "um estudo de Fulano".
  O `kira-voto-brasil` tem 15 marcas de fonte por mil palavras. O máximo da amostra é 5,1, e a mediana é 0,8 no
  Filosofatos e 0,2 no Inferno de Dante. A skill de roteiro ainda manda pôr "quem disse" na narração, o contrário
  da sua decisão de 18/10.
- **Voz do narrador.** Nos vídeos de política do Filosofatos, o narrador confessa nas viradas e vira a tese contra
  si no fecho. Só você pode escrever essas frases.
- **Duração.** Os dois canais fazem de 18 a 44 minutos (mediana de 23 a 25). Os nossos têm 6 e 13 minutos. A
  decisão é sua; ela está no fim.

## 1. Amostra e método

- **Canais:** `@filosofatosx`, com 13 vídeos: os 10 de mais views e os 3 de política e poder (voto, fascismo e
  Maquiavel). E `@infernodedante`, com 207 mil inscritos e 10 vídeos, sem os 17 comentários de capítulo de One
  Piece, a seu pedido.
- **Nossos:** `kira-voto-brasil` (6:19) e `death-note-fins-meios` (12:49), medidos pelo `episode.json` e pelo
  `final.mp4`.
- **Passos:**
  - coleta sem login;
  - download com cookies, numa cópia apagada ao fim;
  - medição de fala e cortes;
  - pandas;
  - som (`silencedetect` a −45 dB e 0,5 s, mais a fatia da fala com fundo sonoro);
  - 23 fichas, uma por vídeo, por agentes que não viram as views nem o nosso roteiro;
  - decupagem cena a cena de 7 vídeos, com o nosso lido às cegas como "V07".
- **Ressalvas:**
  - cada grupo é um canal só, então a correlação com views mede só a variação dentro do canal. Com 10 a 13 vídeos,
    ela é só descrição;
  - os 10 de mais views do Filosofatos não são de anime (Bíblia, psicologia, estoicismo). Só os 3 de política estão
    perto do nosso tema;
  - a legenda automática erra nomes e não tem pontuação;
  - a medida de fundo sonoro não separa música de ruído: a escuta separa.

## 2. Tabela: o que se repete

Medianas. "Fonte" conta "segundo", "de acordo com", "estudo", "pesquisa", "pesquisadores" e "artigo" por mil
palavras. "Eu" conta eu, meu, minha, pra mim e acho.

| | Filosofatos, 10 de mais views | Filosofatos, política (3) | Inferno de Dante (10) | `kira-voto-brasil` | `death-note-fins-meios` |
|---|---|---|---|---|---|
| Duração | 23 min (18 a 39) | 23 min (20 a 23) | 25 min (18 a 44) | **6,3 min** | **12,8 min** |
| Palavras por minuto | 185 | 181 | 181 | **147** | **156** |
| Abertura, até o 1º bloco | 59 s (18 a 215) | 192 s (78 a 205) | 107 s (63 a 153) | 44 s | 81 s |
| Tipo de abertura | confissão ou causo pessoal (5), provocação (4), cena de filme (1) | cena (2), confissão (1) | tese sobre a ficção (7), saudação (2), confissão de interesse (1) | **dado** | pergunta e **dado** |
| Capítulos | 6, com o título dito na fala | 6, com o título dito | 6 a 7 | nenhum | nenhum |
| "Você" por mil | 10,4 | 3,8 | 4,7 | **1,1** | 7,5 |
| "Eu" por mil | 11,9 | 10,5 | 8,6 | 6,5 | **1,5** |
| "A gente" por mil | 3,6 | 2,2 | 7,3 | 0 | 0,5 |
| Fonte na fala por mil | 0,9 | 0,5 | 0,2 | **15,1** | 5,0 |
| Perguntas ao espectador | 2 a 15 por vídeo | 1 a 5 | 0 a 6, e muito "né?" | 9 | 27 |
| Silêncio (−45 dB, ≥ 0,5 s) | 0,05% | 0% | 0% | **9,4%** | **10,2%** |
| Fala com fundo por baixo | 91% | 40% | 97% | **3%** | **4%** |
| Troca de imagem | plano médio de 0,7 a 125 s (jogo ou anime) | 1,3 a 1,4 s (anime cortado); jogo contínuo no Maquiavel | 1,9 a 12,5 s | 4,3 s | 4,8 s |
| Texto na tela | primeira frase ou título do capítulo palavra a palavra | nenhum | nenhum posto pela edição | 11 de 42 cenas (decupagem) | 6 citações, 6 tarjas, 2 palavras-chave (roteiro) |
| Chamada final | nenhuma em 8 de 10; comentário em 2 | nenhuma em 2; "Lê." em 1 | curtir, comentar, inscrever e ser membro | segue e comenta | segue e comenta |

Fontes: `data/cache/nicho/Referencias/medidas.csv`, `analise/som.csv`, `analise/episodio-*.csv` e as fichas em
`research_notes/Referencias/formato/`.

## 3. A escrita

### O assunto e a narrativa

O Filosofatos não fala do anime: o anime é só fundo de imagem. O assunto é quem assiste, e a mensagem é um espelho:
uma ideia grande explica algo que você faz sem perceber, e o narrador também faz. Ele fecha virando a tese contra
si ("isso eu não sei se eu consigo não", `3IHyC_29COI`, 20:03; "mais de mim sentado no chão da cozinha",
`_wkpaPhYaLU`, 22:25). Quem conta a obra é o Inferno de Dante.

| | Filosofatos | Inferno de Dante | `kira-voto-brasil` |
|---|---|---|---|
| Assunto | você | a obra | o Brasil |
| Caso | experimento, história, confissão | cenas do anime, de 2 a 3,5 min | a obra e dados |
| Mensagem | "você também faz isso" | "veja como a obra é genial" | "isto é o que acontece no país" |
| Fecho | a tese contra o narrador | pede curtida, comentário e membro | o veredito do dono |

**Decisão do dono (2026-10-20):** o nosso ensaio fala sobre quem assiste, no molde do Filosofatos. A obra entra como
um caso entre outros. Como as fichas não dizem nada sobre o espectador, "você" entra de três jeitos:

- pergunta ("E você, julgaria pelo resultado?");
- hipótese marcada ("Pensa na última vez que…");
- frase do dono, marcada como opinião ou confissão (ADR 019).

Nunca como fato sobre o que quem assiste faz.

### A narrativa medida (batidas, passo 4b)

Sete vídeos marcados batida a batida por agentes que leram só a transcrição (`batidas.md`), contados por
`narrativa.py`. É descrição, não conclusão: são 3 do Filosofatos, 2 do Inferno de Dante e os nossos 2. V07 é o
`kira-voto-brasil` e V08 é o `death-note-fins-meios`, marcados às cegas.

| Vídeo | Assunto | Abertura | % caso | % "você" | % narrador | Confissões | Fecho contra si | Chamadas |
|---|---|---|---|---|---|---|---|---|
| FILO voto | você | 192 s | 64 | 10 | 6 | 3 | sim | 0 |
| FILO Maquiavel | pensador | 114 s | 52 | 9 | 6 | 1 | sim | 1 ("Lê.") |
| FILO fascismo | mundo | 205 s | 24 | 7 | 12 | 3 | sim | 0 |
| DANTE deus (FMA) | obra | 122 s | 46 | 5 | 15 | 1 | não | 2 |
| DANTE vilão | obra | 122 s | 43 | 0 | 16 | 0 | não | 2 |
| nosso `kira` | mundo | 44 s | 25 | 10 | 5 | 0 | não | 1 |
| nosso `death-note` | obra | 81 s | 41 | 15 | 2 | 0 | não | 1 |

"% você" soma APLICA e PERGUNTA; "% narrador" soma CONFISSAO e OPINIAO. Tabela completa, com o tempo de caso antes
do conceito e os ganchos, em `research_notes/Referencias/formato/batidas/narrativa.md`.

- **"Falar de você" não é mais "você" na fala.** Os nossos falam de quem assiste tanto ou mais (10 e 15% do
  tempo; o `death-note` faz 9 perguntas a cada 10 min, o Filosofatos de 2 a 2,5). O que o Filosofatos tem e nós
  não temos é o narrador exposto: de 1 a 3 confissões e o fecho virado contra si nos 3 vídeos. Os nossos têm zero
  das duas coisas.
- **O assunto nem sempre é "você".** Dos 3 de política, só o do voto tem assunto `voce`; o do fascismo é `mundo` e
  o do Maquiavel é `pensador`. O que se repete nos três é a voz: o fecho volta para quem assiste e para o narrador.
  Os 10 mais vistos (amor, autoestima, internet morta) não foram marcados.
- **Abertura.** De 114 a 205 s no Filosofatos e 122 s no Inferno de Dante; 44 e 81 s nos nossos.
- **Caso.** De 24 a 64% do tempo no Filosofatos; 25% no `kira`. Caso longo antes do conceito só aparece com
  clareza no vídeo do voto (mediana de 84 s por bloco) e no de Fullmetal (48 s). No fascismo e no Maquiavel, o
  conceito vem antes na maioria dos blocos.
- **Concordância.** Dois agentes marcaram o vídeo do voto sem se ver: mesmo tipo em 92% do tempo, os mesmos 5
  capítulos, 4 pontes, 5 aplicações e 3 confissões. As maiores trocas foram APLICA × OPINIAO (33 s) e
  CONCEITO × APLICA (24 s).
- **Regra ajustada depois da rodada.** Os dois agentes engoliram a mesma confissão de 4 s (02:28) pela regra de
  "trecho curto". A definição agora marca `CONFISSAO` e `PERGUNTA` mesmo quando são uma frase só; as contagens de
  confissão acima podem estar um pouco baixas.
- **Procura automática (`candidatos`).** As frases típicas na transcrição acharam menos da metade das batidas dos
  agentes. Fica só como conferência.

#### Os 10 mais vistos do Filosofatos (segunda rodada, com a regra nova)

Medianas por grupo. Os 10 de cima (417 mil a 674 mil views) foram marcados já com a regra que conta confissão e
pergunta de uma frase só; os 3 de política, não. Por isso as confissões dos 10 podem estar infladas em relação aos 3.

| Grupo | Assunto `voce` | Abertura | % caso | % "você" | % narrador | Confissões (por 10 min) | Fecho volta | Fecho contra si | Com chamada |
|---|---|---|---|---|---|---|---|---|---|
| Filosofatos, 10 de cima | 7 de 10 | 131 s | 31 | 12 | 20 | 4,5 (2,1) | 9 de 10 | 4 de 10 | 3 de 10 |
| Filosofatos, política | 1 de 3 | 192 s | 52 | 9 | 6 | 3 (1,3) | 2 de 3 | 3 de 3 | 1 de 3 |
| Inferno de Dante | 0 de 2 | 122 s | 44 | 3 | 16 | 0,5 (0,2) | 2 de 2 | 0 de 2 | 2 de 2 |
| nosso `kira` | não (`mundo`) | 44 s | 25 | 10 | 5 | 0 | sim | não | sim |
| nosso `death-note` | não (`obra`) | 81 s | 41 | 15 | 2 | 0 | sim | não | sim |

Os três que não são `voce` entre os 10: a Bíblia (`obra`), a internet morta (`mundo`) e o estoicismo
(`pensador`). Tabela por vídeo em `research_notes/Referencias/formato/batidas/narrativa.md`.

- **"Você" como assunto aparece em 7 dos 10 de cima.** Combina com a sua escolha, mas não prova que é o assunto
  que traz a audiência: os 10 foram escolhidos por views dentro de um canal que já tem público, e não há um grupo
  de baixo do mesmo canal com outro assunto para comparar. O de política com assunto `voce` (o do voto) é o de
  menos views, mas tinha 4 dias.
- **A maior diferença para nós é a voz do narrador.** Opinião e confissão ocupam 20% do tempo nos 10 de cima e de
  2 a 5% nos nossos. As confissões não ficam só na abertura e no fecho: espalham-se pelo vídeo inteiro (num deles,
  14 em 24 min).
- **"Você" na fala, nós já temos.** Os 10 de cima ficam em 12% do tempo; os nossos, em 10 e 15%.
- **O fecho volta à abertura em 9 de 10.** O fecho contra si aparece em 4 de 10: nos de política era 3 de 3, mas
  não é regra do canal.
- **Pedir algo no fim é exceção:** 3 dos 10.
- **Caso e conceito variam muito:** de 13 a 80% do tempo em caso. Não há uma proporção que se repita.
- **O exemplo de roteiro com as 3 confissões aprovadas** (`exemplo-roteiro-ensaio-voce-2026-10-20.md`) fica em
  cerca de 6 por 10 min, acima da mediana dos 10 de cima (2,1), por ser curto. Em 12 min, 3 confissões dariam 2,5
  por 10 min.
- **Critérios que os agentes aplicaram de jeitos diferentes:** abertura como bloco 0 ou já como capítulo 1; título
  de capítulo não anunciado; pergunta de muleta ("né, cara?"). A concordância foi medida num vídeo só; vale medir
  num segundo antes de usar os números em regra.

### Abertura: quanto dura e como prende

- **Filosofatos, política:**
  - **voto:** abre com um experimento real contado como cena, com lugar, ano e prancheta (`3IHyC_29COI`, 00:00). O
    título só é dito aos 112 s, como paradoxo;
  - **fascismo:** abre com uma confissão pequena, o narrador xingando o professor (`_wkpaPhYaLU`, 00:01);
  - **Maquiavel:** abre com a conspiração de 1478, com detalhe físico, e liga a cena ao autor só aos 70 s
    (`4YDCskeIGKM`).
- **Filosofatos, mais vistos:** são mais curtos, de 18 a 60 s, com provocação na segunda pessoa (`QVFErIvhBy8`,
  `W5FXAMzyfIc`, `-zC6SxusjFw`) ou confissão (`lKRBXVeL6yc`, `rkYvaxINmqI`, `tF77QLsI75o`). Seis mostram a
  primeira frase ou o título do capítulo palavra a palavra nos primeiros 2 a 3 s.
- **Inferno de Dante:** começa por uma tese sobre a ficção ("o vilão", "o retorno", "o gênio") e guarda o nome da
  obra até 1:30 ou 1:45 (`vLCrM8SlAjM`, `hrP4nTiOsZE`, `M6jx3yr4Wto`, `21JxU6P0DDk`). Depois vem o aviso de spoiler.
- **Nenhum dos 23** abre com um número nem anuncia "vou passar por três partes". A promessa vem como pergunta,
  como paradoxo ou como o que o vídeo não vai fazer (`_wkpaPhYaLU`, 00:57).
- **Nossos:**
  - `kira`: abre com um dado da obra e um percentual, a pergunta e o mapa de três partes (S01 a S05, 44 s). O
    agente às cegas classificou a abertura como "dado";
  - `death-note`: abre com uma pergunta ao espectador e o dado dos doze agentes.

### Como o vídeo é dividido

- Os dois canais usam 6 ou 7 capítulos. No Filosofatos, o título do capítulo é **dito na fala** e aparece em
  cartela ("o escocês e o padre", `3IHyC_29COI`, 03:12). O fim de cada bloco aponta para o próximo.
- **Fio:**
  - uma pergunta que volta ("por que ninguém muda de voto", "quem é a pessoa que não posta?");
  - ou uma vida em ordem (Maquiavel, `4YDCskeIGKM`);
  - ou uma tese provada por um caso só (`21JxU6P0DDk`, `c065Xbs89x8`).
- **Ganchos plantados e pagos:** "Guarda o nome Tito Lívio porque eu vou falar dele lá no final" (`4YDCskeIGKM`,
  01:51, pago em 22:26). Também em `lKRBXVeL6yc` (22:41), `jCyACuBn8pM` (13:55 → 39:04) e `d24OSR54q5g`
  (08:52 → 28:37).
- **Nossos:** sem capítulos. O `kira` anuncia as partes no começo (S04) em vez de dizer o título de cada uma
  quando ela chega. Os dois já retomam um ponto plantado: "a frase do começo" (S17) e "os doze agentes" (S115).

### Quanto tempo de caso ou cena vem antes do conceito

| Vídeo | Caso antes do conceito |
|---|---|
| `3IHyC_29COI` (voto) | 1 a 2,5 min de experimento por bloco |
| `4YDCskeIGKM` (Maquiavel) | 2:15 de Borgia antes de "satisfeito e estupefato" |
| `hrP4nTiOsZE` (deus) | 2 a 3,5 min de resumo antes da leitura |
| `vLCrM8SlAjM` (vilão) | 20 a 60 s |
| `c065Xbs89x8` (retorno) | 10 min de recap, o caso extremo |

- **Exceção:** nos blocos de ideia do Maquiavel e no fascismo, o conceito vem primeiro e o exemplo do dia a dia
  depois.
- **Pensador como personagem:** o filósofo entra numa cena com idade, lugar ou anedota (Hume jovem na França,
  `3IHyC_29COI`, 03:12; Maquiavel aos 9 anos, `4YDCskeIGKM`). Não entra como autoridade citada.
- **Nossos:**
  - `kira` conta os agentes do FBI (S29 a S34) antes de Locke (S35);
  - `death-note` anuncia o pensador antes do caso em alguns blocos ("Se você quer uma régua para esse caso, ela vem
    de Immanuel Kant", S117).

### Primeira pessoa, "você" e "a gente"

- **Filosofatos:** "eu" alto (10 a 12 por mil). Confessa nas viradas: "eu teria feito a mesma merda"
  (`3IHyC_29COI`, 02:28). Usa "você" para acusar e aplicar: "Esse vídeo aqui é sobre você faz uns bons minutos"
  (13:16).
- **Inferno de Dante:** "a gente" é a pessoa mais alta (7,3 por mil), como fã que assiste junto. O "eu" é de
  opinião sobre a obra.
- **Nossos:**
  - `kira`: "você" quase só no fim (1,1 por mil) e "a gente" em zero;
  - `death-note`: tem "você" (7,5 por mil), mas quase não tem "eu" (1,5 por mil).

### Perguntas ao espectador

- **Filosofatos:** de 2 a 15 por vídeo, quase todas retóricas e respondidas na hora. Usa ordens no lugar de
  pergunta ("tenta fazer a lista", `_wkpaPhYaLU`, 06:51; "conta comigo", 20:00).
- **Inferno de Dante:** quase não pergunta. A muleta é o "né?".
- **Nossos:** o `death-note` faz 27 perguntas em 13 min, mais que qualquer um dos 23 por minuto. O `kira` faz 9.

### Palavras por minuto

- Eles falam de 170 a 196 palavras por minuto, e o ritmo fica estável do começo ao fim (178 a 195 por décimo no
  Filosofatos).
- Nós ficamos em 147 e 156. O motivo está na voz e nas pausas, não só no texto: 9 a 10% do nosso tempo é
  silêncio.

### Como a opinião aparece

- **Filosofatos:**
  - marca com "eu acho" ou confissão: "Eu acho que as pessoas são boas na média." (`4YDCskeIGKM`, 23:05);
  - ou dá um veredito seco, sem marca (`QVFErIvhBy8`, `cY5asjgdvuc`, `-zC6SxusjFw`);
  - nos de política, declara que não toma partido e testa os dois lados: "E deu empate." (`3IHyC_29COI`, 12:47).
- **Inferno de Dante:** "na minha opinião", às vezes 7 vezes num vídeo (`Jgy_a6rWJPE`).
- **Nossos:** a opinião do dono aparece marcada ("Pra mim…", S25, S27 e S38) e com o argumento contrário (ADR 019).
  É a mesma forma deles.

### Fecho e chamada

- **Filosofatos:** volta à cena da abertura e vira a tese contra o narrador: "ainda não recuperei aquele caderno"
  (`_wkpaPhYaLU`, 22:41); "isso eu não sei se eu consigo não" (`3IHyC_29COI`, 20:03). Em 10 de 13 vídeos não há
  chamada. Onde há, ela é um comentário ligado à história do vídeo (`rkYvaxINmqI`, 35:22).
- **Inferno de Dante:** retoma a pergunta do título e faz a chamada completa (curtir, comentar, compartilhar,
  inscrever e ser membro).
- **Nossos:** os dois fecham com "E você?" e "Segue o canal e comenta a sua resposta". São duas chamadas numa, e a
  nossa skill diz "uma chamada só". Nenhum dos dois volta à cena da abertura.

## 4. O som

- **Silêncio:** zero nos 23 vídeos. Mesmo onde a trilha some, a fala vem emendada.
- **Fundo sonoro:**
  - Inferno de Dante: 96 a 99% da fala tem fundo, num nível constante, ~47 dB abaixo da voz;
  - Filosofatos: varia de 30 a 98%. Nos vídeos de política o fundo cobre a abertura e o fecho e baixa no meio (no
    do fascismo, 86% no primeiro décimo e de 24 a 50% depois).
- **Nossos:**
  - 9,4% e 10,2% de silêncio, com fundo em 3 a 4% da fala;
  - **onde está o silêncio:**

    | | Silêncio na troca de cena | Silêncio dentro da cena | Marcas `<short pause>` |
    |---|---|---|---|
    | `kira` | 30 buracos, 20 s | 19 buracos, 16 s | 10 |
    | `death-note` | 77 buracos, 49 s | 40 buracos, 30 s | 13 |

  - **leitura:** a maior parte do silêncio é montagem (o respiro entre os WAVs). A outra parte vem da voz entre as
    frases e das marcas de pausa.
- **Entrega:** a escuta de 18/10 ainda vale. A medida não diz se eles riem ou hesitam. A transcrição deles mostra
  autocorreção e digressão assumida ("Não tem nada a ver com o assunto. Eu só acho que merecia ser lembrado.",
  `_wkpaPhYaLU`, 13:43).

## 5. A duração

- Os dois canais fazem ~20 minutos, e o Filosofatos põe "(pra ouvir enquanto faz outra coisa)" no título. A
  imagem é fundo: jogo ou anime sem relação com a fala (52 de 52 cenas "clima" no Maquiavel; 0 cenas "mostra" no
  voto e no fascismo). Quem ouve não precisa olhar.
- **Nosso caso:**
  - a imagem é feita para ser vista (cartões, números, quadros da obra), e cada afirmação precisa de ficha;
  - 20 minutos pedem umas 3.600 palavras: o `death-note` tem 2.000 e o `kira` tem 930;
  - o fundo "pra ouvir" deles depende de material em movimento de terceiros, que não usamos.
- **O que a amostra não diz:** se 20 minutos funcionariam para nós. Não temos retenção própria.

## 6. Recomendações

Cada uma tem as fichas que a sustentam e a cena nossa que mudaria.

1. **Abrir com cena, confissão ou provocação; o número vem depois.**
   - **Sustentação:** `3IHyC_29COI`, `4YDCskeIGKM`, `_wkpaPhYaLU`, `tF77QLsI75o`, `QVFErIvhBy8`. Nenhum dos 23 abre
     com dado ou mapa.
   - **Cena:** `kira` S01 a S05. O S04 sai, e as três partes viram títulos ditos quando chegam.
   - **Regra:** a cena sai de ficha (lugar, data e objeto). A confissão é do dono.
2. **Dividir em capítulos com o título dito na fala, e abrir cada bloco pelo caso.** O pensador entra como
   personagem da cena.
   - **Sustentação:** `3IHyC_29COI` (títulos lidos; 1 a 2,5 min de caso), `4YDCskeIGKM` (Borgia), `hrP4nTiOsZE`,
     `tF77QLsI75o`.
   - **Cenas:** `kira` S11 e S29; `death-note` S117 ("Se você quer uma régua…").
   - **No vídeo:** o título vai num `keyword`; o capítulo vai na descrição.
3. **Fala sem fonte:** o nome do pensador fica; "segundo", "um estudo de Fulano" e "Fulano nota" saem.
   - **Sustentação:** `3IHyC_29COI` dá pesquisador sem nome, com lugar, ano e amostra ("Um professor de Yale",
     10:00). `21JxU6P0DDk` dá a crítica sem nome ("muita gente critica", 14:27). Mediana de 0,2 a 0,9 contra os
     nossos 15,1.
   - **Cenas:** `kira` S08, S22, S23, S33 e S34.
   - **Exceção que fica:** controvérsia atribuída no perfil de poder ("o órgão X acusou…"), por risco jurídico.
4. **Sem buraco de som.**
   - **No roteiro:** no máximo uma `<short pause>` por minuto e nenhuma pausa no fim de cena. Juntar cenas curtas
     seguidas reduz trocas.
   - **Na montagem, fora das skills:** emendar as cenas sem o respiro dos WAVs.
   - **A trilha:** decisão sua (seção 8).
   - **Sustentação:** `4YDCskeIGKM` ("a fala corre sem interrupção"), `3IHyC_29COI`, `vLCrM8SlAjM` e as 23 medidas.
   - **Cenas:** `kira` S08 e S09 viram uma; S10 perde a pausa.
5. **Frases do dono nas viradas e no fecho:** uma confissão no começo e a tese virada contra si no fim.
   - **Sustentação:** `3IHyC_29COI` (02:28, 20:03), `_wkpaPhYaLU` (00:25, 22:25), `4YDCskeIGKM` (23:01),
     `tF77QLsI75o` (22:54).
   - **Cenas:** `kira` S01 e S38; `death-note` S156 e S151.
   - **Regra:** o agente pede essas frases ao dono e nunca as escreve (ADR 019).
6. **O fecho volta à cena da abertura, sem lição.**
   - **Sustentação:** `3IHyC_29COI` (a prancheta), `_wkpaPhYaLU` (o caderno), `YNnt7fkA2T0` (o quarto de
     madrugada), `68ZQYG9YbXU` (do Kung Fu Panda à formiga).
   - **Cenas:** `kira` S38 voltaria à imprensa e à frase de S01. `death-note` S151 voltaria aos doze agentes.
7. **Uma chamada só, ligada à história.**
   - **Sustentação:** `rkYvaxINmqI` (35:22) e `lKRBXVeL6yc` (33:25) pedem um comentário sobre o que o vídeo contou.
     8 dos 10 mais vistos do Filosofatos não pedem nada.
   - **Cenas:** `kira` S40 e `death-note` S134: "Segue o canal e comenta" vira uma coisa só.
   - **Regra:** a ADR 026 manda o topo pedir para seguir ou compartilhar. Ver os conflitos abaixo.

## 7. Conflitos com as nossas regras

| Padrão deles | Nossa regra | O que fazer |
|---|---|---|
| "Guarda o nome Tito Lívio" (`4YDCskeIGKM`, 01:51) | o humanizer proíbe "Guarde esse nome." como frase de efeito | permitir só quando o nome volta mais tarde no vídeo, com o pagamento na cena |
| Nenhuma chamada no fim (Filosofatos) | ADR 026: o topo pede seguir ou compartilhar | manter a ADR; trocar "segue e comenta" por uma chamada só |
| Veredito seco, sem "eu acho" (`QVFErIvhBy8`, `-zC6SxusjFw`) | ADR 019: opinião dita como opinião | manter a marca "Pra mim…" |
| Exemplo do dia a dia como se fosse fato ("eu duvido que você tenha atravessado um inventário…", `4YDCskeIGKM`, 13:20) | regra 2: nada sem ficha | só como hipótese marcada ("Pensa numa…", como no S144), nunca como fato sobre quem assiste |
| Pesquisador sem nome na fala | regra 2: toda claim tem `source_ids` | a fonte fica no rodapé; a fala tira o nome, não a ficha |
| "Quem disse vai na narração" (item 7 da skill de roteiro) | decisão do dono de 18/10: a fala não cita fonte | mudar a skill (recomendação 3) |

## 8. O que não copiar

- **Cena em movimento da obra:** anime, jogo e filme rodando ao fundo são material de terceiros. No nosso vídeo, só
  entra quadro oficial parado (ADR 007, `Citacao`, até 10 por vídeo e 8 s cada). O substituto é o B-roll de banco
  como textura (ADR 031), que já faz o papel de "clima".
- **Rosto filmado:** os 10 vídeos do Inferno de Dante mostram o rosto do narrador filmado, em 6 a 25% dos quadros. Fica fora até a decisão
  sobre o apresentador (ADR 017).
- **Nenhuma frase deles:** as fichas citam no máximo duas frases, só para mostrar a forma. "Calma que eu chego lá",
  "conta comigo" e "pra ouvir enquanto faz outra coisa" não entram no nosso roteiro nem no título.
- **Pedido de membro e de "coquinha":** é do canal deles.

## 9. Decisões do dono

1. **Duração:** 6 a 8 min (o que temos) ou ~20 min (o que eles fazem).
2. **Trilha:** a ADR 030 está proposta. O custo da licença é zero: a YouTube Audio Library é gratuita e não sofre
   reivindicação do Content ID no YouTube. Ela não cobre o uso fora do YouTube, então o corte para Reels sai sem
   ela.
3. **Regras nas skills:** quais das 7 recomendações viram regra em `roteiro-explicativo` e `humanizer-narracao`.
4. ~~**Assunto do ensaio:** a obra ou quem assiste.~~ **Decidido em 2026-10-20:** quem assiste (seção 3, "O assunto
   e a narrativa").

## Arquivos

- **Fichas:** `research_notes/Referencias/formato/<id>.md` (23).
- **Decupagem:** `research_notes/Referencias/formato/analise/decupagem-fichas.jsonl` (7 vídeos, o nosso às cegas).
- **Medidas, som e pandas:** `data/cache/nicho/Referencias/` (`medidas.csv`, `janelas.csv`, `analise/`), fora do
  Git.
- **Script de som:** escrito nesta sessão, fora da skill. Ainda não está no passo 3 da `analise-de-formato`.
- **Material baixado:** fica em `data/cache/nicho/Referencias/` até o dono dizer que a análise acabou.
