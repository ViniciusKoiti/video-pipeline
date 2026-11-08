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

## Emenda 2026-11-04: Polimento Opcional v2

Implementacao experimental da Fase 1 de `docs/specs/prompt-polimento-de-voz.md`.
**Desligada por padrao; ativacao pendente da escuta e decisao do dono.**

- `[voice_polish]` em `config/providers.toml` declara `enabled = false` e os
  parametros. A composicao dos comandos passa um `VoicePolish` ou `None` aos
  fluxos longo e Short; o nucleo nao importa nem le `Settings`.
- Com `None`, filtros, politica `loudnorm-v1`, nomes e cache permanecem iguais.
  Com polimento, a politica ganha o sufixo `polish-v2` e a cadeia efetiva; muda
  somente a copia em `voice/leveled/`, nunca o WAV bruto ou o cache da sintese.
  Alterar um parametro efetivo muda tambem o hash do estado da voz. Desligar
  volta a reutilizar as copias v1 intactas.
- Ordem antes do loudnorm, nas duas passagens: highpass a 65 Hz, EQ opcional
  (ganho 0 omite o filtro), deesser `i=0.3:m=0.98:f=1.0`. `i`, `m` e `f` sao
  valores normalizados do FFmpeg, nao Hz nem dB. Neste filtro, `m` mais perto
  de 1 limita mais a reducao: 0.98 limita a aproximadamente 0.96 dB. Esses
  valores sao candidatos tecnicos conservadores, nao calibracao de ouvido.
- A verificacao da saida mede o WAV pronto sem reaplicar a cadeia. Continuam
  valendo alvo de loudness, teto de pico e tolerancia de duracao de 20 ms;
  falhas usam `VoiceLevelError` e a recuperacao por cena existente.
- Testes sem rede usam apenas sinais sinteticos: regressao byte a byte contra
  a cadeia anterior, separacao e integridade dos caches, propagacao da politica
  no estado e nos dois formatos, preservacao de duracao, loudness e pico,
  reducao da componente sibilante e preservacao do corpo dentro da tolerancia
  numerica. Nao demonstram preferencia perceptual nem qualidade da voz real.

A Fase 1b continua pendente: cinco falas reais dos WAVs brutos, sem chamar TTS,
ordem cega e chave separada, somente apos autorizacao para gerar as amostras.
Comparar com a baseline preservada em
`data/episodes/ayanokoji-provocacao-epicteto/renders/baseline-voz-2026-11-04/`.
Nao entram nesta emenda ambiencia, ducking ou porta automatica do earshot.
