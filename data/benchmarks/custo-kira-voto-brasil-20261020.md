# Custo do vídeo `kira-voto-brasil` (2026-10-20)

Segundo vídeo longo do formato "ensaio de conceito" (6 min 19 s, pt-BR), feito de ponta a ponta pelo prompt piloto e
agendado para 21/10 às 19h. A medição segue o método do `custo-death-note-fins-meios-20261019.md`:
- **Tokens:** cada chamada do registro da sessão do Claude Code, sem repetição (`message.id`), com entrada, cache escrito
  (5 min ou 1 h), cache lido e saída separados.
- **Preços** do Opus 5.5 por milhão de tokens: entrada US$ 4, cache escrito US$ 5 (5 min) ou US$ 8 (1 h), cache lido
  US$ 0,20, saída US$ 20.
- **Modelo:** todas as chamadas foram ao `claude-opus-5-5`.

O que é estimativa está marcado.

## Resumo

- **Dinheiro gasto: US$ 0.** Nenhuma API paga (`MAX_API_SPEND_USD=0`). A voz no Modal ficou no crédito gratuito e o
  render foi local.
- **Equivalente em API do episódio: ~US$ 42.** O piloto `death-note-fins-meios` custou ~US$ 220, e a projeção para os
  próximos vídeos era de US$ 70 a 95. Este ficou abaixo da projeção por quatro motivos:
  - 2 rodadas do verificador no roteiro, contra 36 no piloto;
  - fontes e imagens reaproveitadas do piloto;
  - um vídeo com metade da duração;
  - nenhum código mudado no meio do episódio.
- **Maior item evitável: a miniatura refeita, US$ 5,86 (14% do total).** A primeira copiou o piloto e foi reprovada.
  A skill `miniatura` existe para isso não se repetir.
- **Na assinatura:** com 4 vídeos por mês, a conta do piloto não muda: ~US$ 25 por vídeo no Max 5x e ~US$ 50 no Max
  20x. Este vídeo usou cerca de um quinto do que o piloto usou.

## 1. Equivalente em API por etapa

| Etapa | Sessão principal | Agentes | **Total** |
|---|---|---|---|
| Pré-produção: tema, candidatos de fonte, prompt (19/10, 23h13–23h37) | 2,44 | 3,24 (busca de candidatos) | **5,68** |
| Fontes e fichas | 2,93 | 3,24 (pesquisador, com a correção da F14) | **6,17** |
| Roteiro e checagem | 1,59 | 9,05 (roteirista 5,28; verificador 1,65 e 2,12) | **10,64** |
| Imagens e voz | 4,48 | 1,64 (verificador das imagens) | **6,12** |
| Render, textos e prévia para o gate 4 | 3,56 | — | **3,56** |
| Miniatura refeita (análise do Filosofatos, recorte, 3 rodadas de versões, urna) | 5,86 | — | **5,86** |
| Gates e agendamento no Postiz | 1,49 | 0,68 (dúvida cega) | **2,17** |
| Dois resumos de contexto automáticos (estimativa: ~460 mil tokens de entrada) | ~2 | — | **~2** |
| **Episódio** | **~24,35** | **17,85** | **~US$ 42** |

Valores em US$. A sessão principal teve 335 chamadas (59,6 M de cache lido, 0,82 M de cache escrito e 0,24 M de
saída) mais as 28 da pré-produção. Os resumos de contexto não aparecem no registro de uso, por isso estão estimados.

**Fora do episódio, trabalho de método** (~US$ 3,50):
- a skill `miniatura`: US$ 0,93;
- commits e o PR #175: US$ 1,49;
- este relatório: ~US$ 1.

### Comparação com o piloto

