---
name: trilha
description: |
  Escreve o plano da trilha sonora de um episódio explicativo (`music.json`): que faixa do catálogo entra,
  onde entra e sai (âncoras na narração), em que papel (fundo, transição, silêncio) e em que nível. Use
  depois do gate 2 e antes da voz final e do render (ADR 030). Não ouve áudio: escolhe pelas etiquetas do
  catálogo e pelo texto, e o dono decide na escuta da prévia.
argument-hint: "<episode-id>"
---

# Trilha: a música segue a virada do roteiro

Você não ouve as faixas. Escolhe pelas etiquetas do catálogo (clima, intensidade, voz cantada, loop) e pelo
que a narração faz em cada cena. O dono ouve na prévia e decide no gate 4; "ajustar a música" volta só aqui.

## Entrada

- `data/episodes/<id>/scenes.json`: narração, `delivery` de cada cena (ADR 022), `objective` (ADR 019) e
  os blocos (os títulos de bloco do `outline.md`, se houver).
- `data/music/catalog.json`: as faixas que existem. **Nenhuma faixa fora dele.**

## Saída

`data/episodes/<id>/music.json` (schema `MusicPlan` em `app/pipeline/schemas.py`):

```json
{"episode_id": "<id>", "cues": [
  {"role": "bed", "track": "ytal-<faixa>", "level": "low",
   "start": {"scene": "S01"}, "end": {"scene": "S09", "text": "trecho exato da narração"},
   "fade_in_ms": 1500, "fade_out_ms": 2500, "why": "abertura em tom de confissão (delivery hook)"},
  {"role": "silence", "start": {"scene": "S10"}, "end": {"scene": "S10"},
   "why": "a frase do dono que decide fica sem música"}
]}
```

- A âncora é um trecho **literal** da narração da cena (sem as marcas `<short pause>`). Sem `text`, a entrada
  vale no começo da cena e a saída, no fim.
- `level`: `low` por padrão; `mid` só em trecho sem narração densa (abertura curta, pausa entre blocos).
- `track_offset_ms` pula o começo da faixa quando a introdução não serve.

## Método

1. **Leia o roteiro inteiro antes de escolher.** Marque as viradas: troca de bloco, a `delivery` `turn`, a
   pergunta final (`invite`), as frases do dono (opinião e confissão).
2. **Poucas faixas.** Duas ou três por vídeo de até 12 min. A troca de fundo só acontece numa virada; o
   `vp check` recusa mais de um fundo novo por minuto, em média.
3. **O clima segue a entrega da cena** (ADR 022):
   - `hook` (abertura): faixa de intensidade baixa a média, que entra já no começo;
   - `calm` (a conta, a explicação): fundo de intensidade 1 ou 2, ou nenhum;
   - `turn` (virada): a troca de faixa entra aqui, ou um silêncio curto antes;
   - `invite` (pergunta final): a faixa da abertura volta, se o fecho volta à abertura.
4. **Silêncio antes da frase que decide.** A frase do dono que fecha um bloco, a confissão e a tese do fecho
   ficam sem música (`silence`) ou com o fundo já saindo (fade de saída terminando na âncora).
5. **Nada de voz cantada sob a narração.** Faixa com `vocals: true` não entra.
6. **Fundos não se sobrepõem.** Um termina antes do próximo começar; a transição curta (`sting`) pode ficar
   por cima de um fundo.
7. **Escreva o motivo** em `why`, ligado à cena: a entrega, a virada, o bloco.

## Antes de entregar

- `.venv/bin/vp check <id>` sem erro de `music.json`.
- Para cada faixa usada: `scripts/provisorio/catalogo_musica.py usar <id> <faixa>` copia o ativo para o
  episódio; o gate 3 da faixa é do dono (`vp approve <id> --step assets --asset <faixa>`).
- Entregue: faixas escolhidas e por quê, onde ficam os silêncios, e o que o dono precisa ouvir com atenção.
