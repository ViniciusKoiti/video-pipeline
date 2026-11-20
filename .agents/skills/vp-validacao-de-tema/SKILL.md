---
name: vp-validacao-de-tema
description: >
  Colete ideias no banco de ideias (concorrentes e nichos vizinhos) e valide temas candidatos
  antes da pauta, com parecer por tema do agente `validador-de-tema`. Use para levantar ideias
  ou escolher o tema do próximo ensaio longo do Cena e Conceito; não aprova tema nem escreve a pauta.
---

# Validação de tema: do banco de ideias ao parecer

A pergunta: **este tema serve ao próximo ensaio do canal, para este público e dentro destas regras?** Quem
responde é o agente `validador-de-tema`, em contexto limpo; quem decide é o dono, antes da pauta
([CLAUDE.md](../../../CLAUDE.md) §2.5 e §4). Escopo: ensaios longos do Cena e Conceito. Os Shorts técnicos têm
a rotina `short-diario`, e os Reels partem do radar (ADR 018).

A sessão principal faz os passos 1, 2 e 4; o agente faz o passo 3.

## 1. Banco de ideias (sessão principal, rotina contínua)

O banco só cresce, em `docs/pesquisa/banco-de-ideias.md`. No topo ficam os **canais de referência**
(concorrentes diretos e os de cada nicho vizinho, com link, inscritos, mediana de views e a data); depois, a
tabela:

| ID | Data | Ideia (pergunta) | Origem (URL) | Público | Formato | Situação |
|---|---|---|---|---|---|---|

- **ID:** `I01`, `I02`… em sequência, sem reaproveitar. É por ele que o lote, o parecer e a pauta citam a ideia.
- **Ritmo:** sessões curtas de coleta, com meta de cerca de 20 ideias por hora. Primeiro o volume, depois a
  triagem.
- **Origem:** vídeo de canal de referência, comentário, busca do YouTube, pedido do dono. Cada linha leva o
  link de onde veio, com views e duração na data da coleta. Uma origem conta para a linha quando o título
  original dela promete o mesmo que a pergunta; a que promete outra coisa entra como "perto", com a promessa
  dela.
- **Nichos vizinhos:** canais grandes de nichos com público parecido. Lista atual, **a confirmar**: psicologia,
  autoconhecimento, história, cultura pop comentada (palpite inicial; no primeiro uso o agente propõe a lista,
  passo 3, e o dono fecha). Na aba Vídeos de cada canal, ordene por "Em alta" (o menu abre em "Mais recentes")
  e anote o formato dos vídeos que mais renderam (promessa, abertura, duração), com o link. São formatos já
  validados por um público semelhante, com menos concorrência direta. Canal que a coleta achar e ainda não
  está no topo do banco entra lá como "achado", e o dono decide o papel dele.
- **Ideia é pergunta:** o fato vem das fontes, depois da pauta. Escreva a pergunta com as palavras do canal:
  pergunta que repete o título de origem vira título derivado na pauta. De vídeo de terceiros, anote a forma
  (o que promete e como) com o link; título, frase e imagem ficam com eles.
- **Coleta:** por páginas públicas, como em [coleta-publica.md](coleta-publica.md): busca, os mais vistos de um
  canal com a mediana dele, abertura e as notas de cada coleta. Ferramenta com cota ou crédito (vidIQ, APIs) só
  com pedido do dono na sessão (CLAUDE.md §8). Os temas a evitar do CLAUDE.md §1 já entram com situação
  "descartada: tema a evitar".

Pronto quando cada ideia nova tem ID, origem com link, público e formato, e situação "nova", e todo número do
banco aparece nas notas da coleta.

## 2. Montar o lote (sessão principal)

Escolha de 1 a 5 ideias com situação "nova", as que o dono apontou ou as mais ligadas ao público. Uma rodada do
agente vale para o lote inteiro, não para cada tema.

Chame o agente `validador-de-tema` passando **só**: o texto de cada linha escolhida, com a origem, o caminho do
banco e o das notas da coleta, de onde ele tira views, medianas e durações. Opinião, entusiasmo, fato de
memória ou "esse tema é bom" ficam fora do pedido: viram conclusão sem fonte. Com o vidIQ autorizado pelo dono
nesta sessão, faça a consulta você, salve o resultado em `docs/pesquisa/research_notes/` e passe só o caminho;
o agente não tem acesso a ferramentas com crédito. Para revisar o mesmo lote, ou se a sessão cair antes do
parecer, retome o mesmo agente com a pergunta nova, sem abrir outro.

## 3. O que o agente confere (um parecer por tema)

