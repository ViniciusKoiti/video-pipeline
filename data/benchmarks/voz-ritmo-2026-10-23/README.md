# Escuta cega do ritmo da voz final (2026-10-23/24)

**Pergunta ao dono:** qual destas quatro versões soa mais natural, mais parecida com a narração do nicho (vídeo do
Montaigne do A Psique, `LWuZr9304Y4`, 130 palavras por minuto, quase sem pausa audível, voz nivelada)?

Ouça `cegas/voz-1.wav` a `cegas/voz-4.wav` sem abrir `gabarito.json`. Ordene da melhor para a pior e anote o
motivo em uma linha cada. Depois abra o gabarito. O texto é o mesmo nas quatro: a cena S05 do `epicteto-na-sua-mao`
(140 palavras), narrada pela sua voz clonada (`chatterbox_modal`).

## As variantes, uma variável por vez

| Variante | O que mudou | Como foi feita |
|---|---|---|
| A, atual | nada: é o WAV que está no episódio | `voice/S05-chatterbox_modal-ef1b7d8f0d.wav` |
| B, cfg 0,6 | só o `cfg_weight` do Chatterbox, de 0,5 para 0,6 (`exaggeration` igual, 0,5) | uma chamada nova ao Modal em 24/10, 92 s |
| C, atempo 0,92 | só a velocidade, 8% mais lenta, altura preservada | `ffmpeg -af atempo=0.92` sobre A |
| D, compressor | só a dinâmica: compressor suave na voz | `ffmpeg -af acompressor=threshold=-24dB:ratio=3:attack=15:release=250:makeup=4dB` sobre A |

## O que a medição diz (antes da escuta)

Medido por `scripts` descartáveis com numpy e ffmpeg (altura por autocorrelação, pausas a −40 dBFS e 0,3 s):

| Variante | Palavras/min | Pausas/min | Silêncio | Altura (Hz) | Variação de tom (desvio, st) | Dinâmica p10–p90 (dB) |
|---|---|---|---|---|---|---|
| A, atual | 178 | 14,0 | 10,9% | 134 | 4,21 | 17,2 |
| B, cfg 0,6 | 187 | 13,4 | 10,8% | 131 | 4,24 | 17,1 |
| C, atempo 0,92 | 164 | 14,0 | 11,4% | 134 | 4,27 | 17,5 |
| D, compressor | 178 | 12,7 | 10,2% | 134 | 4,23 | 10,4 |
| Referência (A Psique, no mix) | 130 | ~0 audível | — | 124 | 2,97 | 11,3 |

Leitura:

- **B não desacelerou.** Subir o `cfg_weight` deixou a fala 5% mais rápida nesta cena, com as mesmas pausas. O
  comentário do `providers.toml` ("quanto menor, mais vivo e rápido") não se confirmou neste caso; a alavanca de
  ritmo não é o cfg.
- **C é a única que muda o ritmo** (164 por minuto), e ainda fica acima do nicho. Para chegar a 130–150 só pela
  velocidade seria preciso 0,80–0,85, que costuma soar arrastado. O resto do caminho é o roteiro: frases mais
  longas e menos pontos finais (regra nova nas skills `humanizer-narracao` e `roteiro-explicativo`).
- **D aproxima a dinâmica da referência** (10,4 dB contra 11,3) sem tocar na fala. É o candidato para a junção, se
  a escuta aprovar.
- A variação de tom é igual nas quatro e já é maior que a da referência: não é o que falta.

## Registro

- `medidas.json`: os números acima por arquivo.
- `gabarito.json`: qual `voz-N` é qual variante (ordem sorteada com semente fixa).
- Decisão do dono: *pendente*. Anotar aqui a ordem escolhida, a data e o que entra no `providers.toml` ou na junção.
- A S05 do Epicteto foi usada só como texto de teste; o episódio não mudou.
