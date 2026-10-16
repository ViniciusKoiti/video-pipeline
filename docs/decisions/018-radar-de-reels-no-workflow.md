# 018 — O resumo do reels-radar como entrada de forma do roteiro

- **Status:** aceito pelo dono em 2026-10-12 ("alterar o workflow para que ele use o radar"); o objetivo do
  vídeo (noticiar, explicar, opinar) fica para uma ADR seguinte
- **Data:** 2026-10-12
- **Etapa do roadmap:** roteiro (#28) e pesquisa (#26)
- **Relaciona-se com:** ADR 009 (agentes das etapas criativas), ADR 014 (perfil vertical), ADR 017 (que já citava
  o resumo do radar como orientação de forma)

## Contexto

O reels-radar (`~/projetos/radar-de-reels`, projeto à parte) coleta métricas públicas de Reels de um nicho e
grava `briefs/<nicho>.json` (`script_brief.v1`): que características de forma andam com mais ou menos
compartilhamento, com `n` de cada lado e a chance de a diferença ser acaso. Nos dois Reels de 2026-10-12
(`thiel-contrato-pt` e `thiel-empresa-pt`) esse resumo entrou só como um caminho de arquivo no pedido ao
roteirista, depois de o tema e as fontes já estarem escolhidos. O dono achou um dos roteiros sem objetivo e
pediu que o workflow passasse a usar o radar de forma declarada.

O resumo é observação de amostra pequena (34 Reels no nicho de privacidade), lida em boa parte da legenda
escrita e não da fala. Não é experimento e não traz fato nenhum sobre o assunto do vídeo.

## Decisão

O resumo do radar é uma **entrada do episódio**, em quatro pontos, sempre como forma e nunca como fonte (§2.2):

1. **Cópia datada no episódio.** `scripts/provisorio/radar_resumo.py <id> <nicho>` copia o resumo para
   `data/episodes/<id>/radar-brief.json`. O episódio usa a cópia: o resumo de lá pode mudar depois sem mudar o
   que este vídeo seguiu. A pasta do reels-radar vem de `RADAR_DIR` no `.env`. O script não coleta nem chama
   rede; coleta que gasta crédito continua sendo decisão do dono, no outro projeto.
2. **Pauta antes das fontes.** Skill `pauta`: a partir do resumo e do ângulo do dono, escreve `pauta.md` com
   público, temas concretos como perguntas, a forma indicada, o que as fontes precisam responder e o critério
   de parada. O dono aprova antes de qualquer download.
3. **Fichamento e roteiro leem o resumo.** No fichamento, os temas com base viram perguntas às fontes; tema sem
   ficha vai para `open_questions`. No roteiro, o resumo decide abertura, duração, título na tela e legenda, e
   o `outline.md` ganha a seção "Radar" (cada padrão: seguido, ou não e por quê). "Você" continua preso às
   fichas de `impact_today`.
4. **Alertas de forma no `vp check`.** `app/pipeline/radar.py` lê o resumo e compara com o roteiro e a legenda
   do post só os **padrões** (`strength: "pattern"`) que dá para medir no texto: duração, abertura que fala com
   quem assiste, abertura em pergunta, tamanho da abertura, título entre os dois primeiros planos, emoji na
   primeira linha da legenda, pedido de comentário e tamanho da legenda. São alertas, nunca erros. O que
   depende de ver o vídeo (pessoa falando para a câmera, tom de alerta) aparece na linha do resumo como "sem
   conferência no texto". Resumo com mais de 45 dias gera alerta.

## O que fica de fora

- **Temas não geram alerta no código.** Avisar "falta a palavra celular" empurraria o roteiro a dizer algo que
  nenhuma ficha sustenta.
- **Indícios (`hint`) não geram alerta.** São hipóteses; a skill os trata como tais.
- **O argumento do vídeo.** O radar diz que forma anda melhor, não o que o vídeo quer dizer. O objetivo
  (noticiar, explicar, opinar) e uma conferência de propósito são o passo seguinte, a decidir com o dono.
- **Nada do reels-radar vira dependência.** O contrato é lido por um modelo próprio, que ignora campo novo.

## Consequências

- `app/pipeline/radar.py`, `app/pipeline/check.py` (`check_episode` recebe `today`), `app/cli.py`,
  `scripts/provisorio/radar_resumo.py`, `tests/test_radar.py` (dados sintéticos).
- Skills `pauta` (nova), `roteiro-explicativo` e `fichamento`.
- Se o reels-radar mudar o contrato para outra versão, o `vp check` acusa erro no `radar-brief.json` e o
  modelo daqui precisa acompanhar.
- Os Reels citados no resumo (`evidence`, `top.watch`) são de terceiros: servem para o dono assistir e ver a
  forma. Nada deles é copiado, e o resumo fica em `data/episodes/`, fora do Git.