Suponha que o tema não serve até achar evidência. Cada leitura diz se é **fato** (fonte com URL e data de
consulta), **estimativa** (número de terceiros) ou **inferência** (seu raciocínio sobre os fatos).

1. **Público:** fala com jovens de 20 a 30 anos com desânimo profundo, num tom acolhedor e sem energia de coach
   (CLAUDE.md §1)? O ensaio fala de quem assiste; a obra ou o pensador é um caso.
2. **Demanda:**
   - no canal: `data/episodes/*/metrics.json` (views, retenção e cliques por formato, nas leituras de 7 e 28
     dias), `docs/pesquisa/studio-export-cena-e-conceito-2026-11-14.md`,
     `docs/pesquisa/analise-canal-cena-e-conceito-2026-11-08.md` e
     `docs/pesquisa/retencao-idade-media-2026-11-14.md`;
   - fora: os vídeos mais vistos de concorrentes e de nichos vizinhos sobre o tema, e a busca pública do
     YouTube, pelas notas da coleta que o pedido trouxer. Leia cada vídeo de origem em **vezes a mediana** do
     canal dele e compare a duração dele com a do formato no CLAUDE.md §1. Confira o título original de cada
     origem (oEmbed do YouTube) contra a pergunta: origem que promete outra coisa sai da conta e vai para os
     achados do parecer.

   Views de terceiros mostram interesse associado, não garantem o resultado do canal.
3. **Saturação:** o tema está na lista a evitar do CLAUDE.md §1? Quanto o nicho direto já cobriu, e o que o
   canal acrescentaria?
4. **Evidência:** as perguntas do tema têm resposta em pelo menos 2 fontes reais e independentes (CLAUDE.md §4)?
   Aponte quais existem, com link; o fichamento é do `pesquisador`. Ficção histórica dispensa (ADR 055).
5. **Promessa:** dá para responder às quatro perguntas e propor um título que o vídeo entrega
   ([promessa-e-titulo.md](../../../.claude/skills/pauta/promessa-e-titulo.md))? Escreva uma opção de título como
   prova.
6. **Imagem e direitos:** dá para ilustrar dentro da lista fechada da ADR 007 sem o vídeo virar só imagem
   gerada? Obra citada cabe no teto de citação (10 quadros, 8 s cada)?
7. **Originalidade (YPP):** existe um ângulo próprio, com pesquisa e estrutura do canal (CLAUDE.md §5, política
   de conteúdo não original)?

**Nichos vizinhos propostos.** Enquanto a lista do passo 1 estiver "a confirmar" (decisão do dono, 2026-11-19),
o parecer abre com esta seção, antes dos temas: de 3 a 6 nichos, cada um com um canal grande de exemplo (link e
tamanho), a evidência de público parecido com o do canal e o formato que ele valida. Cada nicho do palpite
inicial aparece confirmado ou descartado, com o motivo. Com a lista fechada, um nicho novo pode ser proposto do
mesmo jeito. O dono decide quais entram.

## Parecer

Um bloco por tema, do mais promissor ao menos:

```markdown
### <tema>

Veredito: segue para pauta | segue com ressalvas | não segue

| Critério | Leitura | Evidência (URL, data) | Tipo |
|---|---|---|---|
| Público | … | … | inferência |
| Demanda | … | … | fato |

Ressalvas: …
Título de prova: …
Só o dono decide: …
```

"Não segue" quando o tema bate na lista a evitar, quando faltam fontes independentes para a promessa central ou
quando ele só se ilustra fora da ADR 007. "Segue com ressalvas" quando o que falta o dono pode aceitar ou a pauta
pode resolver.

Pronto quando os sete critérios de cada tema têm leitura com tipo marcado, e todo número tem fonte ou está
marcado como estimativa.

## 4. Registrar (sessão principal)

- Grave o parecer assim que chegar, em `parecer-lote-N.md` nas notas da coleta, com o link no topo do banco: a
  escolha do dono pode vir em outra sessão.
- No banco, a situação de cada ideia vira "validada: <veredito> (<data>)". Linha em que o parecer achou erro
  (origem que promete outra coisa, número que não bate) é corrigida, com a nota na situação.
- Leve os pareceres ao dono numa pergunta só, com a sua recomendação. Depois da escolha, a ideia escolhida vira
  "virou pauta: `<id do episódio>`", e o bloco do parecer entra no `pauta.md` dele, na seção "Validação do
  tema".
- Os nichos vizinhos que o dono aceitar substituem a lista do passo 1, já sem o "a confirmar", com a data da
  decisão, e os canais deles ganham o papel no topo do banco.

Pronto quando o parecer está gravado, cada ideia do lote tem a situação nova e a pergunta foi feita ao dono.
