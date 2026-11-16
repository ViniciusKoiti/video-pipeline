# Cena e Conceito (@cenaeconceito): o que deu certo, o que não deu e por quê (2026-11-08)

Análise só de leitura, a pedido do dono, para decidir o próximo passo editorial. Nada foi consultado fora do repositório (sem vidIQ, sem Studio, sem render). Nenhum outro arquivo foi alterado.

## Conclusão (5 linhas)

1. Em ~20 dias o canal tem 9 inscritos e 1.790 views. Os 12 vídeos longos somam 839 views (mediana 55; calculado aqui) e os 9 Shorts, ~949 (53%). O critério do piloto (≥ 5 mil views em 28 dias) falhou por ordem de grandeza: `death-note-fins-meios` tem 7 views em 19 dias.
2. O que se destacou, com n minúsculo: `montaigne-desapego` (261 views, 28,4% assistido), `ayanokoji-ser-parecido` (146 em 7 dias) e "A pausa" (96 em 4 dias): promessa pessoal e prática ligada a um pensador. Também três Shorts curtos de autoajuda estoica (869 views juntos).
3. Nenhum longo tem cauda: os seis longos mais antigos somaram 22 views em 7 dias (01 a 08/11), e 62% a 85% das views de cada um vieram nos três primeiros dias de relatório.
4. A explicação mais provável é distribuição (canal novo, sem público semente) somada à falta de recorte (5 linhas e ao menos 6 públicos declarados em 19 dias). Embalagem, retenção e tema não se separam: não há impressões, CTR nem origem de tráfego registrados (zero leituras em `metrics.json`).
5. A leitura ainda é sujeita a ruído operacional: títulos ao vivo diferentes dos agendados, dois vídeos não listados, um sem miniatura nem tags, itens do Studio nunca registrados. Recomendação central: fechar o ciclo D7 antes de produzir mais, e fixar um recorte de 4 vídeos (CLAUDE.md §12).

Siglas das fontes: **[VIQ]** = `docs/pesquisa/vidiq-como-era-a-vida-2026-11-08.md` (§4, snapshot de 08/11); **[TEMAS]** = `temas-cena-conceito-2026-11-01.md`; **[CRESC]** = `crescimento-youtube-embalagem-hipoteses-2026-10-23.md`; **[DIAG]** = `diagnostico-fluxo-2026-11-07.md`; **[REG]** = `data/publicacoes/registro.jsonl`; **[MJ]** = `data/episodes/<id>/metrics.json`; **[PUB]**, **[PAUTA]**, **[POST]**, **[EP]** = `publicacao.md`, `pauta.md`, `post.json`, `episode.json` do episódio. "Calculado aqui" = conta minha sobre números dos arquivos. Grau de confiança: **evidência** (dado direto), **indício** (dado direto, mas confundido), **hipótese** (inferência sem teste).

---

## 1. Situação em números

### 1.1 Canal

- Criado em 2026-10-19; 9 inscritos; 1.790 views; 22 vídeos (13 "longos" + 9 Shorts, segundo o vidIQ) [VIQ §4]. O vidIQ classifica como longo o vídeo vertical de 0:57 ("Herói vs. Vilão", 2 views); tratado abaixo como Short na soma.
- Views diárias do canal: 10 (23/10) → 97 (27/10) → 495 (01/11) → 1.373 (04/11) → 1.790 (08/11) [VIQ §4]. De 01 a 04/11 entraram 878 views em 3 dias (~293/dia), de 04 a 08/11 só 417 em 4 dias (~104/dia; calculado aqui). A data do Short de 546 views não consta em nenhum arquivo, então não dá para atribuir o salto a ele (lacuna).
- Dos 46 agendamentos no `registro.jsonl`, 13 foram para o Cena e Conceito (8 com o id antigo do canal, 5 com o novo) e 33 para outras contas (Nabote, MEI, Instagram, @viniciusnakahara, @baixo.nivel.dev.s etc.); calculado aqui sobre [REG]. Um dos 13 (Ayanokoji, 31/10) nunca saiu [PUB ayanokoji-ser-parecido, "Reagendamento"].

### 1.2 Vídeos longos

Janela = dias entre a data de publicação do vidIQ e 08/11, sem horário (calculado aqui). Views/dia = views ÷ janela, só ordem de grandeza (a distribuição é concentrada nos primeiros dias, ver §1.4). "Breakout" é o do vidIQ [VIQ]: inferi que ele é views ÷ ~43,5, a mediana do canal (261 ÷ 6,0 e 146 ÷ 3,4 dão ~43), ou seja, "acima da mediana de uma base minúscula".

