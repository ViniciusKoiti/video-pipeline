# Rubrica congelada do avaliador (Fase 0, 2026-11-05)

Proposta: a mesma do envio anterior (`scripts/bench/earshot_retry.py`, `PROMPT`, copiada abaixo sem alteração), mais **uma** linha final
nova. Qualquer outra mudança de palavra exige refazer o controle. Modelo `gemini-3.8-flash` passado explicitamente,
`synth_intended=true`, MP3 mono 64 kbps. A meta (8) não aparece no prompt. A nota não mede "parece humano": mede "está bem feita
como voz clonada de propósito". Notas por versão vêm do campo `answer` (o `critique.overall.score` vale para o áudio inteiro).

## PROMPT (verbatim; `{duration}`, `{second_start}`, `{total}`, `{lufs}` preenchidos por chamada)

Responda em portugues do Brasil. Compare duas versoes da MESMA narracao pt-BR. A toca de 0 a {duration:g} s, depois ha 1 s de silencio; B toca de {second_start:g} a {total:g} s. Ambas tem volume integrado {lufs:g} LUFS, duracao {duration:g} s cada, pico abaixo de -1,5 dBTP e diferenca de volume menor que 0,1 LU. Nao sabe qual tratamento recebeu cada uma. A voz clonada e intencional e nao e um defeito por si so. E um ensaio narrado, nao anuncio. Sem imagem, efeitos ou musica: sincronia e musica devem ser nulas. Compare sibilancia em s/ch/x, conforto, clareza, prosodia, corpo, brilho, abafamento, lingua presa e artefatos. Avalie tambem pronuncia de nomes e termos estrangeiros, sem presumir erros. Ignore silencio de preenchimento no fim dos recortes e a pausa separadora; julgue a fala. Nao presuma melhoria. Se forem indistinguiveis, diga empate ou inconclusivo. No campo answer, de uma nota perceptual de 1 a 10 para CADA versao, informe preferencia A/B/empate/inconclusivo e confianca, justificando somente diferencas audiveis especificas. Nao busque uma nota desejada. Separe observacao de hipotese. Nao invente frequencias ou medidas. Diga se a diferenca sustenta alterar a producao. A copia enviada e MP3 mono 64 kbps: explicite a limitacao para sutilezas dos agudos. Notas sao opiniao de LLM, nao MOS validado. Tempos de defeitos sao aproximados.

## Linha acrescentada (única mudança proposta)

Termine a resposta com uma linha exata, sem texto depois: `NOTAS A=<n> B=<n>` (números de 1 a 10).

## Registro

Cada resposta (JSON completo), hash do arquivo, hora, tentativa e status HTTP. Resposta válida entra no registro mesmo com nota baixa;
429/503/timeout é indisponibilidade e não conta como avaliação.

## Variante de clipe único (acrescentada em 2026-11-05, depois do timeout da chamada 1)

O par A+pausa+B de ~65 s deu timeout (Gemini sem resposta em 600 s). Por pedido do dono: (3) repetir o par de U uma vez e (2) avaliar
um clipe por chamada. O prompt do clipe único é o `SOLO` de `fase0_controle.py` (cópia do PROMPT sem as partes de A/B), terminando em
`NOTA=<n>`; vale também `critique.overall.score` do JSON. Notas do par e do clipe único **não se misturam** sem declarar a diferença.
Teto: 6 chamadas HTTP no total da Fase 0 (1 já gasta).
