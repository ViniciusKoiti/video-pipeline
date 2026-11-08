# Rubrica congelada do avaliador (rascunho da Fase 0, 2026-11-05)

Vale para controle e candidatas, sem alteração entre chamadas. Muda uma palavra, muda a versão e o controle é refeito.

- Ferramenta: `llm_critique` do earshot, modelo `gemini-3.8-flash` passado explicitamente, `synth_intended=true`,
  `with_timeline=false`, sem vídeo. Um trecho por chamada, nome de arquivo neutro (`clipe-<hash curto>.wav`).
- Nota que conta: `critique.overall.score`; secundárias `scores.realism`, `scores.mix_balance`, `scores.loudness`.
  `sync` e `music` esperados nulos (sem imagem nem trilha).
- A nota **não mede "parece humano"**: mede "está bem feita como voz clonada de propósito".
- A meta (8 a 10) **não aparece** no prompt.

## Texto do campo `prompt`

Responda em português do Brasil. Trecho de um ensaio narrado em pt-BR, sem imagem, efeitos nem música. A voz é clonada de
propósito; síntese não é defeito por si só. Avalie só o que se ouve: sibilância em s/ch/x, aspereza, brilho, abafamento,
estalos, pronúncia de nomes e termos estrangeiros, prosódia (entonação, final de frase, pausas), consistência de timbre e
conforto de ouvir por vários minutos. Separe observação de hipótese. Não invente frequências nem medidas. A cópia enviada é MP3
mono 64 kbps: diga o que essa limitação impede de julgar. Para cada defeito dê tempo aproximado, severidade e a causa provável
(processamento de áudio, pronúncia/texto, entrega da fala, timbre da referência). Se não houver defeito, diga que não há.

## Registro de cada resposta

Guardar o JSON completo (`full=true`), hash do arquivo, hora, tentativa, status HTTP. Resposta válida entra no registro mesmo
com nota baixa; 429/503/timeout é indisponibilidade e não conta como avaliação.
