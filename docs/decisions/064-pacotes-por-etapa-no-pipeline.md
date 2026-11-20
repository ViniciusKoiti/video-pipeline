# 064 — Pacotes por etapa no `app/pipeline`

- **Status:** aceita pelo dono em 2026-11-19, depois de uma sessão de perguntas com 22 decisões. Aplicação em
  PRs, um por vez; o primeiro registra esta decisão e liga o guarda.
- **Data:** 2026-11-19
- **Relaciona-se com:** ADR 006 (portas e adaptadores), ADR 037 (modelos por área), ADR 038 (constantes por área),
  ADR 042 (fronteiras; reserva `app.pipeline.production` e `app.pipeline.short` para a orquestração), catraca de
  tamanho (`tests/test_tamanho_modulos.py`).

## Contexto

- O `app/pipeline` tinha 65 módulos soltos, 175 modelos numa pasta só e 41 arquivos de constantes: mais da metade
  do `app/` (281 de cerca de 520 arquivos, 12,7 mil de cerca de 23 mil linhas). Os outros pacotes já se dividem por
  responsabilidade: `providers` por porta, `render` por motor, `commands` por subcomando do `vp`.
- Entre 2026-10-19 e 2026-11-19, o `check.py` (576 linhas, 485 de código, na catraca de tamanho) e o `gates.py`
  mudaram cada um em 11 dos 65 commits do `app/`. Toda decisão editorial do dono vira regra do `vp check` ou do
  gate, sempre no mesmo arquivo, e PRs em paralelo conflitam ali.
- Os imports cruzavam as etapas sem direção: o hash do gate 2 usava uma função do `vp numeros`, e a proteção
  e a reabertura usavam hashes e o erro definidos no `gates.py`.

## Decisão

1. **Um subpacote por etapa**, com nomes em inglês como o resto do `app/`:

   ```
   app/pipeline/
   ├── schemas.py · models/ · constants/   contratos do disco (ficam onde estão)
   ├── ports · atomic_files · file_hash · shots · attribution · motion_inputs   base sem etapa
   ├── governance/  state · protection · review_hashes · reopen · failures · scene_step · gate_stamps
   ├── research/    sources · extract · excerpts · format_decision
   ├── script/      check (dividido em checks/, um módulo por regra) · check_report · script_form
   │                funnel_check · objective_check · opinion_labels · narration_gaps · emotion_marks
   │                glossary_check · retention_clock · text_fit · checagem_local · numbers
   │                numbers_citations · molde · radar · briefs
   ├── visuals/     assets · candidates
   ├── sound/       music · music_library · sfx · sfx_inputs
   ├── voice/       voice · voice_state · voice_timeline · voice_retake · speech_review
   ├── publishing/  package · metrics · translation · medicao · affiliate · usage
   ├── bench/       bench · bench_data
   ├── production/  voice_production · caption_production · episode_build · assembly · audio_review
   ├── short/       short_voice · short_timing · short_join · short_mouth · short_speech
   ├── gates.py     junta as conferências das etapas para o `vp approve`
   └── status.py    o antigo pending.py: o que falta para o `vp status`
   ```

2. **Camadas:** base → `governance` → etapas (`research`, `script`, `visuals`, `sound`, `voice`, `publishing`,
   `bench`) → fluxos (`production`, `short`, `gates`, `status`). Um módulo não importa uma etapa de camada acima
   da sua, e não há ciclo entre etapas. Entre etapas da mesma camada, sem ciclo, vale importar. Não há lista
   fechada de dependências permitidas; ela só entra se aparecer acoplamento indesejado.
3. **Os contratos ficam:** `schemas.py`, `models/` e `constants/` continuam na raiz do pipeline e são a base.
   O modelo usado por uma etapa só vai para `<etapa>/models/`, e a constante para `<etapa>/constants/`; as ADRs
   037 e 038 valem em qualquer profundidade.
4. **Guarda:** `tests/test_pipeline_layers.py` aponta cada import que sobe de camada ou fecha ciclo entre etapas
   da mesma camada. A etapa vem do subpacote; o módulo ainda solto na raiz declara a sua em `ROOT_MODULES`. As
   violações de hoje ficam em `KNOWN`, que só encolhe.
5. **Migração, um PR por vez, sempre a partir do `main`, sem PR empilhado:**

   | PR | O que faz | Merge |
   |---|---|---|
   | 0 | Esta ADR, o guarda com a catraca e a regra no CLAUDE.md §3 | Claude |
   | 1 | Quebra as violações da catraca, que fica vazia | Claude |
   | 2 | `short/` e `production/` | Claude |
   | — | Conferências do MP4 depois do render (vindas do #220), em `publishing/` | dono revisa |
   | 3 | `script/` e o `check.py` dividido em `script/checks/` com registro explícito | dono revisa |
   | 4 | `voice/`, `sound/`, `visuals/`, `research/`, `publishing/`, `governance/` e `bench/` | Claude |
   | 5 | Remove as reexportações, migra scripts e testes, atualiza o mapa do CLAUDE.md §3 | — |

   Depois do PR 3 dá para parar, se o ganho já bastar.
6. **Compatibilidade:** o caminho antigo reexporta os nomes até o PR 5, como na ADR 037. O código do `app/`
   importa pelo caminho novo desde o PR que move o módulo; `scripts/provisorio/` e `tests/` podem usar o antigo
   até o PR 5. Skills e docs que citam o caminho mudam no mesmo PR que move; as ADRs antigas não. `voice.py` e
   `bench.py` viram o `__init__.py` dos pacotes de mesmo nome.
7. **Prova em cada PR:** `ruff`, `mypy` e `pytest`, mais `vp check` e `vp status` em dois episódios reais, com a
   saída idêntica antes e depois.
8. **Fora:** `media/`, `commands/`, `providers/` e o resto do `app/`. O `gates.py` só muda de lugar; não vira
   registro nesta mudança.

## Consequências

- Nada muda nos dados dos episódios, nos comandos do `vp`, no `episode.json` nem nos hashes de gate e de cache,
  que vêm dos arquivos de dados e não do caminho do código.
- Uma regra editorial nova do `vp check` vira um arquivo em `script/checks/` mais uma linha no registro, em vez de
  outra edição no mesmo `check.py`.
- Medido no PR 0: quatro imports sobem de camada, por três causas. `GateError` mora no `gates.py`
  (`check_report`, `reopen`); `current_hash` e `legacy_hashes` também (`protection`); e o hash do gate 2 usa
  `strip_block` do `vp numeros` (`review_hashes`). Nenhum ciclo entre etapas da mesma camada.
- PR 1: o carimbo de cada gate (`gate_hash`, `current_hash`, `legacy_hashes`, o hash da tradução) e o
  `GateError` foram para `gate_stamps.py`, em `governance`; o `strip_block` foi para o `review_hashes`.
  O `gates.py` e o `numbers.py` reexportam os nomes usados pelos testes até o PR 5. A catraca ficou vazia.
- Os 12 scripts de `scripts/provisorio/` que importam do `app/` seguem pelos caminhos antigos até o PR 5.