| # | Vídeo (título ao vivo, vidIQ) | Episódio | Publ. (vidIQ) | Dur. | Linha | Janela | Views | Views/dia | Breakout | Retenção / CTR conhecidos |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Por que torcemos pelo Light? (Death Note) | `death-note-fins-meios` | 20/10 | 12:49 | anime + filosofia (nome da obra) | 19 d | 7 | 0,4 | — | 0 views nos 3 dias do relatório de 21–23/10; "não interpretável" [TEMAS] |
| 2 | Kira teria voto no Brasil? | `kira-voto-brasil` | 21/10 | 6:19 | anime + sociedade | 18 d | 67 | 3,7 | 1,5x | 57 views em 22–24/10, 1:13 médio, 19,52% assistido [TEMAS] |
| 3 | E se o Light tivesse ganhado? | `historia-vencedores` | 22/10 | 12:40 | anime + opinião (molde Filosofatos) | 17 d | 9 | 0,5 | — | 1 view em 23–25/10, 28 s, 3,74% [TEMAS] |
| 4 | O Que Não Está na Sua Mão \| Epicteto… | `epicteto-na-sua-mao` | 23/10 | 11:32 | estoicismo, pensador (molde "topo") | 16 d | 88 | 5,5 | 2,0x | 60 views em 24–26/10, 1:32, 13,32% [TEMAS] |
| 5 | Porquê Montaigne não era bonzinho? | `montaigne-desapego` | 27/10 (agendado 26/10 18h) | 11:43 | filosofia, pensador | 12 d | **261** | 21,8 | 6,0x | 162 views em 28–30/10, 3:19, **28,40%** [TEMAS] |
| 6 | A manipulação que não precisa de mentira \| Orwell | `manipulacao-linguagem-politica` | 29/10 (22h BRT de 28/10) | 11:39 | manipulação / política | 10 d | 75 | 7,5 | 1,7x | 68 no contador e 48 no Analytics amplo em 01/11 [TEMAS] |
| 7 | Cansada de carregar tudo? A lição estoica… | `estoicismo-mulheres-inabalavel` | 31/10 (agendado 30/10 12h) | 17:03 | estoicismo p/ mulheres (fala direta) | 8 d | 43 | 5,4 | — | nada registrado |
| 8 | Como se parecer mais com o Ayanokoji: Epicteto aprovaria? | `ayanokoji-ser-parecido` | 01/11 (o `metrics.json` diz 02/11 18h) | 12:35 | anime (personagem) + estoicismo | 7 d | 146 | 20,9 | 3,4x | nada registrado |
| 9 | "Não dê nem água": quem ganha quando o povo se divide? | `boicote-divisao-arendt` | 03/11 | 7:41 | política | 5 d | 9 | 1,8 | — | nada registrado |
| 10 | A pausa: o guia estoico para decidir antes de reagir | `guia-mastermind-estoico` | 04/11 | 12:13 | estoicismo + anime (clipes) | 4 d | 96 | 24,0 | 2,2x | nada registrado |
| 11 | Como não explodir quando alguém te provoca — Ayanokoji e Epicteto | `ayanokoji-provocacao-epicteto` | 05/11 (22h44 de 04/11 BRT), **não listado** | 10:00 | anime + estoicismo | 3 d | 5 | 1,7 | — | nada registrado |
| 12 | Como era ser rico na Idade Média? | `idade-media-ser-rico` | 07/11 18h BRT | 8:40 | "como era ser X" (reconstrução, IA) | **1 d** | 33 | 33 (1º dia) | 3,3x | nada registrado |

Fontes das datas de agendamento, canal e visibilidade: [REG] eventos `agendado`/`pacote`, [POST] e [PUB] de cada episódio. Durações conferem com [EP]/[MJ] (ex.: 519 s ≈ 8:40 em `idade-media-ser-rico`).

Sem retenção/CTR/impressões, qualquer linha acima é só views. Os únicos dados de Studio/Analytics locais são os de [TEMAS] (consulta de 01/11, três datas por vídeo depois da publicação, "não são primeiras 72 horas exatas") e a frase de [PUB]/[PAUTA] de `idade-media-ser-rico`: "ensaios anteriores do canal (66 a 260 views, 24 a 27% assistido)", dado do dono segundo [VIQ §4]. No relatório amplo de 04/10 a 01/11, Montaigne tem 258 views, 84 engaged views, 3:15 médios e 27,80% [TEMAS].

### 1.3 Shorts (à parte)

| Short | Duração | Views | Breakout |
|---|---|---|---|
| A técnica infalível para lidar com gente invejosa | 29 s | 546 | 12,6x |
| O hábito noturno que separa os homens comuns dos melhores | — | 170 | — |
| Como os manipuladores usam a sua mente #deathnote | — | 153 | 15x |
| 6 outros | — | entre 4 e 51 (soma ≈ 80 por diferença) | — |
| "Herói vs. Vilão: a armadilha da moralidade" (0:57, classificado como longo pelo vidIQ) | 0:57 | 2 | — |

[VIQ §4]. Soma dos Shorts por diferença: 1.790 − 841 = 949 views (calculado aqui); os três maiores = 869 (48,5% do canal).
**Nenhum desses Shorts tem arquivo, pauta ou registro no repositório** (busca por "invejosa", "hábito noturno" e "manipuladores usam" só acha o arquivo do vidIQ; [REG] não tem postagem de Short no Cena e Conceito). Origem e data de publicação são lacuna. Os Shorts técnicos do projeto (Java, C) vão para outros canais.

### 1.4 O que se calcula