| Item | `death-note-fins-meios` | `kira-voto-brasil` |
|---|---|---|
| Verificador | US$ 101,49 (36 rodadas) | US$ 5,41 (2 no roteiro, 1 nas imagens) |
| Roteirista | US$ 45,52 | US$ 5,28 |
| Pesquisador e fontes | US$ 10,39 | US$ 6,48 (com a busca de candidatos) |
| Sessão principal do episódio | ~US$ 65 | ~US$ 24 |
| **Total do episódio** | **~US$ 220** | **~US$ 42** |
| Duração do vídeo | 13 min | 6 min 19 s |
| Custo por minuto de vídeo | ~US$ 17 | ~US$ 6,60 |

## 2. Voz, render e o resto

| Item | Medida | Custo |
|---|---|---|
| Voz final no Modal (GPU T4) | 39 cenas em 6 min 40 s de relógio, para 378,9 s de fala. GPU estimada em 400 a 500 s pela razão do piloto | ~US$ 0,07 a 0,08 de GPU, mais CPU e memória: **~US$ 0,15 (estimativa), dentro do crédito de US$ 30/mês** |
| Render local (Remotion) | 46 min 26 s, 7,3× o tempo real, pico de 2,9 GB | Luz: ~0,12 kWh a 150 W, **~R$ 0,12 (estimativa)** |
| Recorte da miniatura (rembg, local) | 3 recortes de ~13 s | desprezível |
| Imagens | 20 ativos reaproveitados do piloto, o retrato de Locke (Commons, PD) e a foto da urna (Agência Senado, CC BY 2.0) | US$ 0 |
| Fontes | 20 fontes públicas (7 copiadas do piloto) | US$ 0 |
| Busca na web | 2 buscas, na assinatura (a US$ 10 por mil buscas, seriam US$ 0,02) | US$ 0 |
| Postiz | instância do dono | não medido |

## 3. Suas horas (não medidas)

Pelo registro da conversa, o seu tempo ficou espalhado em decisões curtas:
- 13 paradas: gates, plano de imagens, render, miniatura e agendamento;
- assistir ao vídeo (6 min);
- a conversa da miniatura, das 12h15 às 14h20.

Estimo de 1 a 2 horas, mas é uma estimativa. Medir de verdade pede anotar o início e o fim de cada vez que você
para para o vídeo.

## 4. Quanto precisa render

| Custo por vídeo | RPM US$ 0,50 | RPM US$ 1,00 | RPM US$ 2,00 |
|---|---|---|---|
| US$ 25 (Max 5x, 4 vídeos/mês) | 50 mil views | 25 mil | 12,5 mil |
| US$ 42 (este vídeo pela API) | 84 mil | 42 mil | 21 mil |

**Programa de Parcerias:** um vídeo de 6 min 19 s junta horas de exibição mais devagar que um de 13 min. As 4.000 horas
pedem:

| Retenção média | Minutos por view | Views para 4.000 h |
|---|---|---|
| 20% | 1,26 | ~190 mil |
| 30% | 1,90 | ~127 mil |
| 40% | 2,53 | ~95 mil |

O vídeo mais curto custou um quinto, mas precisa de cerca do dobro de views para juntar as mesmas horas. Isso pesa na
decisão de duração do formato, que é sua.

## 5. Como baixar mais

1. **Miniatura pelo canal de referência desde o início** (skill `miniatura`): ~US$ 5 a menos por vídeo.
2. **#169 no main:** gravar o `asset_id` deixa de derrubar o gate 2, e some uma rodada do verificador e uma reaprovação.
3. **Gerador de legenda pronto:** some a revisão à mão, pouco custo, mas tempo seu.
4. **Sonnet 5.5 no roteirista e no verificador:** pela metade do preço, o episódio cairia para ~US$ 33. Isso pede um
   teste de qualidade antes.

## 6. O que medir a seguir

- **Fatura do Modal em outubro:** confirma a voz dentro do crédito e substitui a estimativa de GPU.
- **Suas horas,** anotadas no próximo vídeo.
- **Métricas aos 7 e 28 dias** (28/10 e 18/11): views, retenção e inscritos, para pôr números reais na seção 4.
