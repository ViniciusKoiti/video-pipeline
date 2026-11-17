---
name: edicao-de-roteiro
description: |
  Edição de roteiro para narrativa e retenção no YouTube, a começar pelos primeiros 30 s: notas por trecho,
  cada uma com o texto proposto, gravadas em edicao.md para o roteirista aplicar. Use na montagem, quando só
  existe o outline.md; na edição, depois do roteiro com vp check limpo e antes da checagem; e na segunda
  passada, quando o roteirista devolver as cenas que mudou.
argument-hint: "<episode-id>"
---

# Edição de roteiro: notas em `edicao.md`

Você é o par do roteirista. O texto é dele: você escreve só `data/episodes/<id>/edicao.md`.

**Nota** é a unidade do seu trabalho, e tem quatro partes: o trecho literal, o que acontece com quem ouve
naquele ponto, a proposta (o texto que entraria no lugar) e o custo (o que a troca arrasta). Uma observação
vira nota quando você consegue escrever a proposta; "está muito técnico" vira nota quando nomeia o termo, o
número ou a frase e traz a troca.

## Dois momentos

- **Montagem:** há `outline.md` e ainda não há `scenes.json`. Siga [`MONTAGEM.md`](MONTAGEM.md), nesta pasta,
  no lugar dos passos abaixo.
- **Edição:** há `scenes.json` com `vp check` limpo. Siga os passos abaixo; se o `edicao.md` já tem a seção
  "Montagem", confira primeiro se o que foi aceito lá está no roteiro.

## Passos

1. **Leitura a frio.** Leia só o campo `narration` do `scenes.json`, em ordem, uma vez, antes de abrir
   qualquer outro arquivo: é assim que o público recebe. Marque cada ponto em que você quis pular, se perdeu
   ou deixou de querer saber o que vem depois. Pronto quando toda cena foi lida e as marcas têm o id da cena.
2. **Primeiros 30 s.** É a parte que mais pesa: passe a abertura pelos quatro testes da seção "Primeiros
   30 s" e escreva a seção de mesmo nome do arquivo. Pronto quando cada teste tem `passa` ou `falha` com o
   trecho, e toda falha tem a abertura proposta por inteiro.
3. **Causa.** Com `outline.md`, `facts.json`, `sources.json` e, se existirem, `pauta.md`, `partitura.md` e
   `radar-brief.json` abertos: para cada marca, ache a causa na tabela de tipos e procure nas fichas
   aprovadas o que serviria melhor ali. Depois percorra todas as atribuições e datas da fala com o teste da
   seção "Atribuições e datas". Pronto quando cada marca tem um tipo ou foi descartada, e cada atribuição e
   cada data da narração passou pelo teste.
4. **Notas.** Escreva as notas no formato da seção "Arquivo", as da abertura primeiro e as demais da que
   mais pesa para a que menos pesa, dentro do teto. Pronto quando cada nota tem as quatro partes e cada
   proposta só usa fatos de `facts.json`.
5. **Fecho do arquivo.** Preencha "O que não mexer", "Referências para a descrição", "Para o dono" e
   "Limites desta leitura". Pronto quando toda fonte citada em alguma `claim` do roteiro aparece nas referências.
6. **Relatório** à sessão principal: o resultado dos quatro testes da abertura, a leitura em uma frase,
   quantas notas por tipo, as três que mais pesam e o que pede ficha.

## Primeiros 30 s

A abertura decide se o resto do roteiro é ouvido, e é a retenção que o dono mede no YouTube Studio
(`retention_30s_percent`, CLAUDE.md §12). Por isso ela tem seção própria no arquivo, em todo episódio, mesmo
quando passa em tudo.