- **Peso dos Shorts:** 949 de 1.790 views (53%) contra 841 (47%) dos longos. Os três Shorts maiores sozinhos (869) superam a soma dos 12 longos (839). Calculado aqui.
- **Views por longo:** média 69,9 e mediana 55 nos 12 longos "de verdade" (839 ÷ 12); média 64,7 e mediana 43 incluindo o 0:57. Cinco dos 12 têm ≤ 9 views.
- **Concentração:** Montaigne = 31% das views dos longos; Montaigne + Ayanokoji + "A pausa" = 503 (60%).
- **Por linha** (soma das views dos longos, calculado aqui): anime + filosofia/sociedade (#1–3) = 83 em 3 vídeos; estoicismo/filosofia com pensador (#4, 5, 7, 10) = 488 em 4; Ayanokoji (#8, 11) = 151 em 2; política/manipulação (#6, 9) = 84 em 2; "como era ser X" (#12) = 33 em 1 (um dia).
- **Cauda:** comparando [TEMAS] (01/11) com [VIQ] (08/11), os seis longos mais antigos ganharam em 7 dias: `death-note-fins-meios` 4→7 (+3), `historia-vencedores` 4→9 (+5), `kira-voto-brasil` 65→67 (+2), `epicteto-na-sua-mao` 86→88 (+2), `montaigne-desapego` 258→261 (+3), `manipulacao-linguagem-politica` 68→75 (+7); total +22 (≈ 3 views/dia somados). A fonte muda (Analytics via MCP e contador público), então é **indício**, não medida exata.
- **Rajada inicial:** primeiros três dias do relatório ÷ total atual: Kira 57/67 (85%), Epicteto 60/88 (68%), Montaigne 162/261 (62%). Mesmas ressalvas.

### 1.5 Cadência e horário

12 longos entre 20/10 e 07/11: 5 na semana de 20/10, 3 na de 27/10 e 4 de 03 a 07/11 [REG, VIQ]. Horários de Brasília: 19h, 19h, 12h, 18h, 18h, 22h, 12h, 12h, 12h, 12h, 22h44, 18h [POST]. Os de melhor ritmo (Montaigne 18h, Ayanokoji 12h, "A pausa" 12h) não mostram padrão de horário. [CRESC] OF09 registra que não há posição oficial segura sobre horário e mandou "não testar horário".

---

## 2. O que parece ter funcionado

| # | Achado | Confiança | Por quê (e o que falta) |
|---|---|---|---|
| F1 | **Montaigne é o melhor longo**: 261 views, 162 em 3 dias, 3:19 médios, 28,40% assistido (a maior retenção medida; Epicteto 13,32%, Kira 19,52%) | evidência (números); causa = hipótese | Abertura em cena (um homem num cavalo manso, no meio de uma guerra) [EP], tese pessoal ("bonzinho", "agradar") e título em pergunta com o nome do pensador. [TEMAS] já anotou que a pergunta pessoal é "uma pista para testar relações e vulnerabilidade". Faltam impressões, CTR e origem de tráfego. O título ao vivo difere do agendado (ver §3.3). |
| F2 | **Ayanokoji (ser parecido)** e **"A pausa"** vêm em seguida: 146 em 7 dias (20,9/dia) e 96 em 4 dias (24/dia) | indício | Promessa prática ("como se parecer", "decidir antes de reagir") com personagem conhecido ou conceito concreto. Contradiz a leitura de que "anime afasta": o vídeo com nome de personagem (#8) rende ~40x mais por dia que o primeiro Death Note (#1). Não contradiz a leitura de que **o tipo de promessa** importa. |
| F3 | **Promessa pessoal/prática > pergunta moral abstrata**, nos números por dia | indício (n = 12, temas e datas diferentes) | Altos: Montaigne, Ayanokoji, "A pausa". Baixos: "Light/Kira" (0,4 a 3,7), Orwell (7,5), boicote (1,8). Exceções: "Cansada de carregar tudo?" (5,4/dia, promessa pessoal, 17 min) e Epicteto (5,5). Não é regra. |
| F4 | **Shorts curtos de autoajuda estoica** captam distribuição: 3 Shorts = 869 views, 12,6x e 15x o normal do canal | evidência (números); causa = hipótese | Formato curto, gancho emocional. Sem arquivo local, não dá para ver o que eles têm. Atenção: view de Short não equivale a público de longo (histórico separado; [CRESC] OF11). |
| F5 | `idade-media-ser-rico` abriu com 33 views no 1º dia (3,3x) | **hipótese** (1 dia, não separa clique do próprio dono, grupos e Postiz) | Só deixa o formato "como era ser X" elegível para teste. Não supera o ritmo de Montaigne (162 em ~3 dias ≈ 54/dia no relatório de 28–30/10) nem se pode afirmar que iguala (janelas diferentes). |
| F6 | **Operação de publicação**: cadeia de gates, dúvida cega e `vp postiz` sem registro de duplicata, mídia faltando ou ativo `needs_review` em render [DIAG §4]; descrições com divulgação de voz clonada e créditos [DIAG §4] | evidência | Garante direitos e rastro; **não** produz audiência. Strike ou reivindicação: sem registro local (não conferi o Studio; "Verificações de direitos" estão pendentes no `ayanokoji-provocacao-epicteto`, [PUB]). |

---

## 3. O que não funcionou

### 3.1 Causas do vídeo (título, miniatura, tema, abertura, duração)

Todas **hipóteses ou indícios**: sem impressões e CTR, não dá para dizer se o problema foi clique (embalagem) ou exibição.

- **Tema Death Note/Kira/Light (3 vídeos, 83 views):** o piloto foi pensado para "fã de anime curioso por filosofia" [PAUTA death-note-fins-meios]. A pauta registra a medição do nicho como "ensaio sem anime ~10–13 mil por canal, contra ~60–80 com anime" (unidade não explicitada) [PAUTA death-note-fins-meios, "Registro"] e admite que "o canal não tem métricas próprias". No canal, o resultado foi 0 views em 3 dias no primeiro vídeo e 1 no terceiro [TEMAS]. Hipótese: o público do tema existe, mas o canal não chegou até ele (distribuição, §3.2).
- **Duração fora do molde do nicho:** Filosofatos mediana 23 min, Inferno de Dante 25 [CRESC §13; `roteiro-referencias-2026-10-20.md`]; os nossos 6:19 a 17:03 (mediana ~11:40). O próprio [CRESC] registra que o YouTube não dá orientação de duração (OF13) e que "o que precisar" é a posição oficial (EN02). Efeito: não demonstrado.
- **Miniatura:** seguiu o padrão Filosofatos (personagem recortado, fundo de cor, uma palavra) [`miniaturas-filosofatos-2026-10-20.md`], mas aquele canal tem 465 mil inscritos; a amostra "mostra o padrão visual, não prova qual miniatura rende mais". Sem CTR, nada se conclui. O vídeo `boicote-divisao-arendt` foi agendado **sem miniatura nem tags** [POST: `thumbnail` ausente, `tags: []`] e fez 9 views, mas o tema também é político e sem base de comparação.
- **Abertura:** abertura em pergunta retórica ou dado (Death Note "Os seus fins justificam as suas ações hoje?", Kira com dado do Japão, Epicteto com a "mentira confortável") teve retenção menor (Epicteto 13,3%, Kira 19,5%) do que abertura em cena (Montaigne 28,4%) [EP, TEMAS]. n = 3 e 1; hipótese fraca, mas barata de testar (§6, H5).
- **Sem trilha em 5 de 12** (`death-note-fins-meios`, `kira-voto-brasil`, `boicote-divisao-arendt`, `ayanokoji-provocacao-epicteto`, `idade-media-ser-rico`; campo `music` do [EP]); os três longos de melhor ritmo (Montaigne, Ayanokoji, "A pausa") têm trilha. Os finais sem trilha saíram a −16 a −17 LUFS, contra −14 [DIAG §2.4]. É correlação com confundidores fortes (data, tema); trilha afeta retenção, não explica ausência de impressão.
- **Título:** `historia-vencedores` (29 caracteres) e `idade-media-ser-rico` (33) estão abaixo do que o nicho usa (60 a 71) [CRESC §13]; os de 54 a 72 caracteres não rendem sistematicamente mais. H06 do [CRESC] segue sem teste.

### 3.2 Causas do canal

- **Cold start e ausência de público semente (indício forte):** 9 inscritos em 20 dias [VIQ]. O primeiro ensaio fez 0 views nos três dias do relatório e 7 em 19 dias; o terceiro, 1 nos três dias e 9 em 17 [TEMAS, VIQ]. [CRESC] OF05 lembra que vídeos de canal novo e com menos de 100 views têm CTR atípico, e que "nenhuma métrica isolada" decide.
- **Sem recorte** (CLAUDE.md §12 pede "4 vídeos no mesmo recorte em 4–6 semanas"): em 19 dias saíram 12 longos em 5 linhas (anime/Death Note; estoicismo com pensador; Ayanokoji; política/manipulação; "como era ser X") e, pelas pautas, ao menos 6 públicos declarados: fã de anime curioso por filosofia [PAUTA death-note, kira, montaigne]; quem procura filosofia/psicologia prática [PAUTA epicteto]; mulheres de 35 a 60 anos [PAUTA estoicismo-mulheres]; fã de anime de 15 a 30 anos [PAUTA ayanokoji-ser-parecido, provocacao]; fã de filosofia interessado em política [PAUTA manipulacao]; público de história medieval [PAUTA idade-media]. Hipótese: o canal não ensina o algoritmo quem é o espectador dele. A decisão "após 4 vídeos no mesmo recorte" (§12) **não tem base** [DIAG §2.1].
- **Cadência de ~0,6 longo por dia** (12 em 19 dias) com Shorts adicionais: o ritmo de produção supera o de leitura. Não há uma única leitura D7 registrada [MJ, DIAG §2.1] e nenhum teste de molde ficou documentado (o `data/benchmarks/teste-moldes.md` citado nas pautas "a criar" não existe).
- **Dependência dos Shorts (indício):** 53% das views vêm de 9 Shorts sem origem local conhecida; se as 9 inscrições vieram deles, o público é de Shorts, que não assiste longo da mesma forma [CRESC OF11]. Lacuna: inscritos por origem.
- **Atenção dividida:** 72% das postagens agendadas (33 de 46) foram para outras contas [REG]. Não há como medir o efeito no canal, só o custo de atenção do operador.
- **Teste de moldes não lido:** os três braços ("topo" = Epicteto, "Filosofatos" = `historia-vencedores`, "mulheres" = `estoicismo-mulheres-inabalavel`, [PAUTA]) têm 88, 9 e 43 views. Não há o que ler; o braço Filosofatos ainda tem 29 caracteres de título e 12:40 de duração (o rascunho previa ~5:30) [PAUTA historia-vencedores, VIQ].

### 3.3 Causas de operação

| Item | O que os arquivos mostram | Impacto na leitura |
|---|---|---|
| **Títulos ao vivo ≠ títulos agendados** | Ao menos 4 de 12 diferem do `post.json`: Death Note ("Por que torcemos pelo Light? (Death Note)" × "...Os fins justificam os meios em Death Note"), Montaigne ("Porquê Montaigne não era bonzinho?" × "Por que ser bonzinho não te protege, segundo Montaigne"), estoicismo-mulheres ("Cansada de carregar tudo?..." × "Estoicismo para mulheres: 4 práticas..."), "A pausa" (× "O intervalo: o guia estoico..."). Kira e Epicteto podem ser só truncamento do vidIQ. Nada disso está em [PUB] ou [REG]. | O título que gerou os números não está registrado; H01 (nome do personagem × ideia) fica sem base. Lacuna: histórico de alterações do Studio. |
| **Visibilidade** | `ayanokoji-provocacao-epicteto` saiu **não listado** por decisão do dono (5 views) [PUB]. `guia-mastermind-estoico`: o `post.json` da pasta é `unlisted` (14h30Z), mas o `agendado` registrado é o pacote de 15h00Z; visibilidade efetiva a confirmar no Studio [REG, POST, `protecao-strike.md`]. | Os 5 views do #11 e possivelmente os 96 do #10 não são de vídeo público. |
| **Data de saída** | Ayanokoji-ser-parecido: [MJ] diz 02/11 21h00Z, [VIQ] diz 01/11, [PUB] registra post do domingo 01/11 12h mas `agendado` só existe para 02/11. Montaigne e Estoicismo: o vidIQ dá 27/10 e 31/10, o agendamento foi 26/10 21h00Z e 30/10 15h00Z. | A janela de 7/28 dias de cada vídeo está incerta em 1 dia; o `metrics.json` pode estar com `published_at` errado (nunca foi corrigido). |
| **Id do canal trocado** | O Postiz foi atualizado em 31/10 e o canal ganhou novo id; o agendamento do Ayanokoji de 31/10 se perdeu e teve de ser refeito [PUB ayanokoji-ser-parecido]. | Um a dois dias de atraso (de 31/10 para 01/11 ou 02/11) em um dos vídeos que depois rendeu mais. |
| **Itens do Studio** | Legenda, comentário fixado, tela final, categoria "Educação" e rótulo de conteúdo sintético são "À mão no Studio" em todos os [PUB]; nenhum registro marca feito [DIAG §2.9]. Rótulo: "não marcar" em Death Note, Kira e Vencedores; "decidir no Studio" nos demais [DIAG]; `idade-media-ser-rico` usa imagens geradas por IA (FLUX/Gemini) e deixou o rótulo como decisão do dono [PUB, `comentario-fixado.txt`]. As descrições dizem que os créditos estão no comentário fixado: se ele não foi fixado, descrição e comentário se contradizem. | Não se sabe se existem legenda, tela final e comentário. Sem tela final, não há caminho de um vídeo para o próximo. |
| **Loudness e trilha** | 5 de 12 sem trilha; −16 a −17 LUFS nos sem trilha [DIAG §2.4, §2.6]. | Pode pesar na retenção; só se testa com A/B de mixagem. |
| **Métricas** | 12 `metrics.json` com `readings: {}`; hipótese `null` nos mais antigos; `guia-mastermind-estoico`, `boicote-divisao-arendt` e `idade-media-ser-rico` **sem** `metrics.json`; `vp metricas pendentes` quebra [MJ, DIAG §2.1]. | Impossível falar em CTR, retenção ou origem de tráfego com dado local. |
| **Horário** | Variou entre 12h, 18h, 19h e 22h [POST]. | [CRESC] diz para não tratar horário como causa; sem teste. |

---

## 4. Confundidores e limites estatísticos

- **n minúsculo.** 12 longos, 9 inscritos, 3 semanas, nenhum com D28 fechado. Contagens de 5 a 9 views (Light, boicote, provocação) são indistinguíveis entre si (raiz de 9 ≈ 3). A diferença entre ~21/dia e ~5/dia é maior que o ruído de contagem, mas não é maior que a diferença de tema, dia e exposição.
- **Cold start.** O algoritmo precisa de dado para recomendar; vídeos de 1 a 3 dias (#11, #12) não se comparam com os de 2 semanas. A tabela §1.2 usa views/dia só para ordenar; o D7 vence em 11/11 (#10), 12/11 (#11), 14/11 (#12).
- **Fonte dos números mistura.** [TEMAS] é Analytics via MCP (janelas de três datas, fuso do retorno não explícito); [VIQ] é contador público; contagens "têm atualização e escopo diferentes" [TEMAS]. Em Orwell, 68 (contador) e 48 (Analytics) coexistem no mesmo dia.
- **Views do próprio dono, de testes e de conhecidos.** O dono confere cada vídeo no Studio depois da saída [PUB]; vídeos com < 10 views podem ser majoritariamente isso. CLAUDE.md §12: "amigos não contam". Não há como separar nos arquivos.
- **Sobrevivência e breakout.** O arquivo do vidIQ avisa que a busca mostra o que passou do normal [VIQ, cabeçalho]; o breakout do canal é relativo à mediana de 13 vídeos baixos. Os concorrentes são sobreviventes (§5).
- **Views de Short e de link compartilhado** não geram impressão no longo (OF06, [CRESC]); podem inflar CTR e mascarar exibição.
- **Variáveis trocadas ao mesmo tempo.** Entre um vídeo e o seguinte mudaram tema, pensador, título, miniatura, trilha, duração, visibilidade e dia. Qualquer comparação par a par é indicativa, como o próprio [CRESC §5] já avisava.
- **O que NÃO dá para concluir:** que anime afasta público; que estoicismo funciona melhor que anime; que Montaigne "validou" o molde do topo; que o horário importa; que o formato "como era ser X" funciona ou não; que a causa seja a embalagem; que haja penalidade de conteúdo repetitivo (não há aviso registrado, mas o Studio não foi consultado); que a retenção de 13 a 28% seja boa ou ruim (sem curva e sem comparação com vídeos de duração parecida).

---

## 5. Comparação com o padrão dos concorrentes ([VIQ] §1–3)

### O que eles fazem que o canal não faz

| Eixo | Concorrentes | Canal |
|---|---|---|
| **Promessa reconhecível por lugar + ano ou objeto** | "Assim era a vida dentro de [casa/castelo/navio] em [ano]"; hits: castelo medieval 1200 (781 mil), casa vitoriana 1880 (434 mil, 236x), fazenda no Brasil colonial 1800 (468 mil); "Brasil 1964" (749 mil), "Brasil 1975" (350 mil) [VIQ §2]. A demanda "vive nas cabeças longas com lugar + ano" [VIQ §1] | O título do canal é por conceito/pensador (Montaigne, Epicteto) ou por obra (Death Note, Ayanokoji); "Como era ser rico na Idade Média?" não traz lugar nem ano nem objeto (o recorte "Inglaterra, século quatorze" só aparece na fala e na descrição) |
| **Nicho único** | Reconstrução Histórica, Reconstrução do Passado e História Clássica repetem um molde por dezenas de vídeos (~50) | 5 linhas em 19 dias |
| **Duração** | 17 a 31 min nos grandes; outros canais pt de 9 a 55 min; formato "para dormir" de 2 a 3,5 h [VIQ §2] | 6:19 a 17:03; o "como era" tem 8:40 (o modelo em inglês, The Basic Ages, tem 11 min [VIQ §3]) |
| **Cadência** | Reconstrução Histórica "quase diária" no mesmo horário (19h UTC), um molde | ~0,6 longo/dia, 5 linhas, 6 horários |
| **Tema** | Casa, noite, comida, frio, sobrevivência, Brasil colonial, Bíblia/Jesus, pessoa famosa dentro do lugar [VIQ §2] | Filosofia de pensador e obras de anime; nenhum dos temas de maior demanda do arquivo |
| **Tamanho do canal** | Os hits vêm de canais com 15 a 70 mil inscritos | 9 inscritos |

Limite: os hits dos canais pequenos são 1 ou 2 explosões e o resto em centenas ou poucos milhares ("não replica", [VIQ §2, última seção]). A mediana dos ~50 mais vistos de Reconstrução Histórica (60 a 150 mil) é de um canal que já é sobrevivente.

### O que o canal faz que eles não fazem

- Ensaio com fonte primária, pensador, citação na tela, créditos e gates humanos; revisão de roteiro, direitos e dúvida cega antes de agendar [DIAG §4].
- Voz clonada do dono, declarada na descrição, com ilustração em desenho/pintura de domínio público, não "reconstrução por IA" realista. [VIQ §5] já avisa: "o projeto usa desenho: não é a mesma aposta".
- Capítulos e livros com afiliado.
- Shorts técnicos em canais próprios (Java, C), fora do nicho.
- O que pode pesar contra: a mesma política (§12 do CLAUDE.md) que faz o projeto exigir variação é o que os canais de IA em massa arriscam; se funcionar neles, é com escala e imagens realistas que o projeto não faz.

**Aprendizado utilizável:** mais que "como era a vida", o arquivo mostra o padrão **objeto concreto + época** com título longo e **uma promessa que o espectador reconhece sem saber o assunto**. "Como era ser rico na Idade Média?" copia o título em inglês do The Basic Ages (543 mil views, 11 min) sem a especificidade de lugar, ano e objeto, que é o que os brasileiros usam.

---

## 6. Hipóteses ranqueadas para o desempenho baixo

Cada uma com o teste mais barato e a medida do Studio (D7 e D28). Nenhum teste pede anúncio pago, upload automático ou mudança de gate.

| # | Hipótese | Plausibilidade | Teste mais barato | Medida no Studio (D7 / D28) |
|---|---|---|---|---|
| H1 | **Falta de distribuição inicial** (cold start, sem público semente): quase nenhum vídeo foi mostrado a quem clicaria | **a mais provável** | Ler (não mudar nada) impressões e origem de tráfego dos 12 longos e comparar: se a maioria tem < 200 impressões, o problema é exibição, não embalagem. Se Montaigne tiver muito mais, estudar o que ele teve (inclusive link compartilhado). | Impressões, origem (Navegação, Sugeridos, Pesquisa, Externo, Shorts), % tráfego de Shorts, inscritos por origem |
| H2 | **Falta de recorte/identidade** (5 linhas, 6 públicos) impede o sinal de "quem assiste este canal" | muito provável | Cumprir §12: 4 longos seguidos numa única promessa. Antes disso, ler a aba Público (espectadores que voltam, quem assiste vários vídeos) | Espectadores recorrentes, inscritos por vídeo, sobreposição de público no D28 |
| H3 | **Ruído operacional** (título trocado, visibilidade, miniatura ausente, itens do Studio) invalida as comparações | certo (§3.3); o peso nas views é desconhecido | Checklist no Studio por vídeo: título e miniatura atuais, visibilidade, legenda, tela final, comentário fixado, rótulo, categoria, data real. Cerca de 15 min. Registrar | Dados gerais do vídeo e histórico de alterações |
| H4 | **Embalagem não gera clique em público frio** (miniaturas no molde Filosofatos, títulos 54 a 72 caracteres ou 29 a 33) | provável, não separável de H1 sem impressões | Regra do [CRESC] EN09/OF05: CTR por vídeo com ≥ 500 impressões; depois A/B nativo de 1 variável (H07) só no vídeo com mais impressões | CTR, impressões, resultado do A/B (`inconclusivo` vale) |
| H5 | **Abertura em pergunta/dado retém menos que abertura em cena** (28,4% × 13,3% × 19,5%) | possível; n = 3 | Rodar `titulo_video_dito_s` e o tipo de abertura nos 12 episódios (já medido pelo `vp check`) e cruzar com a Intro de 30 s. Teste futuro: dois vídeos do mesmo recorte, só a abertura muda (H02 do [CRESC]) | Retenção 30 s ("Intro"), curva de retenção D7, cena do primeiro vale |
| H6 | **Tema ou promessa não coincide com demanda** (anime-filosofia não é buscado; "estoicismo" é) | possível | Ver "Pesquisa no YouTube" e termos que levam aos vídeos; só gastar crédito de vidIQ se o dono decidir | Termos de busca, % tráfego de pesquisa |
| H7 | **Retenção baixa** (13 a 28%, duração média 1:13 a 3:19) corta a recomendação | possível | Comparar com vídeos de duração parecida no Studio; ouvir os 3 primeiros minutos dos dois piores | AVD, % assistido, retenção 30 s, curva |
| H8 | **Sem trilha, voz seca e −16/−17 LUFS** pesam na retenção dos 5 vídeos sem música | baixa a moderada | Comparar retenção dos 5 sem trilha com os com trilha no mesmo tema (após D7); regra do projeto já exige trilha (§15) | % assistido, AVD |
| H9 | **Duração abaixo do nicho (12 min × 23)** | baixa; sem apoio oficial (OF13) | Não testar agora; é decisão do dono (já registrada como pendente) | AVD × duração |
| H10 | **Penalidade por conteúdo repetitivo** (um por dia, mesma estrutura, imagens paradas) | baixa; sem aviso registrado | Ver mensagens de política e monetização no Studio; registrar o que variou por vídeo no `outline.md` (OF14) | Avisos e status de monetização |

---

## 7. Recomendações

### Parar

1. **Parar de publicar um longo por dia** enquanto não houver leituras D7. A cadência atual produz mais dado do que se lê, e o ciclo (§12) exige leitura. Decisão do dono; o CLAUDE.md §1 ("foco") ainda declara a cadência diária.
2. **Parar de alterar título, miniatura ou visibilidade sem registrar.** Hoje 4 de 12 títulos diferem do agendado e nada documenta quando mudaram.
3. **Parar de tratar vídeos não listados ou agendados como "publicados"** na análise (o `ayanokoji-provocacao-epicteto` e talvez "A pausa").
4. **Parar de declarar "teste de moldes" sem arquivo**: ou cria-se `data/benchmarks/teste-moldes.md` com os três braços, ou o teste deixa de ser citado.
5. **Pausar temas políticos com ruptura** (como o boicote) até haver base de comparação; foi o vídeo mais frágil em operação (sem miniatura e tags) e está fora do recorte que rendeu. É pausa, não veredito: n = 2 (Orwell 75, boicote 9).

### Manter

6. A cadeia de gates, a dúvida cega e a divulgação de voz clonada (§2 do CLAUDE.md). Sem isso, os 12 vídeos teriam risco de direitos e política que os números não mostram.
7. O formato que mais deu retenção: **abertura em cena + um pensador + uma pergunta pessoal + trilha**, com título em pergunta (Montaigne, "A pausa", Ayanokoji "como se parecer"). Tratar como candidato a recorte, não como molde provado.
8. Trilha em todo ensaio longo (§15): os de melhor ritmo a têm.

### Testar (uma variável por vez, medida antes de produzir)

9. **Antes de produzir o próximo vídeo:** ler o D7 dos 12 longos e preencher `metrics.json` (itens abaixo). Zero custo. As janelas D7 de 9 deles já venceram [MJ requests, REG].
10. **Fixar um recorte de 4 vídeos** em 4–6 semanas. Candidato com mais base local: **filosofia prática com pensador**, abertura em cena e promessa de aplicação (3 dos 4 melhores longos). Decisão do dono; o roteirista deve registrar no `outline.md` "o que variou" por vídeo (OF14).
11. **Descobrir a origem dos três Shorts maiores** (sem arquivo local) e, se foram do dono em outro fluxo, trazê-los para o pipeline antes de replicar. Teste barato: apontar, no Studio, o "vídeo relacionado" do Short para o longo mais adequado e medir `Shorts` em origem de tráfego do longo (OF11). Sem anúncio pago.
12. **A/B nativo de uma variável** (título ou miniatura) no longo com mais impressões, só depois de ler H1/H4 e confirmar elegibilidade no Studio (H07 do [CRESC]).
13. **Rótulo de conteúdo sintético**: decidir uma regra uma vez e aplicar aos vídeos seguintes (OF15), principalmente para os de imagens geradas por IA.

### A linha "como era a vida" (`idade-media-ser-rico`)

**Merece um teste, não uma série, e só nestas condições:**

- **Leitura primeiro:** esperar o D7 (14/11) com impressões, CTR, retenção, inscritos e origem. A hipótese já está escrita na pauta ("mais clique e retenção que os ensaios anteriores do canal: 66 a 260 views, 24 a 27% assistido"): aplicar a régua que ela fixou, com uma condição extra de exposição (impressões suficientes para o CTR significar algo). Passa se: views D7 acima do D7 do melhor longo anterior (Montaigne; 261 é o total dele em 12 dias, o D7 sai da leitura), % assistido ≥ 28,4% (o de Montaigne) e CTR acima da mediana dos 12 longos (quando lida). Só retenção boa: ajustar embalagem e repetir. Menos de 66 views no D7 com impressões baixas: inconclusivo por exposição, não por formato.
- **Uma variável por vez:** o segundo vídeo muda **título com lugar + ano + objeto concreto** (padrão dos concorrentes, ex.: "Como era ser camponês na Inglaterra em 1350?" é só ideia de título, **a validar**) e mantém duração e voz. Trilha e rótulo de IA entram padronizados (o piloto saiu sem trilha, sem decisão registrada e com rótulo pendente [PUB, `outline.md`]; fica registrado como confundidor).
- **Risco de política (OF14):** avatar fixo e roteiro "história em modelo" são o padrão que a política descreve. Cada vídeo precisa variar o corpo, e a defesa vale se for registrada.
- **Limite:** o mercado do arquivo premia reconstrução realista e longa (17 a 31 min) feita em massa; o projeto escolheu desenho e voz do dono. Um vídeo não prova o formato (a própria pauta diz isso).
- **Parada:** se o D7 do primeiro e do segundo ficarem abaixo de 66 views com exposição razoável, arquivar a linha e não produzir o resto da escada medieval (`idade-media-vida-em-cada-nivel`).

### O que registrar no `metrics.json` para o ciclo de 7/28 dias

O schema só aceita `hypothesis` como texto e `readings.d7/d28` com dados numéricos ou origem; esforço, título e visibilidade vão nas notas [CRESC §5]. Usar `vp metricas iniciar` para o que falta (guia-mastermind-estoico, boicote-divisao-arendt, idade-media-ser-rico); não usar zeros para gravar nota.

| Campo | O que registrar |
|---|---|
| `published_at` | A data **real** do Studio (vários divergem em 1 dia: Montaigne, Estoicismo, Ayanokoji) |
| `hypothesis` | Hipótese principal com variável e medida, **escrita antes** de ler; nunca retroativa para os 4 primeiros (null fica null) |
| `readings.d7` e `d28`: números | `views`, `impressions`, `ctr_percent`, `avg_view_duration_s`, `retention_30s_percent`, `subscribers_gained`, `traffic_sources` (Navegação, Sugeridos, Pesquisa, Externo, Shorts), % de TV |
| `readings.*.notes` | título e miniatura **vigentes** na leitura e quando mudaram; visibilidade; legenda, tela final, comentário fixado e rótulo de IA (feitos ou não); o que variou vs o vídeo anterior; tem trilha ou não; −LUFS |
| `requests` | A data de D7 recalculada se o `published_at` mudou |
| Fora do arquivo (aba Público) | espectadores recorrentes, idade e gênero (o teste "mulheres 35+" do [PAUTA] depende disso), fatia de TV (OF03/OF16) |

Calendário de leituras ([MJ], [REG], datas do vidIQ): **D7** `ayanokoji-ser-parecido` 08–09/11, `boicote` 10/11, `guia` 11/11, `provocacao` 11–12/11, `idade-media-ser-rico` 14/11. **D28** `death-note-fins-meios` 17/11, `kira` 18/11, `historia-vencedores` 19/11, `epicteto` 20/11, `montaigne` 23/11, `manipulacao` 25/11, `estoicismo-mulheres` 27/11, `ayanokoji-ser-parecido` 29–30/11, `idade-media-ser-rico` 05/12.

---

## 8. Lacunas

Em ordem de peso para a decisão:

1. **Impressões, CTR, origem de tráfego, % de TV e curva de retenção de qualquer vídeo.** Sem elas, H1 (exibição) e H4 (embalagem) não se separam. Nenhum arquivo local as tem. É a mais importante.
2. **Origem, data e conteúdo dos 9 Shorts** (que somam 53% das views).
3. **Títulos e miniaturas efetivamente ao vivo** e quando mudaram (hoje só há o snapshot do vidIQ de 08/11).
4. **Visibilidade efetiva** do `guia-mastermind-estoico` e data real de saída de Montaigne, Estoicismo e Ayanokoji.
5. **Quem assiste:** perfil de idade e gênero, espectadores que voltam, inscritos por vídeo e origem.
6. **Itens do Studio** (legenda, tela final, comentário fixado, rótulo de IA, categoria) feitos ou não.
7. **Views do dono, de conhecidos e de teste** dentro dos totais baixos.
8. **Avisos de política ou direitos** no Studio (conteúdo repetitivo, Verificações de direitos nos vídeos com clipe).
