Ok # Cena e Conceito: plano dos próximos passos (2026-11-14)

Junta o que saiu da sessão de 14/11: o diagnóstico do Studio (`studio-export-cena-e-conceito-2026-11-14.md`), a revisão
das ADRs (`revisao-adrs-2026-11-14.md`) e o público declarado pelo dono (jovens de 20 a 30 anos com desânimo profundo).

**Diagnóstico em uma frase:** os vídeos foram exibidos, mas pouca gente clica (CTR em torno de 1,6%). A única exceção,
"Como era ser rico na Idade Média?", teve 4,2% de CTR e 32,7% assistido. Os Shorts trazem volume, mas não levam ao longo.

Marcação: **[dono]** = decisão ou ação só do dono; **[eu]** = posso fazer na sessão; **[juntos]** = o dono traz o dado,
eu analiso.

## Fase 0: urgente (hoje e amanhã)

| # | Passo | Quem | Por quê |
|---|---|---|---|
| 0.1 | **Pausar a rotina diária de Shorts** (o timer roda amanhã às 06:00) ou liberar o download de fontes | [dono] | Está parada há 7 dias no mesmo passo e gasta cota sem produzir nada (ADR 036). |
| 0.2 | **Manter não listados os vídeos com a voz do Azure** até ler os termos de uso comercial da Microsoft | [dono]; a leitura e o resumo podem ser [eu], se pedido | Condição da ADR 058. |
| 0.3 | Estreitar a permissão `vp postiz *` no `settings.local.json` | [dono] | Libera um comando que a ADR 036 proíbe à rotina. |

## Fase 1: medir (semana de 16 a 22/11, sem custo)

| # | Passo | Quem | Para quê |
|---|---|---|---|
| 1.1 | ~~Curva de retenção do Montaigne e da Idade Média~~ **feito em 14/11** (`retencao-idade-media-2026-11-14.md`) | [juntos] | As duas curvas são quase iguais no mesmo relógio: ~60% saem até os 2 min. A diferença no % assistido vem da duração. |
| 1.2 | Exportar **Vídeos sugeridos** e **Pesquisa do YouTube** (Origem do tráfego) | [juntos] | Ver ao lado de quem a miniatura disputa o clique; é a entrada para escolher temas. |
| 1.3 | Conferir a coluna **Restrições** da A pausa e da Provocação | [dono] | Saber se os 33 clipes de anime geraram reivindicação (a emenda de 03/11 da ADR 007 condiciona o próximo vídeo com clipe a isso). |
| 1.4 | Conferir o **Vídeo relacionado** do Short da comida | [dono] | Saber se o teste "Short leva ao longo" chegou a acontecer. |
| 1.5 | **Leituras D28** (o `vp metricas pendentes` lista): Light 17/11, Kira 18/11, "E se o Light…" 19/11, Epicteto 20/11, Montaigne 23/11 | [juntos] | Uma exportação do Studio por janela basta; eu gravo com `vp metricas ler`. Refazer o D7 da Idade Média em 16/11 se os números mudarem. |
| 1.6 | **Escuta cega do ritmo da voz** (4 arquivos em `data/benchmarks/voz-ritmo-2026-10-23/cegas/`) | [dono] | Pendente desde 23/10; define o ritmo para o público desanimado (hoje 178 palavras/min, o nicho fala 130). |

## Fase 2: decidir a fase de crescimento (uma ADR, depois da fase 1)

Uma ADR nova que substitua as premissas da validação (CLAUDE.md §12) e aposente o que não se aplica mais (ADRs 018,
023, 026, 028 e a parte E da 031). Decisões do dono, cada uma com a minha recomendação:

| # | Decisão | Recomendação |
|---|---|---|
| 2.1 | **Recorte** dos próximos 4 longos | "Como era ser X", que tem o melhor sinal (CTR 4,2%, 32,7% assistido), mas é um vídeo só. Alternativa: pensador com pergunta pessoal (Montaigne, 27%). |
| 2.2 | **Cadência** | 2 a 3 longos por semana enquanto o recorte é testado, não um por dia (a análise de 08/11 já recomendava isso). |
| 2.3 | **Miniatura** | Escolher pelo teste A/B nativo ("Testar e comparar"), com a variante no estilo da Idade Média contra a atual, não mais fixa no canal de referência. |
| 2.4 | **Métricas** | API do YouTube só de leitura preenchendo o `vp metricas` (eu confiro antes se ela traz impressões e CTR), ou seguir com exportações do Studio. Os créditos do vidIQ renovam em 30/11. |
| 2.5 | **Voz** | A sua voz clonada, mais lenta, com o `calm` como base, uma abertura menos intensa e uma gravação de referência mais íntima (testar numa cena antes de mudar o `providers.toml`). |

## Fase 3: produzir o próximo longo como teste (depois das fases 1 e 2)

- Tema dentro do recorte escolhido, a partir da vizinhança (1.2) e, depois de 30/11, dos vídeos que se destacam no vidIQ.
- Se for "como era ser X": `roteirista-ficcao-historica` com `"fiction": true` (feito em 14/11).
- Título curto e concreto; duas ou três miniaturas no teste A/B desde o primeiro dia.
- Duração de 8–9 min como teste (as pessoas ficam cerca de 3 min em qualquer duração; ver 1.1), esforço nos primeiros
  2 min e a voz da decisão 2.5.
- Uma hipótese escrita antes de publicar (CLAUDE.md §4), lida no D7 e no D28.

## Fase 4: Shorts que levam ao longo

- **Legenda queimada nos Shorts do `motion-video`** (hoje saem sem legenda; 61% das views, 11 s por view). É trabalho
  no motion-kit.
- Todo Short com o **Vídeo relacionado** apontando para o longo e com o fecho do personagem chamando para o canal.
- Medir pela origem do tráfego do longo.

## Fase 5: arrumação, em paralelo e sem mudar decisão

- Status e referências cruzadas das ADRs (lista em `revisao-adrs-2026-11-14.md`).
- A skill `analise-de-formato` ainda trata anime em movimento como impossível de reproduzir.
- Separar e commitar as mudanças de 14/11 num branch próprio (skills do anime, `fiction: true`, documentos de análise).

## Já feito em 14/11

- Diagnóstico do Studio e leitura D7 da Idade Média (`metrics.json` criado).
- Revisão das 55 ADRs.
- Regra do anime alinhada à emenda de 03/11 nas skills `roteiro-explicativo` e `plano-de-imagens` e na ADR 031.
- Ficção histórica com número e data na tela sem claims (`"fiction": true`, ADR 055), com testes.