**Recorte.** Os primeiros 30 s de narração, terminem onde terminarem: diga a cena e a frase em que o recorte
acaba, mesmo no meio de uma cena. Meça pela melhor fonte que existir, nesta ordem: `captions.srt` (voz real);
o ritmo de voz medido que o outline declarar; o bloco de números do `outline.md` ("Estimativa a N caracteres
por segundo"; a 14, são 420 caracteres); 420 caracteres. Diga no arquivo qual usou. No Short ou Reel, o recorte é a primeira
cena e os testes valem para ela.

**Os quatro testes**, cada um respondido com `passa` ou `falha` e o trecho literal. Teste que passa por pouco
é `passa` com uma nota explicando o risco:

1. **Assunto.** A primeira frase diz o assunto do `title` do `scenes.json` (e o primeiro plano mostra o da
   capa planejada na `pauta.md`)? Anote em que segundo o assunto é dito.
2. **Promessa.** Dentro do recorte, a pergunta central (`objective.question` ou `objective.promise`) é dita
   em voz alta, de um jeito que quem ouve repetiria?
3. **Concreto.** Dentro do recorte há um caso, um número com comparação ou uma cena com lugar e objeto, vindo
   de uma ficha? Abertura só de conceito falha.
4. **Aberto.** Aos 30 s, algo ficou sem resposta e puxa a cena seguinte? Abertura que já entrega a resposta,
   ou que não abriu pergunta nenhuma, falha. Em vídeo `opinar`, a tese vem cedo e dizê-la não é responder: o
   teste passa quando, depois da tese, fica aberto o melhor argumento contrário ou o caminho até ela.

Além dos testes, cada frase do recorte faz um destes trabalhos: gancho, ponte com quem assiste ou promessa.
Frase que faz outro (saudação, contexto histórico, mapa das partes, atribuição, segunda data) vira nota
`ABERTURA` com a proposta de corte ou de mudança de lugar.

**Abertura proposta.** Se algum teste falha, escreva a abertura inteira como ficaria, cena a cena, com os ids
das fichas usadas, além das notas de linha. O roteirista compara as duas versões lado a lado.

**Quando a forma do formato manda:**

- **Ensaio com obra de ficção:** a abertura segue a seção do mesmo nome em `roteiro-explicativo` (cena,
  confissão do dono ou provocação; a promessa vem depois) e dura mais que 30 s. O teste 1 vira informação,
  com o segundo em que o assunto é dito. Responda os testes 2 a 4 em dois pontos, aos 30 s e no fim da
  abertura do formato, e mostre os dois na tabela: falha em qualquer um é falha. O trabalho de cada frase
  vale até o fim da abertura do formato.
- **Hipótese registrada:** se a `pauta.md` ou o `outline.md` registra uma hipótese que toca a abertura (as
  de `docs/pesquisa/crescimento-youtube-embalagem-hipoteses-2026-10-23.md` ou outra do episódio), a proposta
  mantém a variável em teste e diz qual é.
- **Medida anterior:** se há `metrics.json` de episódio publicado do mesmo formato com
  `retention_30s_percent`, cite o valor e o que aquela abertura fazia de diferente.

## Retenção e público (dados do canal, 2026-11-14)

Você lê como **especialista em retenção e conteúdo**: onde alguém do público pararia de assistir, e onde um minuto passa
sem entregar nada novo.

- **Público** (decisão do dono, 2026-11-14): jovens de 20 a 30 anos com um desânimo profundo. Vira nota `TOM` a fala
  que soa como coach, sermão, bronca ou promessa de cura, ou que diminui o que a pessoa sente comparando com uma
  vida pior.
- **O que a curva mostra** (Idade Média e Montaigne, com cerca de 57 e 86 pessoas): no mesmo relógio as duas são quase
  iguais. Cerca de 40% saem nos primeiros 30 s, cerca de 60% até os 2 min e cerca de 15% ficam até o fim; as pessoas
  ficam uns 3 min em qualquer duração (`docs/pesquisa/retencao-idade-media-2026-11-14.md`).
- **Primeiros 2 minutos.** Além dos 30 s, leia os 2 min iniciais como um bloco (cerca de 1.700 caracteres a 14 por
  segundo, ou o que o `captions.srt` disser). Marque cada ponto em que alguém desanimado largaria o vídeo. As notas
  desse trecho vêm logo depois das da abertura. Confira se o `outline.md` declara a única mudança testável nesse
  trecho; se não declara, peça ao roteirista.
- **Duração-alvo: 8 a 9 min** (teste decidido pelo dono em 2026-11-14). Proponha cortar cena ou trecho que não entrega
  conteúdo novo e escreva no custo quanto tempo a troca economiza.
- **Não cobre como regra o que não se confirmou:** "promessa mais cedo segura mais", "cena de perigo na abertura segura
  mais" e "explicação derruba". Se o roteiro testa um deles como mudança declarada, a nota preserva a variável.

## Tipos de nota

| Tipo | Causa | Proposta típica |
|---|---|---|
| `ABERTURA` | Nos primeiros 30 s, quem ouve ainda não sabe o que vai ganhar. Contexto antes do gancho, apresentação, promessa vaga. | Nova ordem das primeiras cenas ou nova primeira frase. |
| `TENSÃO` | O bloco responde antes de perguntar, ou a pergunta central some por mais de um bloco. | A frase que abre a pergunta antes da resposta, ou a ponte que a retoma. |
| `DENSO` | Mais de um número na frase; termo usado antes de explicado; três nomes próprios numa cena; conceito sem caso; mecanismo antes da dúvida que ele resolve. | A frase com um número só, o termo trocado pelo que ele faz, o caso antes do conceito. |
| `ATRIBUIÇÃO` | Fonte nomeada na fala que reprova no teste. | A frase sem a atribuição. |
| `DATA` | Data que reprova no teste: a segunda da cena, dia e mês onde bastava o ano, ano onde bastava "dois anos depois". | A frase com o intervalo, ou sem a data. |
| `ORDEM` | O fato mais forte no meio, a consequência antes da causa, o caso depois da tese. | Para onde a cena vai e a frase que muda nas duas pontas. |
| `REPETE` | Duas cenas dizem o mesmo, ou um resumo recapitula o que acabou de ser dito. | Qual das duas fica e a frase que cobre o corte. |
| `PONTE` | A passagem entre blocos é "e depois", "outro ponto", ou falta. | A frase de ligação, nascida do bloco anterior. |
| `FECHO` | O fim se anuncia ("para concluir") antes de entregar, ou termina sem responder à pergunta. No vídeo longo, a última cena não une a pergunta dos comentários e a chamada do estágio (emenda de 2026-11-16 da ADR 026). | O fecho que responde com fato e só então chama: a pergunta, depois a chamada (`engagement` e `cta`). |
| `CORTE` | Cena correta que não serve à `objective.promise`, ou trecho que não entrega nada novo (duração-alvo de 8 a 9 min). | Sai a cena; a frase que emenda as vizinhas; no custo, o tempo economizado. |
| `TOM` | A fala soa como coach, sermão, bronca ou promessa de cura, ou diminui o que a pessoa sente comparando com uma vida pior. Público: jovens de 20 a 30 anos com desânimo profundo (decisão do dono, 2026-11-14). Também a opinião anunciada com rótulo ("digo isso como opinião"; emenda de 2026-11-16 da ADR 019). | A frase dita de igual para igual, sem receita; a opinião com marca natural ("na minha leitura", "pelo menos é assim que eu enxergo"). |
| `LACUNA` | A fala diz que o narrador não achou ("eu não encontrei", "não achei", "não sei"), ou empilha ressalvas ("a minha aposta", "é palpite meu") que não mudam a resposta. Decisão do dono, 2026-11-14. | "Eu acho X, porque Y", com Y fichado, ou o corte da frase (skill `roteiro-explicativo`, começo). Na conclusão e no fecho, nunca termina no vazio. |

`CORTE` e `REPETE` valem também para uma frase dentro da cena.

**Peso:** as notas da abertura primeiro; depois, quanto mais cedo no vídeo e quanto maior o trecho afetado,
mais pesa.

**Teto:** 12 notas num vídeo longo, 5 num Short ou Reel. Quando o mesmo tipo atinge mais de um terço das
cenas, escreva uma nota estrutural, que conta como uma: em `ORDEM`, a nova ordem dos blocos; nos outros
tipos, a regra em uma frase, a lista das cenas atingidas e duas cenas reescritas inteiras como modelo.

## Atribuições e datas (decisão do dono, 2026-11-11)

As fontes continuam embasando tudo: `claims`, `source_ids` e o rodapé ficam como estão. A edição é da fala.

**Teste:** leia a frase sem a atribuição ou sem a data. Quem ouve entende pior a história? Se sim, fica.

Passam no teste:

- atribuição a quem é personagem (o pensador, o autor da obra, quem tomou a decisão);
- atribuição de acusação, controvérsia ou decisão de órgão. Esta é obrigatória, com o que as fichas dão de
  quem, o quê e quando, e você a mantém sempre;
- atribuição quando duas fontes discordam e a discordância é o ponto da cena;
- atribuição que o dono pediu para a fala dizer, de fonte interessada ou não;
- data que situa a época, ordena dois eventos, mede um intervalo ou é ela mesma o fato. O normal é uma por
  cena.

Pesquisa entra pelo que mediu ("uns pesquisadores olharam os dados de 232 mil usuários").

**Referências para a descrição.** O que sai da fala vai para a descrição do vídeo: liste cada fonte de
`sources.json` que sustenta alguma claim do roteiro, com autor ou instituição, título, ano e link copiados do
arquivo. Campo ausente vira "falta no sources.json".

## Fronteiras

- **Decisão do dono registrada no episódio** (`pauta.md`, `outline.md`) vale sobre as regras gerais desta
  skill. Onde as duas colidem, siga a decisão e registre o conflito em "Para o dono", com o que a regra
  geral proporia.
- **Fato:** a proposta usa só fichas aprovadas no gate 1 (`selecao-gate1.md`, quando existir; senão,
  `facts.json`) e preserva número, causa, superlativo e quem fez. Ficha da reserva pode entrar, e o custo
  diz "ficha da reserva". Trecho que pede um fato ausente vira nota com custo `pede ficha` e proposta em
  branco.
- **Frase do dono** (toda frase que o outline atribui ao dono, com ou sem a marca [DONO]): o texto fica.
  Você pode propor outro lugar para ela e frases suas ao lado dela; opinião nova é só dele. Se a leitura a
  frio tropeçou no texto dela, isso vai para "Para o dono", com o trecho e o que aconteceu.
- **Ficção histórica (ADR 055):** valem os tipos de narrativa; `ATRIBUIÇÃO`, `DATA` e as referências ficam
  de fora, e as propostas usam formas gerais em vez de número, preço ou nome específico.
- **Retenção é impressão:** escreva "me pareceu". Número de retenção só de `metrics.json` de episódio
  publicado do mesmo formato; `partitura.md` e `radar-brief.json` são forma do nicho.
- **Vizinhos:** vício de frase é do `humanizer-narracao`, duração de cena e de plano é do `vp check`,
  fidelidade ao trecho é do `verificador`. Um desses entra em nota só quando é a causa de uma marca da
  leitura a frio. O bloco do outline entre `<!-- números: gerado por …` e `<!-- números: fim -->` é do
  código.

## Arquivo

```markdown
# Edição do roteiro: <id> — rodada 1, <data>

Leitura em uma frase: o que o vídeo promete e onde ele mais perde quem assiste.

## Primeiros 30 s
Recorte: S01–S03 (~31 s, estimativa a 14 caracteres por segundo).

| Teste | Resultado | Trecho |
|---|---|---|
| Assunto | passa, dito aos 4 s | "…" |
| Promessa | falha | a pergunta só aparece na S05, aos 52 s |
| Concreto | passa | "…" (F03) |
| Aberto | falha | a S03 já responde |

**Abertura proposta:**
- S01: "…" (F03)
- S02: "…"

## Notas

### N01 · S04 · DENSO
- **Trecho:** "…"
- **Quem ouve:** três números em doze palavras; o que importa, o terceiro, chega quando a atenção já foi.
- **Proposta:** "…"
- **Custo:** âncora do plano 2 muda para "…"; claims iguais.
- **Resposta do roteirista:**

## O que não mexer
Até três trechos que seguram a atenção, com a cena e o motivo.

## Referências para a descrição
- source-01 — Autor, *Título*, ano. Link.

## Para o dono
Conflitos com decisões dele no episódio e tropeços em frases dele. Vazio se não houver.

## Limites desta leitura
O que faltou nas entradas e o que é impressão.
```

**Custo** lista tudo o que a proposta arrasta: `anchor` e `keyword` literais da narração que mudam junto,
claim que fica sem frase, `delivery` que deixa de caber, âncora de trilha em `music.json`, cena que some (os
ids das outras ficam) e, quando o episódio já tem voz ou render, as cenas que voltam para a voz.

## Segunda passada

O roteirista responde a cada nota no arquivo e aplica (skill `roteiro-explicativo`, "Edição antes da
checagem"). Quando a sessão principal retomar esta conversa com as cenas tocadas, releia essas cenas e as
vizinhas e acrescente a seção "Rodada 2", no formato da rodada 1:

- o estado de cada nota da rodada 1: `fechada`, `fechada (adaptada)` com o motivo aceito, ou `aberta`;
- as notas novas que a mudança trouxe, com as quatro partes;
- os testes dos primeiros 30 s refeitos, se alguma cena da abertura foi tocada.

Pronto quando toda nota da rodada 1 tem estado. A rodada 2 é a última. Nota nova de texto vai ao roteirista,
que responde e aplica sem outra passada sua; em "Para o dono" entra só o que pede decisão dele.
