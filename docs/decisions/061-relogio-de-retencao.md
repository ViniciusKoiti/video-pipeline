# 061 — Relógio de retenção no roteiro: promessa, gancho de retomada e pausa de aviso

- **Status:** aceito pelo dono em 2026-11-16 ("vamos alterar para seguir esse padrão"), como teste. Os limites
  podem mudar com as leituras do D7 e do D28.
- **Data:** 2026-11-16
- **Pedido do dono:** os pontos levantados no `vazio-de-ter-tudo` (publicado em 15/11): "a promessa central só fecha
  em 00:00:31", "a virada prática só começa em 00:04:18" e "antecipar uma prévia da virada ou um micro-gancho forte
  logo após o bloco do CVV".
- **Relaciona-se com:** ADR 019 (objetivo e promessa), ADR 022 (entrega por cena), ADR 031 (molde e partitura),
  ADR 052 (estado da voz por cena); `docs/pesquisa/retencao-idade-media-2026-11-14.md`.

## Contexto

As curvas dos dois melhores longos mostram cerca de 40% saindo nos primeiros 30 s, cerca de 60% até os 2 min, e as
pessoas ficando uns 3 min em qualquer duração. No `vazio-de-ter-tudo`, pela voz real: a pergunta S04 termina em
0:34, o aviso do CVV ocupa S20–S21 (2:37–3:00), a cena seguinte abre outro bloco ("A anestesia", 3:00) e a primeira
virada (S41) entra em 5:24. Nada no código sabia que cena fecha a promessa, que cena retoma a atenção ou que cena é
um aviso; o relógio do `vp check` só estimava a duração total, e errava: 7,2 min estimados para 7:47 reais.

## Decisão

1. **Campo `beat` na cena** (opcional): `promise` (a cena que fecha a promessa), `rehook` (gancho de retomada:
   antecipação forte ou pergunta nova), `turn` (virada para a parte prática) e `pause` (aviso: CVV, saúde). O
   roteirista marca; o campo não muda voz, tela nem render. `delivery` continua dizendo só como a voz entrega.
2. **O relógio do `vp check`** (`app/pipeline/retention_clock.py`), só em vídeo de 4 min ou mais:
   - a cena `promise` termina até 0:30;
   - uma cena `rehook` ou `turn` toca a janela de 2:00 a 3:00;
   - depois de uma cena `pause` (ou de uma sequência delas), a seguinte é `rehook` ou `turn`;
   - roteiro longo sem nenhum `beat` pede as marcas.

   Tudo isso sai como ponto de `atenção` para o gate 2, não como erro: a regra é um teste. Cena que fala do CVV
   sem `beat: pause` gera alerta.
3. **Tempo real quando existe.** Com a voz de todas as cenas pronta no `manifest.json`, o relógio usa a duração dos
   WAVs (`app/pipeline/voice_timeline.py`, medida pelo `ffprobe` na linha de comando); antes, estima pelo texto. A
   linha diz qual: "voz real" ou "estimado". Rodar o `vp check` de novo depois do `vp voice` confere o relógio que
   vai ao ar.
4. **Skills.** `roteiro-explicativo` marca as cenas e escreve para o relógio; `edicao-de-roteiro` lê as linhas
   "relógio" e transforma o que falhar em nota `ABERTURA` ou `TENSÃO`. "Promessa mais cedo segura mais" sai da lista
   do que não se usa como regra: o alvo de 0:30 é regra do dono, mesmo sem prova nas curvas.

## Consequências

- `app/pipeline/models/scene.py` (`beat`), `app/pipeline/models/_schemas_types.py` (`Beat`),
  `app/pipeline/retention_clock.py`, `app/pipeline/voice_timeline.py`,
  `app/pipeline/constants/retention_clock_constants.py`; `tests/test_retention_clock.py`.
- A forma do roteiro sai de `check.py` para `app/pipeline/script_form.py` (objetivo em
  `app/pipeline/objective_check.py`), pelo gate de tamanho; o `check_episode` recebe `measure`.
- Roteiros antigos continuam válidos; os longos sem `beat` passam a ter um ponto de atenção.
- Limites em `RetentionClockConstants`: mudar a janela é mudar a constante e esta ADR.
