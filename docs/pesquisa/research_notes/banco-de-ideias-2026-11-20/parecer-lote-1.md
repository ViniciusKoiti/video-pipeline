# Parecer do lote 1 (I02, I03, I04, I05, I16)

Agente `validador-de-tema` (sonnet, sem a conversa), 2026-11-20. Recebeu só as 5 linhas do banco, o caminho do
banco e o desta coleta. O texto do agente está inteiro a partir de "Texto do agente". Mudou só a forma: os
títulos desceram um nível, os caminhos absolutos viraram relativos à raiz do repositório e o link da Wikipedia,
que veio como `.com`, foi corrigido para `.org`. Nada aqui aprova tema: quem decide é o dono.

## Errata da sessão principal (2026-11-20, depois do parecer)

O que a revisão da coleta mudou em relação ao que o agente leu:

1. **Três medianas.** O agente leu a primeira versão do `mais-vistos.txt`, que contava como zero os vídeos só
   para membros (ver o [LEIA.md](LEIA.md)). Com a mediana corrigida:

   | Tema | Vídeo de origem | No parecer | Corrigido |
   |---|---|---|---|
   | I03 | Filosofatos, 556 mil | cerca de 5,2 vezes a mediana de 107 mil | 4,6 vezes a mediana de 121 mil |
   | I16 | Psicologia dos Animes, 489 mil | cerca de 6,9 vezes a de 71 mil | 6,5 vezes a de 75 mil |
   | I16 | Inferno de Dante, 273 mil | cerca de 6,3 vezes a de 43 mil | 6,2 vezes a de 44 mil |

   As outras contas do parecer não mudam (Ludoviajante, A Psique e Minutos de Sanidade não têm vídeo só para
   membros). Na leitura da sessão principal, nenhum veredito dependia dessas três contas, e a I05 continua com o
   maior efeito relativo do lote (10,4 e 20,4 vezes).
2. **Texto das linhas enviadas ao agente.** A I02 dizia "Van Gogh, pelas cartas e quadros" e a I04, "ensaio com
   pensador (Schopenhauer; Kierkegaard na ansiedade)". Eram suposição da sessão principal pelo título, sem ver os
   vídeos, e saíram do banco. O agente já tinha marcado Schopenhauer e Kierkegaard como não verificados.
3. **Origens da I04.** O achado 1 do agente foi aplicado: a linha do banco ficou só com o Ludoviajante, e os
   outros dois vídeos entraram como "perto".
4. **Origem "perto" na I16.** Pela regra que a skill ganhou depois deste lote (a origem conta quando o título
   original promete o mesmo que a pergunta), o vídeo do Inferno de Dante sobre o Killua virou "perto" no banco.
   O parecer ainda o conta como demanda.

## Texto do agente

Pareceres do lote I02, I03, I04, I05 e I16 (consulta em 2026-11-20). Nenhum arquivo foi escrito.

Convenções:
- Tipo: fato = fonte com URL lida; estimativa = número de terceiros; inferência = meu raciocínio.
- "Vezes a mediana" = views do vídeo ÷ `mediana_views` do canal em
  `docs/pesquisa/research_notes/banco-de-ideias-2026-11-20/mais-vistos.txt`. A conta é minha; é estimativa de
  interesse associado, não previsão para o canal.
- Fontes acadêmicas: li só resumos e páginas secundárias. A conferência da citação literal é do `pesquisador`.

### Achados que afetam o lote inteiro

