# 019 — Objetivo do vídeo: noticiar, explicar, opinar

- **Status:** aceito pelo dono em 2026-10-12 (os três tipos, e um vídeo pode ter mais de um); o rastreio dos
  tipos pelo reels-radar segue como proposta, descrita no fim
- **Data:** 2026-10-12
- **Etapa do roadmap:** roteiro (#28)
- **Relaciona-se com:** ADR 009 (agentes das etapas criativas), ADR 018 (resumo do reels-radar)

## Contexto

O dono achou o roteiro do `thiel-empresa-pt` "sem objetivo". A revisão mostrou por quê: a pergunta central era
um inventário de assuntos, as fontes não sustentavam falar com quem assiste, e cada rodada de checagem cortou
o que não tinha fonte forte, até sobrarem frases verdadeiras sem ligação. O verificador confere se cada frase
é verdadeira; nenhuma etapa perguntava o que o vídeo se propunha a fazer.

O dono definiu os tipos: um vídeo **noticia**, **explica** ou **opina** sobre algo. E disse que depende do
vídeo: pode haver vídeos de vários tipos, inclusive com mais de um tipo no mesmo roteiro.

## Decisão

O `scenes.json` ganha o campo opcional `objective`:

- `kinds`: de um a três tipos, sem repetir, **na ordem em que aparecem no vídeo**. O primeiro é o principal e
  manda na estrutura.
- `promise`: uma frase com o que a pessoa sabe, entende ou pensa depois de assistir.
- Cada tipo exige o seu campo, que só existe com ele: `noticiar` → `event_date`; `explicar` → `question`
  (termina em "?"); `opinar` → `thesis` e `thesis_by`.

Regras:

1. **O objetivo vem do dono**, pela pauta (skill `pauta`) ou direto. O agente não escolhe o tipo nem escreve a
   tese.
2. **Opinião é opinião.** A tese é dita como opinião, na primeira pessoa ou atribuída, e nunca vira número,
   data ou citação na tela. Os fatos em volta dela continuam presos às fichas (§2.2). Isso registra a regra
   que o dono já tinha dado: a tese dele pode ir sem prova, desde que marcada.
3. **Notícia tem prazo.** Com `noticiar`, o `vp check` avisa quando o fato tem mais de 30 dias: aí o vídeo
   explica ou opina.
4. **Sem objetivo, alerta.** Roteiros antigos continuam válidos; o `vp check` avisa que falta o objetivo e,
   quando ele existe, mostra os tipos e a promessa.
5. **Fichas que não sustentam a promessa param o roteiro.** A decisão de trocar a promessa volta ao dono.

O `vp check` confere só a estrutura do campo e a idade da notícia. Se o roteiro cumpre a promessa é julgamento,
e fica com o dono no gate 2 (e, se for criado, com um agente leitor que diga em uma frase qual é o ponto do
vídeo; candidato, ainda não decidido).

## Consequências

- `app/pipeline/schemas.py` (`Objective`, `ScenesManifest.objective`), `app/pipeline/check.py`
  (`objective_warnings`, `objective_summary`), `tests/test_objective.py`.
- Skills `roteiro-explicativo` (estrutura por tipo) e `pauta` (o objetivo passa a ser um item da pauta, e o
  critério de parada se refere à promessa).
- O `episode.json` não muda: o objetivo é do roteiro, não do render.
- Os dois Reels de 2026-10-12 não têm objetivo declarado e passam a receber o alerta.

## Proposta em aberto: rastrear os tipos no reels-radar

O dono sugeriu medir, no reels-radar, que tipo de vídeo anda mais em cada nicho. O desenho possível, a decidir
lá (o contrato `reels.v1` só muda com validação do dono):

- Um campo novo na leitura de cada Reel (`purpose`: notícia, explicação, opinião, ou nenhum), preenchido pelo
  extrator de regras a partir da legenda, que continua só em memória.
- O `radar mine` compararia o compartilhamento por tipo, com o mesmo teste dos outros padrões, e o resumo
  ganharia itens como `purpose_explain`.
- Aqui, o `vp check` passaria a comparar o tipo principal do roteiro com esses padrões, como já faz com a forma.

Limites conhecidos: com 34 Reels num nicho, cada tipo dificilmente chega a 5 de cada lado; a legenda escrita
nem sempre diz o que o vídeo faz; e regras de palavras erram ironia e mistura de tipos.
