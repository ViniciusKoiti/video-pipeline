# Fase 0 do loop de voz: proposta (2026-11-05, revisão 2)

Status: **proposta para o dono; nada foi enviado ao Gemini, nenhuma voz foi gerada e nenhum trecho foi montado.**
Segue `docs/specs/prompt-loop-voz-earshot.md`. Dados dos trechos e hashes em `controle.json`.
Revisão 2: o dono pediu que o ajuste use o **último vídeo**, e que a pronúncia seja **outro laço** (ver o fim).

Verificado localmente: os WAVs nivelados dos trechos existem, todos com −16,0 ± 0,4 LUFS e pico −1,5 dBFS (ffmpeg `ebur128`); sonda de CPU 0,048 s.

## Trechos propostos

| Id | Conjunto | Vídeo | Duração | Por que este |
|---|---|---|---|---|
| U | **ajuste** | `short-circuit-breaker-java-pt`, o Short inteiro (7 falas; voz final gerada em 2026-11-05) | 32,0 s | termos em inglês (circuit breaker, Java, threads), números por extenso ("sessenta para vinte e quatro"), uma frase longa no fim, entrega `hook` na abertura |
| R1 | **reservado** | `guia-mastermind-estoico` (S01+S02) | 32,1 s | narrativa de abertura, nomes (Light Yagami, FBI) |
| R2 | **reservado** | `guia-mastermind-estoico` (S22+S23) | 37,6 s | tese marcada como opinião, números de capítulo |
| R3 | **reservado** | `ayanokoji-provocacao-epicteto` (S27) | 29,1 s | cena longa, retomada de pergunta |

O R3 do desenho anterior (o vídeo do boicote, político) saiu. O ajuste tem **um** trecho de 32 s, porque o último vídeo é um Short. O reservado nunca guia um ajuste e vem de dois
vídeos longos diferentes, para o padrão valer também fora do Short. O trecho U é do próprio vídeo, então a voz que se ajusta é a que o dono acabou de ouvir.

Limite do desenho: com só um trecho de ajuste, uma melhora pode ser sob medida para ele. O reservado existe para pegar isso. Se o dono quiser dois pontos de ajuste, dá para
cortar o U em duas metades (gancho+fechado+aberto, 13,5 s; o resto, 18,6 s); curtas demais, o avaliador oscila mais.

## Rubrica

A mesma do envio anterior: `scripts/bench/earshot_retry.py`, constante `PROMPT` (A/B às cegas, notas de 1 a 10 por versão, preferência, confiança, "não busque uma nota
desejada", MP3 mono 64 kbps declarado, voz clonada intencional). Uma mudança proposta: terminar a resposta com a linha exata `NOTAS A=<n> B=<n>`, para a nota ser lida sem
interpretar texto livre. A meta (8) não entra no prompt. No A/B, o `critique.overall.score` estruturado vale para o áudio inteiro e não separa as versões; as notas por versão
vêm do campo `answer`.

## Plano de chamadas (para o dono autorizar, com o teto dito)

A calibração usa **controle contra controle** (o mesmo áudio como A e como B), que mede direto o ruído do avaliador. Avaliações por trecho: **3** (decisão do dono, 2026-11-05).

| Etapa | Chamadas | Conteúdo |
|---|---|---|
| Fase 0: ruído | 3 | U, controle × controle, 3 vezes |
| Fase 0: linha de base do reservado | 3 | R1, R2, R3, controle × controle, 1 vez cada |
| **Total Fase 0** | **6** | 32 s a 38 s de áudio por chamada (A + 1 s + B, ~65 a 76 s) |
| Cada rodada (se o dono liberar) | até 2 | 2 candidatas × U (A/B controle × candidata, ordem sorteada) |
| Verificação da vencedora | até 9 | R1, R2, R3 × 3 avaliações (mediana) |

Máximo (3 rodadas): 6 + 6 + 9 = **21 chamadas**; um caso típico (1 rodada): 17. Passa do teto de 12 da rodada anterior: **autorização nova**. Intervalo de 5 minutos entre chamadas e
retentativa só para 5xx, como em `earshot_retry.py`. Camada gratuita, sem faturamento, sem trocar de modelo (`gemini-3.8-flash`). O áudio enviado é voz sintética clonada do dono,
como nos envios já autorizados; vai como MP3 mono 64 kbps (o earshot converte sozinho; o Gemini já avisou que isso limita o que ele julga nos agudos).

## O que eu preciso que o dono decida

1. Autoriza a **Fase 0**: 6 chamadas, no máximo, com os 4 trechos acima? (O teto das rodadas seguintes fica para uma segunda autorização, depois de ver a dispersão.)
2. O ajuste fica com um trecho (U inteiro) ou em duas metades?

## Pronúncia: outro laço (fora desta fase)

Por decisão do dono, a pronúncia não entra no loop de DSP. O último vídeo já mostra o ponto de partida: o glossário dele tem `Java` → "Djáva", `threads` → "trédis" e `circuit breaker` →
"sârquit brêiquer". O laço próprio da pronúncia teria de testar cada termo em frases curtas e deixar o **dono escolher de ouvido**; o Gemini não é confiável nisso (o experimento de
`ayanokoji-pronuncia-s01` nunca teve resposta: 5 tentativas, 4 erros 503 e 1 timeout). Cada geração de teste é chamada ao Modal e pede o pedido do dono.

## Se nada disso for autorizado

Nada acontece: o loop não roda e o áudio não sai da máquina.
