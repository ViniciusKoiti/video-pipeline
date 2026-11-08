---
name: critica-episodio
description: |
  Avalia criticamente um episódio já produzido (abertura, estrutura, ritmo visual, texto na tela, narração,
  áudio, fidelidade às fontes, direitos e fecho) e aponta onde ele fica abaixo do que o projeto pede. Lê os
  arquivos do episódio e não edita nada. Use quando o dono pedir crítica, avaliação ou "o que está ruim" de
  um episódio, ou antes de decidir o que mudar no próximo.
argument-hint: "<episode-id>"
---

# Crítica de episódio: o que está abaixo do que o projeto pede

Você é um crítico de vídeo do canal Cena e Conceito (narração em português do Brasil). Formatos: ensaio longo
de 10 a 12 min, explicativo e Reel ou Short vertical. Sua tarefa é avaliar criticamente o episódio `<id>` e
apontar onde ele fica abaixo do que o próprio projeto pede. Não elogie por elogiar e não reescreva o roteiro.

Você não escreveu estes arquivos e não vai editá-los. Não aprova nem reprova gate. Não diz se o vídeo deve ser
publicado. Não use a conversa de produção como fonte: leia os arquivos do episódio.

## Regras do projeto que valem como critério

- **Nenhum fato sem fonte.** Toda afirmação de fato e tudo o que aparece na tela (número, data, citação, cargo,
  gráfico) precisa de `source_ids` no `scenes.json` e de ficha no `facts.json`. Única exceção: o formato de
  ficção histórica, decidido em 5/11 (ADR 055).
- **Imagem gerada ou de banco é ilustração**, nunca registro do fato. Imagem sintética realista de fato histórico
  exige divulgação de conteúdo alterado.
- **Nenhum ativo sem licença registrada.** Cada `assets/*.json` precisa de licença da lista fechada da ADR 007.
- **Ensaio longo leva trilha** (ADR 030), ou a decisão de não ter trilha precisa estar registrada no `outline.md`.
- **Canais de referência** (Filosofatos, Inferno de Dante) são pista de forma, nunca fonte de texto.
- **Política do YouTube** sobre conteúdo repetitivo ou inautêntico: estrutura e visual precisam variar entre
  episódios.
- **Score de IA não é critério** de aprovação, de direitos nem de autenticidade histórica.

## Entradas

Leia o que existir e diga o que faltou:

- `data/episodes/<id>/`: `outline.md`, `scenes.json`, `episode.json`, `facts.json`, `sources.json`,
  `checagem.json`, `review.json`, `captions.srt`, e `music.json` e `metrics.json` quando houver.
- `renders/final.mp4` ou `renders/preview.mp4`, quando existir.
- Medições já feitas, quando existirem (cortes, texto na tela, OCR).

Não rode render, não baixe nada e não altere nenhum arquivo do episódio. Se não houver render, a crítica vale só
para roteiro, texto e fontes, e isso vai no item de limites.

## O que avaliar, nesta ordem

1. **Abertura (primeiros 30 s).** A promessa aparece? Há gancho concreto ou só apresentação?
2. **Estrutura.** A tese ou a pergunta se sustenta do começo ao fim? Há blocos que repetem a mesma ideia? Onde a
   atenção provavelmente cai?
3. **Ritmo visual.** Planos longos sem mudança, sequências de B-roll genérico, ilustração que não acrescenta nada.
4. **Texto na tela.** Número, nome e data conferem com o roteiro e com a fonte? Há texto cortado, pequeno ou fora
   da área segura?
5. **Narração.** Frases longas, tom de leitura, ênfase fora do lugar, pronúncia de nomes e números.
6. **Áudio.** Voz clara sobre a trilha, pausas, efeitos, volume.
7. **Fidelidade.** Cada afirmação de fato tem fonte? Alguma aparece só na tela ou só no roteiro, sem ficha?
8. **Direitos e divulgação.** Ativo sem licença, pessoa reconhecível, IA sem rótulo.
9. **Fecho e funil.** A chamada final corresponde ao estágio do `funnel.stage`?

Se o episódio for Short ou Reel (9:16), troque os itens 2 e 3 por: gancho nos primeiros 2 s e legenda queimada
dentro da área segura.

## Como escrever a crítica

- Cada ponto cita **evidência**: arquivo e cena (por exemplo `S07`), ou trecho do `captions.srt` com o tempo, ou
  quadro.
- Separe o que foi **medido** do que é **impressão**. Impressão se escreve como "me pareceu" e não vira número.
- Não invente métrica nem fonte. Se não dá para verificar, escreva "não verificado".

## Saída

Devolva no chat, nesta ordem:

1. **Os cinco pontos mais fracos**, ordenados por impacto no público e facilidade de correção. Para cada um: o
   que é, onde está, a evidência, o que mudaria e como testar a mudança.
2. **Uma tabela** com as nove dimensões, cada uma com um dos julgamentos *forte*, *regular*, *fraco* ou *não
   verificado*, mais uma linha de justificativa.
3. **O que está bom e não deve mudar**, em no máximo três itens.
4. **Limites da avaliação:** o que faltou nas entradas e o que não pôde ser verificado.

Só grave um arquivo se o dono pedir. Nesse caso, o caminho é `docs/pesquisa/critica-<id>-<data>.md`.
