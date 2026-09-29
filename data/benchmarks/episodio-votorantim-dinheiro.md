# Métricas: episódio de teste `votorantim-dinheiro` (2026-09-28)

Primeiro vídeo com os planos editoriais da ADR 011 (motion-kit 0.2). Recorte de ~90 s, "de onde veio o dinheiro de
cada novo negócio da Votorantim?", reaproveitando as fontes e fichas do `votorantim-completo`. Registro pedido no
CLAUDE.md §11 (duração de cada etapa, imagens, decisões humanas). Máquina livre em todas as medições (sonda
`cpu_probe` de 0,05 s antes do render).

## Resultado

- Prévia 720p: `data/episodes/votorantim-dinheiro/renders/preview.mp4`, **93,1 s** (voz real), 10 cenas, 21 planos.
- Componentes novos no vídeo: `compare` (escala), `keyword` (2), `chart` `share`, `map` `world` com rota,
  `quote` `document`, `network` em camadas, `timeline` com `when`. Ficou de fora o gráfico de linha (nenhuma ficha da
  seleção tem série de 3 anos ou mais).
- Ritmo: média de 4,4 s por plano, acima da faixa de 2–4 s do formato, por causa das cenas só com gráficos (opção B).

## Custo

- **API paga: US$ 0.** Pexels (licença do banco), Wikimedia Commons e Arquivo Nacional sem custo; nenhuma imagem
  gerada (Workers AI não usado).
- Agentes no plano do Claude do dono (ADR 009), pelos números que cada um informou ao terminar:

| Agente | Rodadas | Tokens informados | Tempo |
|---|---|---|---|
| roteirista | 1 roteiro + 4 correções | ~409 mil (último valor informado) | 32,8 min |
| verificador | 5 checagens (4 completas + 1 curta) | ~944 mil (195 + 200 + 214 + 207 + 128 mil) | 45,6 min |
| pesquisador | correção de 5 fichas | ~264 mil | 12,3 min |
| **total** | | **~1,6 milhão** | **~1 h 31 min** |

- Os tokens são um piso: nas correções o roteirista continuou a mesma conversa, e a releitura dela não entra no
  número informado. A sessão principal (coordenação, contrato, template, busca de imagens) não tem medição aqui.

## Duração por etapa

| Etapa | Duração | Observação |
|---|---|---|
| Fichas | 0 (reaproveitadas) + 12,3 min de correção | 5 fichas corrigidas por pedido da checagem (F07, F38, F44, F45, F55) |
| Roteiro | 32,8 min | v1 em 20 min; 4 rodadas de correção |
| Checagem | 45,6 min | 5 rodadas, contexto limpo em cada uma |
| Busca de imagens | ~1,5 min de chamadas | Pexels 29 s (3 pedidos), Commons 66 s (5 consultas) |
| Voz (Kokoro, `pm_alex`) | 84 s | 10 WAVs |
| Render (Remotion, 720p) | 180 s | 10 cenas; total do script 4 min 28 s |

## Checagem, rodada a rodada

| Rodada | Frases reprovadas | Planos reprovados | Principais achados |
|---|---|---|---|
| 1 | 5 de 20 | 6 de 27 | crédito da CBA dito como pago, sem o corte de 50%; recusa ao BNDE sem atribuição (fonte hagiográfica); data da falência divergente |
| 2 | 3 de 19 | 2 de 25 | corte de 50% ainda sem atribuição; "a empresa nasceu" (a origem é 1891) |
| 3 | 2 de 18 | 3 de 26 | "lucro" em vez de "dividendos"; imagens que o outline já mandava trocar |
| 4 | 3 de 17 | 1 de 26 | "então" ligando a pergunta à recusa; "por ano"; B-roll com texto |
| 5 | 0 de 17 | 0 de 26 | passa para o gate 2 |

## Imagens

- Planos de imagem no roteiro: 10. Com ativo aprovado: **5** (3 Pexels, 2 Commons/Arquivo Nacional). Sem imagem: **5**
  (fábrica, Banco União e Pereira Ignácio: nada no Commons; a Brasiliana Fotográfica recusou o acesso automatizado,
  403). Geradas: 0.
- Candidatos vistos: 68 no Pexels (19 minério, 28 cerrado, 21 forno), 19 no Commons.
- Descartados na conferência em resolução cheia: 2 vídeos de forno (sacos com rótulos ao fundo); 1 foto da CBA de
  2010 (fachada com logo, sob narração de 1941). A foto da CBA de 1955 veio do SIAN em 3406×2584 (no Commons, 893×560)
  para permitir o recorte sem rostos.

## Decisões humanas (review.json)

| Hora | Gate | Decisão |
|---|---|---|
| 12:50 | 1 (fontes e fichas) | aprovado |
| 14:22 | 2 (roteiro) | aprovado |
| 14:56 | 1 | reaprovado depois da correção das fichas |
| 16:05 | 3 (5 ativos) | aprovados |
| 16:05 | 2 | reconfirmado depois do gate 3 |

Rejeições humanas: 0. Horas humanas: não medidas.

## Lições para os próximos episódios

- A checagem foi o maior custo e achou erros reais que iriam para a tela. Mandar ao verificador só as cenas que
  mudaram (rodada 5: 128 mil tokens, contra ~200 mil das completas) e juntar correções pequenas numa rodada só.
- Sem foto de arquivo, as cenas voltam a ser cartões sobre fundo escuro: buscar imagens antes do roteiro, ou escolher
  recortes com acervo disponível.
- Defeitos de template vistos só no vídeo: fonte dentro do painel do número sobre imagem (PR #88); rótulos das setas
  da rede pequenos (fixos no motion-kit); rótulos longos cortados na linha do tempo.
