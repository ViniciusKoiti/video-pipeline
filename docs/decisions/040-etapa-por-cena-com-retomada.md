# ADR 040 — Etapa por cena com retomada

Data: 2026-11-01. Status: aceita (RF2 do [fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md),
gap G03 da análise de gaps de 2026-10-31 (removida; o resumo está em [refatoracao-resultado](../refatoracao-resultado-2026-11-01.md), §4 e §7)).

## Contexto

`for_each_scene` continua depois de um `ProviderError`, mas ninguém guardava o que cada cena deixou. Com
`plan`, uma etapa `needs_review` com a mesma entrada era reaproveitada inteira: a cena que falhou nunca era
tentada de novo. `run_step` devolvia só o estado, não confirmava que as saídas ainda existiam, travava para
sempre num `RUNNING` deixado por processo interrompido e conferia a entrada antes do lock.

## Decisão

- `StepState.scenes` guarda um `SceneRecord` por cena (`COMPLETED` com as saídas, `NEEDS_REVIEW` com
  `reason`/`detail`, `PENDING` com `reason="blocked"`). Campo novo com padrão vazio: manifestos antigos valem.
- `run_scenes` (`app/pipeline/scene_step.py`) tenta só as cenas sem registro íntegro; grava o manifesto a cada
  cena; a cena só vira `COMPLETED` depois que a ação terminou e as saídas existem (existem e não estão vazias).
  Interromper no meio (`KeyboardInterrupt`) deixa a cena sem registro. `depends_on` bloqueia só as dependentes.
- **`needs_review` com dois sentidos, distinguidos pelas cenas:** com cena pendente é produção incompleta e
  volta a rodar com a mesma entrada; sem cena pendente é só revisão humana e o resultado íntegro é reaproveitado.
- `plan` reaproveita apenas resultado íntegro (`pending_scenes` e `missing` pedem nova rodada); etapa aprovada
  nunca roda sozinha: entrada nova é `StaleApproval`, saída ausente é `OutputMissing` (§2.6).
- O desfecho de cada cena é reconstruído do `manifest.json`, também no reaproveitamento e após reiniciar.
- **Lock:** um só por rodada, tomado em `run_step`/`run_scenes`; a ação não aninha `store.lock`. `RUNNING ->
  RUNNING` passa a ser transição válida: quem consegue o lock de uma etapa `RUNNING` está retomando uma rodada
  interrompida, porque o lock do SO morre com o processo.
- **Entrada mutável:** `input_hash` pode ser um callable, resolvido sob o lock e conferido de novo no fim; se
  mudou, a etapa vira `failed` (`InputChanged`) e a entrada nova refaz tudo.
- Erro que não é de provedor segue sendo bug: etapa `failed`, cenas concluídas gravadas, exceção sobe.

## Fora do escopo

Ligar `run_scenes` ao narrador e à voz (RF3/RF6); substituir `for_each_scene`; recuperação de publicação de
vários arquivos (G02, RF5/RF6).