1. **Linha I04 do banco com origem divergente (fato).** `oembed` do YouTube, 2026-11-20:
   - A Psique `9OZVki8ScsA` (1,2 mi) é "Schopenhauer REVELA Por Que Pessoas INTELIGENTES Evitam a Vida Social".
     Fala de evitar vida social, não de pensar demais.
   - Filosofatos `YHksV62PcLQ` (439 mil) é "Por que Pessoas Inteligentes São Mais Tristes (Explicado por Rick e
     Morty)". A promessa é "inteligência → tristeza".
   - Só o Ludoviajante `45u2eqABBRk` (2,7 mi, 35:46, "Pra você que pensa e sente demais | A filosofia da
     ansiedade") casa com a pergunta. A linha merece correção no banco.
2. **O canal não tem leitura própria sobre nenhum destes temas (fato).** Todos os `metrics.json` de longos estão
   com `readings` vazio, exceto `idade-media-ser-rico` (D7). Em
   `docs/pesquisa/studio-export-cena-e-conceito-2026-11-14.md`:
   - Pesquisa do YouTube = 4,0% das views (118).
   - Vídeos sugeridos = 74% das impressões, CTR 1,32%.
   - Montaigne (pergunta pessoal com pensador) = 27% do vídeo assistido. Idade Média = 32,7% e CTR 4,17%.
   - Consequência (inferência): a "demanda de busca" por estes temas pouco ajuda o canal. O que decide é o clique
     ao lado de outros vídeos, a embalagem. A vizinhança dos Sugeridos ainda é lacuna do próprio doc.
3. **Retenção (fato, `docs/pesquisa/retencao-idade-media-2026-11-14.md`).** Cerca de 60% saem até os 2 min, e
   quem fica fica uns 3 min. Os vídeos de origem têm 10 a 36 min. Só I05 tem origem na faixa de 8 a 9 min
   definida pelo dono. Nos outros a duração do modelo é de terceiros, não do canal.
4. **Precedente do dono (fato, `data/episodes/vazio-de-ter-tudo/pauta.md`, 2026-11-14).**
   - Ensaio sem pensador, com a ideia no título.
   - Sensação de quem assiste dita como sensação, sem número.
   - Sem diagnóstico ("depressão" como rótulo do espectador) e sem frase que culpe.
   - Esse episódio já cobre "sentido/vazio", o que pesa em I02 e I16.

### Nichos vizinhos propostos

Lista do banco ainda "a confirmar". O dono decide quais entram.

| Nicho | Canal de exemplo (tamanho) | Evidência de público parecido | Formato que valida | Palpite inicial |
|---|---|---|---|---|
| Psicologia / autoconhecimento filosófico (confirmados, fundidos) | A Psique, 416 mil inscritos, [canal](https://www.youtube.com/channel/UCD9y0Ek291a7GXC8YmJa1pQ). Ludoviajante, 1,75 mi, [canal](https://www.youtube.com/channel/UCFzODWkN1gXm4ryOgLK8Deg) | Títulos dirigidos a quem está mal: "Assista quando estiver deprimido" (3,2 mi), "olá, pessoa exausta" (2,0 mi), "Carta aberta para o vazio" (4,9 mi) (estimativa, `mais-vistos.txt`). O público de 20 a 30 anos é inferência: não há dado de idade. | Ensaio de 8 a 17 min com pensador ou conceito e promessa pessoal; abertura em cena ou "imagine" (`aberturas.txt`, legenda automática). A Psique: 3,1 mi no melhor vídeo contra mediana de 43 mil. | confirmados |
| Cultura pop comentada com leitura psicológica | Psicologia dos Animes, 437 mil, [canal](https://www.youtube.com/channel/UCfGv1j8Lf8C3CU3_YhDQaBA). Minutos de Sanidade, 154 mil, [canal](https://www.youtube.com/channel/UCSgjZJ7tDvZ_0d56-Vsaf0g) | O próprio canal também tem anime. Mas, nos números do Studio de 2026-11-14, os vídeos de anime-só oscilaram: Kira 67 views, Light 15, Ayanokoji 156 (fato). | Vídeos de 6 a 12 min, um personagem ou obra como caso, 6 a 20 vezes a mediana do canal. | confirmado, só como caso (ADR 031), não como assunto |
| História | Você Sabia?, [busca q7](https://www.youtube.com/watch?v=WCoywX18oIE), 1,8 mi na pergunta "como era a vida na Idade Média" | Fato do canal: Idade Média teve o único CTR alto (4,17%). Sobreposição com o público do canal: sem dado; a aba Público do Studio resolveria. | O que se valida é o formato concreto "como era ser X", não o tema para quem está sem ânimo. | confirmado com ressalva: como formato, não como público |
| Psicologia em aula longa (neurociência) | NeuroVox, 3,72 mi, [canal](https://www.youtube.com/channel/UCZGKD_HFC4H1WuPf0ZmWgOg) | Demanda enorme (9,2 mi no topo), mas aulas de 40 a 109 min. | Formato de aula, com risco de tom de coach (o próprio banco anota isso em I20). | descartar como nicho; usar como pista de tema |
| Acolhimento curto, em tom de conversa (novo) | Ludoviajante: 6 vídeos de 6:20 a 10:00 entre 1,3 e 3,2 mi (`mais-vistos.txt`) | Títulos falam com quem está exausto ou desanimado. | Conversa de 6 a 10 min, sem pensador. | proposto; um canal só como evidência, o que limita a confiança |

### Pareceres (do mais ao menos promissor)

#### I03. Por que a gente é gentil com todo mundo, menos com a gente?

Veredito: segue com ressalvas

| Critério | Leitura | Evidência | Tipo |
|---|---|---|---|
| Público | Fala de quem assiste e tem entrada acolhedora. O risco é virar "você é seu pior inimigo", frase que culpa. | CLAUDE.md §1 e pauta do `vazio-de-ter-tudo` | inferência |
| Demanda | Filosofatos 556 mil (cerca de 5,2 vezes a mediana de 107 mil). Ludoviajante 1,5 mi (cerca de 2,6 vezes a de 574 mil). O Filosofatos tinha 487 mil em 2026-10-20 e 556 mil hoje: ainda cresce. | `mais-vistos.txt`; `docs/pesquisa/research_notes/Referencias/formato/tF77QLsI75o.md` | estimativa |
| Saturação | Não está na lista a evitar. O nicho direto já fez duas vezes. O Filosofatos cobre voz gravada, viés de negatividade, amor condicional e autocompaixão (Neff). O ângulo livre é o paradoxo de Salomão (distância de si). | ficha tF77QLsI75o §2 | fato + inferência |
| Evidência | Há 2 fontes independentes, de laboratórios diferentes. (a) Neff 2003, *Self and Identity* 2:85-101: autocompaixão = autogentileza, humanidade comum, atenção plena; escores ligados a menos ansiedade e depressão. (b) Grossmann e Kross 2014, *Psychological Science* 25(8):1571-80, 693 participantes: raciocínio mais sábio sobre o problema alheio do que sobre o próprio, e a assimetria some com autodistanciamento (falar de si por "você" ou pelo nome). | [Neff 2003 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2790748), [Grossmann e Kross (PubMed)](https://pubmed.ncbi.nlm.nih.gov/24916084/) | fato (resumos) |
| Promessa | Resultado: compreensão do porquê da assimetria e de um jeito de olhar (ver o problema "de fora"). Confiança: dois estudos. Tempo: não se aplica. Esforço: não se aplica. O estudo é de laboratório; "mudar a vida" só como hipótese ou opinião. | `promessa-e-titulo.md` | inferência |
| Imagem e direitos | Sem obra. Dá para ilustrar com peças do kit, domínio público (retratos de Sêneca e Marco Aurélio) ou gráfico original. Sem pessoa doente reconhecível nem imagem gerada em excesso. | ADR 007 (CLAUDE.md §5) | inferência |
| Originalidade | Ângulo próprio possível: ancorar em Kross (distância) e não repetir a espinha do Filosofatos. Risco: parecer derivado do vídeo de 24 min, que traz "o que eu diria a um amigo" e autocompaixão. | ficha tF77QLsI75o §6 | inferência |

Ressalvas: não repetir exemplos, frases nem a ordem do Filosofatos (CLAUDE.md §2.2). Dizer o limite da prova em
voz alta (estudo de laboratório). Sem diagnóstico. Sem culpa. A fonte primária de cada estudo fica para o
`pesquisador`.
Título de prova: "Por que a gente trata um amigo melhor do que a si mesmo?" [resultado]. Evita a frase "gentil
com os outros" do título do Filosofatos.
Só o dono decide: tom em primeira pessoa (confissão do dono ou hipótese em "você") e se o ângulo fica no paradoxo
de Salomão.

#### I05. Por que, perto dos 30, a gente ainda não se sente adulto?

Veredito: segue com ressalvas

| Critério | Leitura | Evidência | Tipo |
|---|---|---|---|
| Público | Combina com 20 a 30 anos. Mas "homem-criança" / *puer aeternus* é rótulo que culpa quem já está desanimado. | CLAUDE.md §1 | inferência |
| Demanda | Maior efeito relativo do lote: A Psique 447 mil em 9:30 (cerca de 10 vezes a mediana de 43 mil). Minutos de Sanidade 182 mil em 12:20 (cerca de 20 vezes a de 8,9 mil). Duração próxima dos 8 a 9 min do dono. | `mais-vistos.txt` | estimativa |
| Saturação | Dois canais cobriram, com o enquadramento junguiano. Falta um enquadramento em português baseado em pesquisa de desenvolvimento. | `mais-vistos.txt` | inferência |
| Evidência | O conceito de Jung e a pesquisa de desenvolvimento são tradições independentes. (a) Arnett 2000, *American Psychologist* 55(5):469-480: a maioria nessa fase diz que ainda não chegou à vida adulta; a teoria é debatida. (b) Von Franz, *The Problem of the Puer Aeternus* (Inner City Books), e Kiley 1983 popularizou "síndrome de Peter Pan", que não consta no DSM-5 nem na OMS. Lacuna: o núcleo de Arnett é 18 a 25 anos, com extensão à segunda metade dos 20; "perto dos 30" vai além dele. Não vi dado brasileiro. | [Arnett (PubMed)](https://pubmed.ncbi.nlm.nih.gov/10842426/), [Puer aeternus](https://en.wikipedia.org/wiki/Puer_aeternus), [Cleveland Clinic](https://health.clevelandclinic.org/peter-pan-syndrome) | fato (secundárias) |
| Promessa | Responde às quatro perguntas. Resultado: compreensão (por que a sensação é comum e o que ela costuma significar). Confiança: Arnett, citado sem pôr o nome na fala (regra do canal). Tempo e esforço: não se aplicam. | `promessa-e-titulo.md` | inferência |
| Imagem e direitos | Sem obra. Retratos de Jung talvez não sejam domínio público; usar gráfico original e peças do kit. | ADR 007 | inferência |
| Originalidade | Dá para dizer algo próprio: tratar a sensação como característica descrita da fase, não como defeito. | CLAUDE.md §5 | inferência |

Ressalvas: usar "adultez emergente" como eixo e dizer que o *puer aeternus* é conceito junguiano, não
diagnóstico. Não afirmar que "perto dos 30" é coberto por Arnett sem ficha. A pauta deve dizer na fala que a
teoria é debatida.
Título de prova: "Por que, perto dos 30, a gente ainda não se sente adulto?" [resultado].
Só o dono decide: aceitar o enquadramento de Arnett em vez de Jung (o banco registra Jung) e se admite "puer
aeternus" só como nota.

#### I04. Pensar demais deixa a gente mais triste?

Veredito: segue com ressalvas (a linha do banco precisa de correção)

| Critério | Leitura | Evidência | Tipo |
|---|---|---|---|
| Público | Direto. Risco: sugerir que quem sofre "pensa errado". | CLAUDE.md §1 | inferência |
| Demanda | Só o Ludoviajante 2,7 mi (cerca de 4,7 vezes a mediana de 574 mil) responde à pergunta, em 35:46. Os outros dois links têm promessas diferentes (ver achado 1). O A Psique (cerca de 28 vezes a mediana) não vale como prova desta pergunta. | `oembed` e `mais-vistos.txt` | fato + estimativa |
| Saturação | Três canais tocam o tema; o Filosofatos pelo ângulo "inteligente = triste", que não precisamos repetir. | `oembed` | fato |
| Evidência | Há 2 fontes independentes para a promessa central, que é "o problema é ruminar, não pensar". (a) Nolen-Hoeksema, Wisco e Lyubomirsky 2008, *Perspectives on Psychological Science* 3(5):400-424: ruminação agrava depressão; distingue autorreflexão mais adaptativa. (b) Whitmer e Gotlib 2011 (Stanford), que relata que a distinção entre "brooding" e "reflection" fica turva em quem está deprimido. Treynor et al. 2003 é do mesmo grupo de (a), então não conta como independente. Schopenhauer e Kierkegaard como causa de "pensar demais" não verifiquei, e não são necessários. | [Rethinking Rumination (PubMed)](https://pubmed.ncbi.nlm.nih.gov/26158958/), [Treynor 2003 e Whitmer/Gotlib](https://link.springer.com/content/pdf/10.1023/a:1023910315561.pdf) | fato (resumos) |
| Promessa | Resultado: a diferença entre ruminar e refletir. Confiança: duas pesquisas. Estudos são correlacionais; sem "pensar menos cura". | `promessa-e-titulo.md` | inferência |
| Imagem e direitos | Sem obra, ou um pensador em domínio público como caso. Sem pessoa doente reconhecível. | ADR 007 | inferência |
| Originalidade | Dá para fazer em 8 a 9 min com um ângulo próprio: o que distingue "ruminar" de "elaborar". | CLAUDE.md §5 | inferência |

Ressalvas: corrigir a origem no banco antes da pauta. Não dizer "deprimido" como rótulo de quem assiste. Dizer
que ruminação é associada à depressão, não que "pensar demais" a causa.
Título de prova: "Pensar demais deixa a gente triste? A diferença entre ruminar e refletir" [confiança].
Só o dono decide: com ou sem pensador (precedente do `vazio-de-ter-tudo`: sem).

#### I16. Dá para estar deprimido e parecer bem?

Veredito: segue com ressalvas (as mais fortes do lote)

| Critério | Leitura | Evidência | Tipo |
|---|---|---|---|
| Público | Fala a quem se esconde de si. É o tema de maior risco: o título já traz o rótulo "deprimido". | CLAUDE.md §1; pauta do `vazio-de-ter-tudo` | inferência |
| Demanda | Psicologia dos Animes 489 mil (cerca de 6,9 vezes a mediana de 71 mil) em 10:23; Inferno de Dante 273 mil (cerca de 6,3 vezes a de 43 mil) em 55:38, caso Killua. | `mais-vistos.txt` | estimativa |
| Saturação | Dois canais de anime cobriram, cada um com um personagem. No canal, os vídeos de anime-só tiveram resultado oscilante (ver nichos). | `mais-vistos.txt`; `studio-export-cena-e-conceito-2026-11-14.md` | fato |
| Evidência | "Depressão sorridente" **não é diagnóstico formal**: [WebMD](https://www.webmd.com/depression/smiling-depression-overview) e [Psych Central](https://psychcentral.com/blog/the-sad-truth-about-your-smile/) dizem isso. O quadro próximo reconhecido é o transtorno depressivo persistente: [Harvard Health](https://www.health.harvard.edu/a-to-z/dysthymia-a-to-z) e [Mayo Clinic](https://www.mayoclinic.org/health/dysthymia/DS01111). Mas as fontes sobre "sorridente" são de consumo, com discordância entre elas. Não achei página da Fiocruz nem do Ministério da Saúde sobre o termo. CVV (188, 24 h, gratuito): [relatório CVV](https://cvv.org.br/wp-content/uploads/2025/03/CVV-_-Relatorio-_-4Tri_2024.pdf). Fatos oficiais do Itadori vêm do guia oficial, não confirmei a leitura "sorridente". | links acima | fato (secundárias) |
| Promessa | Dá para responder: "sim, o sofrimento pode não aparecer, e o que ajuda é perguntar/procurar ajuda". Resultado como compreensão. O vídeo não pode diagnosticar o espectador. | `promessa-e-titulo.md` | inferência |
| Imagem e direitos | Jujutsu Kaisen é obra grande. Só quadros oficiais (`provider: official`), até 10 por vídeo e 8 s cada; clipe em movimento só em B-roll, sem áudio da obra, só no YouTube, com decisão de risco do dono. Fora da obra: banco de imagem sem pessoa reconhecível doente, então o resto cai em peças do kit. Viável, mas apertado. | CLAUDE.md §5; ADR 007 | inferência |
| Originalidade | O ângulo do canal (voz, pesquisa, estrutura) pode diferir, mas o caso Itadori é o mesmo do concorrente. | `mais-vistos.txt` | inferência |

Ressalvas: aviso do CVV logo no começo e depois de qualquer trecho pesado; sem rótulo diagnóstico para quem
assiste; o termo "depressão sorridente" dito como expressão popular, não como diagnóstico; o Itadori como leitura
própria do canal, com ficha oficial para o fato da obra; checar as regras do YouTube sobre conteúdo de saúde
mental antes do gate 4 (não consultei).
Título de prova: "Dá para estar mal e parecer bem? O que o Itadori mostra" [resultado].
Só o dono decide: assumir o risco de IP e de saúde mental; se entra com anime ou sem (ADR 031 diz anime só como
caso).

#### I02. O que fazer quando a vida para de fazer sentido?

Veredito: não segue (como está)

| Critério | Leitura | Evidência | Tipo |
|---|---|---|---|
| Público | Direto. Mas a pergunta já é o assunto do `vazio-de-ter-tudo` (gates 1 e 2 aprovados em 15/11), e o dono decidiu "ideia no título, sem pensador". | `data/episodes/vazio-de-ter-tudo/pauta.md` | fato |
| Demanda | Ludoviajante 2,5 mi em 16:18 (cerca de 4,4 vezes a mediana de 574 mil). Ângulo e artista (Van Gogh) são do concorrente; o banco registra o mesmo caso. | `mais-vistos.txt` | estimativa |
| Saturação | Há "sentido da vida" por todo lado: a busca q10 traz Nietzsche, Clóvis de Barros, Ludoviajante, A Psique (Tolstói). Dentro do canal já há o vazio. | `busca.txt` | fato |
| Evidência | A promessa "o que fazer" não tem duas fontes independentes mostradas. As cartas do Van Gogh são uma fonte primária real ([Van Gogh Museum, carta 249](https://vangoghmuseum.nl/en/highlights/letters/249); a busca aponta "uma nulidade" como autodescrição, mas não confirmei o texto nem a data). Uma fonte independente sobre "sentido" não foi achada nem verificada. Há risco de direitos: [vangoghletters.org](https://vangoghletters.org/vg/credits.html) tem "All Rights Reserved" de 2009 e uma menção a CC BY-NC-SA 4.0 (trecho cortado; a página de copyright não carregou). NC e SA são proibidos pela ADR 007. As cartas originais em holandês e francês são domínio público (autor morto em 1890), mas a tradução da edição não necessariamente. | links acima | fato (parcial) |
| Promessa | Não responde às quatro perguntas sem romantizar o sofrimento do artista (ele morreu por suicídio) e sem uma resposta dita como opinião do dono. | `promessa-e-titulo.md` | inferência |
| Imagem e direitos | Quadros de Van Gogh são domínio público; as imagens se resolvem. Os textos das cartas dependem da tradução. | ADR 007 | inferência |
| Originalidade | Cópia do ângulo do Ludoviajante e repetição do vazio do canal. | `mais-vistos.txt` | inferência |

Ressalvas: o que serviria seria outra pergunta, "como Van Gogh lidava com dias sem sentido, nas próprias
palavras?", com tradução própria das cartas em domínio público e uma segunda fonte biográfica independente. Aí o
veredito sobe para "segue com ressalvas".
Título de prova (só se a pergunta mudar): "O que Van Gogh escrevia ao irmão nos dias sem sentido?" [confiança].
Só o dono decide: tema fora do `vazio-de-ter-tudo` e a tolerância a tratar um artista que morreu por suicídio.

### Para o registro no banco

I03, I05, I04 e I16: "validada: segue com ressalvas (2026-11-20)". I02: "validada: não segue (2026-11-20)". Na
linha I04, trocar as origens pelas de fato (só o Ludoviajante responde à pergunta). Recomendação de ordem: I03,
I05, I04, I16, I02.

### Aviso sobre uma fonte

Um dos resultados de busca (página do Wikiwand sobre o Itadori) trazia texto endereçado a um assistente de IA. A
própria ferramenta o sinalizou e eu não o segui nem o usei.

### Arquivos relevantes

- `docs/pesquisa/banco-de-ideias.md`
- `docs/pesquisa/research_notes/banco-de-ideias-2026-11-20/mais-vistos.txt`
- `docs/pesquisa/research_notes/banco-de-ideias-2026-11-20/busca.txt`
- `docs/pesquisa/studio-export-cena-e-conceito-2026-11-14.md`
- `docs/pesquisa/retencao-idade-media-2026-11-14.md`
- `data/episodes/vazio-de-ter-tudo/pauta.md`

### Fontes

[Neff 2003](https://pmc.ncbi.nlm.nih.gov/articles/PMC2790748),
[Grossmann e Kross 2014](https://pubmed.ncbi.nlm.nih.gov/24916084/),
[Nolen-Hoeksema 2008](https://pubmed.ncbi.nlm.nih.gov/26158958/),
[Treynor 2003](https://link.springer.com/content/pdf/10.1023/a:1023910315561.pdf),
[Arnett 2000](https://pubmed.ncbi.nlm.nih.gov/10842426/),
[Cleveland Clinic](https://health.clevelandclinic.org/peter-pan-syndrome),
[Harvard Health](https://www.health.harvard.edu/a-to-z/dysthymia-a-to-z),
[Mayo Clinic](https://www.mayoclinic.org/health/dysthymia/DS01111),
[WebMD](https://www.webmd.com/depression/smiling-depression-overview),
[Psych Central](https://psychcentral.com/blog/the-sad-truth-about-your-smile/),
[CVV](https://cvv.org.br/wp-content/uploads/2025/03/CVV-_-Relatorio-_-4Tri_2024.pdf),
[vangoghletters.org](https://vangoghletters.org/vg/credits.html),
[Van Gogh Museum](https://vangoghmuseum.nl/en/highlights/letters/249).
