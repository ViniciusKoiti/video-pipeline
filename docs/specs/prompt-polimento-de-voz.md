# Prompt: polimento da voz (de-esser, EQ, ambiência comum, porta do earshot)

Prompt para abrir a frente de qualidade da voz final. Escrito em 2026-11-04 a pedido do dono, depois da conferência no código
(`app/media/`, `app/render/`, `app/settings/`). Não é decisão: cada fase termina numa parada para o dono ouvir e decidir.

## Pedido

Melhorar a qualidade da voz final (Chatterbox no Modal, voz clonada do dono) com quatro mudanças, da menos para a mais
complexa. O que existe hoje e o que falta foi conferido no código:

| Item | Hoje | Complexidade |
|---|---|---|
| De-esser + EQ da voz | Não existe. A única correção de voz é o nivelamento `loudnorm` em duas passagens (`app/media/voice_level.py`, ADR 054) | **Menos complexo** |
| Teste cego A/B (com e sem a cadeia) | Não existe. Há precedente: o teste cego do ritmo da voz em `data/benchmarks/` | **Menos complexo** |
| Ambiência comum (room tone) | Não existe. Cena gerada separada, sem "sala" em comum | **Mais complexo (médio)** |
| Porta automática do earshot com limiares de voz | `vp audio` existe, mas só reprova loudness, pico real e ataque do corte a 40 ms; roda a pedido, não é parte do render | **Mais complexo (médio a grande)** |

O ducking da trilha já existe (`DUCKING` em `app/render/constants/ffmpeg_constants.py`, `music_mix` em `app/render/ffmpeg.py`,
ADR 030) e **não entra neste pedido**.

## Fase 1 (menos complexa): de-esser + EQ como política v2 do nivelamento, desligável

Contexto a ler antes: `app/media/voice_level.py` (105 linhas), `app/media/constants/voice_level_constants.py`,
`app/pipeline/voice_state.py` (chama `level_voice` e grava `level_policy()` nas linhas 43, 51 e 111),
`tests/test_voice_level.py`, ADR 054, ADR 042 (o núcleo `app/media` não lê `Settings`).

O que fazer:
1. `level_voice(source, polish=None)`: com `polish=None` o filtro, o nome do arquivo e a política ficam **idênticos aos de hoje**.
   Com polimento, o sufixo da política muda e a cópia nasce com outro nome em `voice/leveled/`, sem tocar no WAV bruto.
2. A cadeia entra **antes do `loudnorm`**, na medição (`_measure`) e na geração (`_generate`), para o nivelamento medir a voz já
   polida. Etapas: `highpass` baixo, `equalizer` só se a escuta pedir, `deesser` (opções do ffmpeg: `i` intensidade, `m`
   redução máxima, `f` frequência, todas de 0 a 1; `i=0` é o padrão e não faz nada). Valores iniciais conservadores, a calibrar de ouvido.
3. Chave em `config/providers.toml` (`[voice_polish]`, `enabled = false` por padrão, parâmetros ao lado). A composição passa o valor;
   `app/media` não lê `Settings`. Os três pontos de `voice_state.py` recebem o mesmo valor.
4. Módulo novo para a cadeia (o `voice_level.py` já tem 105 linhas e o projeto limita o tamanho dos arquivos em `app/`). Constantes
   em classe própria (ADR 038), modelos em `models/` (ADR 037), erro herdando de `PipelineError` (ADR 045).
5. Testes sem rede, em `test_voice_level.py`:
   - regressão: `polish=None` gera a saída byte a byte igual à de antes;
   - com polimento: volume dentro do alvo (−16 LUFS ± tolerância), pico abaixo do teto, duração igual (tolerância de 20 ms que já existe);
   - efeito: num sinal sintético com chiado na banda do "s", a energia dessa banda cai e o resto não muda.
6. Emenda à ADR 054 (política v2, desligada por padrão) e uma linha no CLAUDE.md §9 só se o dono aprovar ligar.

Aceite: `uv run pytest` e `uv run ruff check .` limpos; nada do que já existe é regenerado com `enabled = false`.

## Fase 1b (menos complexa): teste cego A/B

Script em `scripts/bench/` (padrão dos outros): escolhe 5 falas de episódios reais, incluindo frases com muito "s", "ch" e "x";
gera A (sem polimento) e B (com) a partir dos WAVs brutos já existentes (**sem chamar o TTS**); embaralha a ordem num arquivo de
chave guardado à parte; grava o resultado em `data/benchmarks/`. Critério proposto: B vira padrão se o dono preferir B em pelo
menos 4 de 5 sem notar artefato. Se não, fica desligado e o resultado é registrado.

**Parada:** o dono escuta e decide. Não ligar `enabled` sem essa decisão.

## Fase 2 (mais complexa, só se pedida): ambiência comum

Não entra na cópia nivelada por cena: reverb ou cauda alonga a duração e o `level_voice` reprova se a duração mudar. O desenho certo é
uma **cama contínua** (−50 a −55 dB) sob o episódio todo, mixada na junção, onde a trilha já entra (`music_mix`). Precisa de ~30 s de
silêncio da sala do dono (dado pessoal, fora do Git) ou de ruído sintético, e de conferir que a cama não atrapalha o ducking nem a loudness.
Emenda à ADR 030. Só começar se, depois da Fase 1, a voz ainda soar "de estúdio".

## Fase 3 (a mais complexa, por último): porta do earshot

Chamar o `vp audio` ao fim do render e reprovar por limiares de voz (sibilância, timbre). Custos a tratar: cada chamada carrega os
modelos (~30 s), a sonda de CPU vale, e os limiares de timbre **não existem hoje**: precisam ser calibrados com o teste cego da Fase 1b
e com a escuta do dono. Começar propondo os limiares e as medidas, sem ligar a porta.

## Regras que valem em todas as fases

- Nenhum render, vídeo ou voz de teste sem pedir ao dono; um render por vez, e só depois da sonda de CPU (`cpu_probe()`, > 0,3 s = máquina limitada).
- Baseline: `data/episodes/ayanokoji-provocacao-epicteto/renders/baseline-voz-2026-11-04/` (prévia, `scenes.json`, `SHA256SUMS`, política
  `loudnorm-v1`, sem de-esser, EQ nem ambiência). Comparar sempre com ela; não apagar.
- Arquivos de gates aprovados são imutáveis (§2.6); nada em `data/episodes/*/` com `review_status: approved` é alterado.
- Sem dependência nova sem justificativa e licença (§2.9). Testes sem rede (§2.10). O custo zero continua valendo (§2.1).
- Mudança de política afeta todos os vídeos: ADR/emenda e decisão do dono antes de ligar.
- Antes de encerrar cada fase: `uv run pytest` e `uv run ruff check .`.
