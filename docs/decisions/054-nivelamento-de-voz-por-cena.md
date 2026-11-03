# 054 — Nivelamento de voz por cena antes da montagem

Data: 2026-11-01. Status: aceita no pedido de incorporar ao fluxo a comparação
nivelada aprovada pelo dono. Relacionada às ADRs 035, 049, 052 e 053.

## Problema

Referências diferentes produziram falas com volume muito diferente. Na comparação
inicial, a neutra em pt-BR estava em −28,14 LUFS e a referência antiga em −13,45 LUFS.
Normalizar somente o vídeo inteiro não equilibra uma cena quieta com outra alta.
O dono aprovou a comparação com as falas niveladas individualmente e pediu sua
incorporação ao fluxo de geração.

## Decisão

- Com `[chatterbox.references]` ativo, a geração de Shorts e longos faz uma cópia de
  cada fala bruta em `voice/leveled/`, pelo FFmpeg, antes de `tempos`, legendas e
  montagem. Duas passagens EBU R128; alvo −16 LUFS, pico −1,5 dBTP, LRA 11,
  PCM 16 bits, estéreo a 48 kHz. O mono é contado nos dois canais, como na escuta.
- `voice_level.py` valida volume, pico e preservação da duração antes de publicar
  o WAV. O relatório JSON contém fonte, hashes, política e volume antes/depois.
  Temporários ficam isolados; falha preserva a síntese bruta.
- O cache das cópias considera bytes do bruto e política de nivelamento. Mudar o
  tratamento local não chama o TTS novamente. Uma cópia ausente/corrompida é refeita;
  referências originais, WAVs brutos e cópias de outras versões são preservados.
- `produce_with_state` registra os caminhos nivelados no estado da voz. Falha numa
  cena vira `needs_review/voice_level_failed`, as outras continuam e a retomada usa
  o bruto já em cache. Áudio sem fala mensurável não é amplificado.
- O registro do Short acrescenta `level`; seu `wav` e o `audio` de `episode.json`
  conservam o subdiretório real. O restante do fluxo recebe esses caminhos, sem
  reconstruí-los só pelo nome do arquivo. Os comandos permanecem os mesmos.
- Provedores e configurações sem o banco ativo mantêm o comportamento anterior.
  O volume final do vídeo, após efeitos/trilha, continua passando pela conferência
  existente. A aprovação de uma comparação não aprova vídeos novos ou publicação.

## Verificação

Testes com FFmpeg real comparam sinais em volumes diferentes, duração, formato,
cache íntegro/corrompido e mudança da política. Testes de integração verificam
Short/longos, metadados, caminhos aninhados e falha por cena com retomada sem TTS.
A CLI real em pt-BR/en reutilizou dez WAVs brutos, gerou as cópias niveladas e
voltou a executá-las sem alterar arquivos; os renders publicados mantiveram os hashes.
