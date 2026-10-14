# 021 — Legenda por frase no vertical, sempre visível

- **Status:** aceito pelo dono em 2026-10-14 (decisões D4 e D6 da issue #116, respondidas na sessão)
- **Data:** 2026-10-14
- **Etapa do roadmap:** legendas (#17) e texto cinético (#80)
- **Relaciona-se com:** ADR 011 (decisão 5, emendada aqui), ADR 014 (legenda queimada no vertical), ADR 015
  (pausas na narração), ADR 016 (voz final)

## Contexto

A ADR 014 manda queimar a legenda no final vertical, porque a maior parte de quem vê um Reel começa sem som.
O render já lia um SRT (`app/render/remotion.py`), mas ninguém o gerava: `captions` estava nulo em todos os
`episode.json`, e o primeiro reel da série 1 (`confeitaria-ingrediente-pt`) chegou à prévia sem legenda.

Dois pontos estavam em aberto no spec da #116:

- **D4, o método.** Alinhamento fino (palavra por palavra) pede modelo novo (Whisper local) ou provedor externo
  (Groq). O §9 do CLAUDE.md fala em "alinhamento do texto com o áudio", mas o primeiro reel só precisa que a
  fala inteira seja lida sem som.
- **D6, a convivência com o `keyword`.** A decisão 5 da ADR 011 esconde a legenda enquanto um `keyword` está na
  tela ("o mesmo texto duas vezes confunde"). No reel 1, três cenas (S01, S03, S06) têm `keyword` com só uma
  parte da fala; sem som, o resto da frase some.

## Decisão

1. **Legenda por frase, com o tempo tirado do WAV de cada cena** (`app/media/captions.py`). A fala é dividida
   nas marcas `<short pause>` (ADR 015), no fim das orações e, quando a frase não cabe em duas linhas
   (`MAX_CHARS` = 60), nas vírgulas ou perto do meio. Cada fronteira cai no fim de um silêncio detectado
   (`silencedetect`, o mesmo de `app/media/pauses.py`) perto da posição proporcional ao texto; numa marca de
   pausa a busca vai mais longe, porque o silêncio existe com certeza. Sem silêncio por perto, a fronteira fica na
   posição proporcional e o script conta quantas ficaram assim. Os blocos cobrem a cena inteira, sem lacuna.
2. **`captions.srt` é editável e só é refeito quando a fala muda.** A chave (`captions.key`) cobre o nome dos
   WAVs (que já leva o hash do texto e da voz), o limite de caracteres e a versão do método. Trocar a voz, como na
   voz final da ADR 016, refaz a legenda e guarda a anterior em `captions.old.srt`, para revisar de novo.
3. **Conferência antes do render.** Bloco sem tempo ou sem texto, intervalo invertido, bloco que começa antes do
   anterior acabar ou que termina depois do áudio param o script. O script lista os blocos com número (em
   algarismo ou por extenso) e com nome próprio para a revisão humana; a narração escreve os números por extenso
   para a voz, e quem revisa pode trocá-los por algarismos no SRT.
4. **A legenda não some com o `keyword` (emenda à decisão 5 da ADR 011).** A frase-chave fica no centro e a
   legenda na base da área segura, as duas ao mesmo tempo. A repetição parcial é aceita; perder a fala sem som,
   não.
5. **Fora desta decisão.** Destaque palavra a palavra (`WordCaption`, guia de animação de texto §3) continua
   proibido sem tempo por palavra vindo do áudio; o modelo proporcional não serve para isso. Alinhamento fino
   (Whisper local ou Groq) fica para quando a revisão do SRT por frase se mostrar o gargalo (#123).

## Consequências

- Todo episódio montado por `scripts/provisorio/montar_episodio.py` sai com `captions` preenchido, e o vertical
  queima a legenda na prévia e no final.
- O tempo das fronteiras é bom nas pausas e nos fins de frase com respiração; no meio de uma frase longa sem
  silêncio ele é aproximado. A revisão do SRT é parte do gate 4.
- Mudar a divisão ou o tempo exige subir `VERSION` em `app/media/captions.py`, o que refaz as legendas geradas.
- Nenhuma dependência nova e nenhum provedor externo.
