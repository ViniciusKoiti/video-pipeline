# Loop da refatoração SOLID: uma iteração

Prompt de cada rodada do `/loop` (sem intervalo, o próprio modelo marca a próxima). Fonte da verdade e critérios:
[fluxo-refatoracao-solid-2026-11-01.md](fluxo-refatoracao-solid-2026-11-01.md). Regras do projeto: `CLAUDE.md`.

## Escopo desta rodada de loops

**Até o fim do RF5**, e só isto: os três critérios `[ ]` do RF5 (entradas do kit validadas, preservação dos campos
que o auto-play não interpreta, briefs e catálogo de música). **Não iniciar o RF6 nem o RF7**: eles mexem nos
scripts de produção do dono e dependem de decisões dele (nome dos WAVs dos Shorts, condições da voz final e do
render final).

## Uma iteração (uma fatia pequena, nada além)

1. `git status`, `git log --oneline -5` e a seção 1, o RF5 e a seção 5 do fluxo. Se todos os critérios do RF5 já
   estão `[x]`, vá para "Parar".
2. Escolha **um** critério `[ ]` do RF5 e leia o código e o gap (G10) antes de escrever. Não deduza o formato
   de arquivo do kit: leia `app/pipeline/sfx.py`, `app/pipeline/music.py`, `app/media/` e os scripts que o usam.
3. Implemente a fatia em `app/` (modelos em `models/`, constantes em `constants/`, erros herdando
   `PipelineError`, sem `try/except` de erro do projeto em comando ou script, `Context` sem `Settings`).
   Scripts viram chamadores finos de `app/`, com os mesmos argumentos.
4. Testes com pasta temporária e fakes, sem rede. Cada teste novo importante deve **falhar** com uma mutação do
   defeito (faça a mutação, confira, restaure o arquivo). Nunca `skip`/`xfail` para cumprir critério.
5. `bash scripts/check_qualidade.sh` precisa passar. Não regenere `tests/baseline_tamanho_app.json` para aceitar
   crescimento (só para registrar encolhimento).
6. Documente: ADR em `docs/decisions/` se houve decisão de arquitetura; marque `[x]` só o que foi provado, com a
   evidência e as ressalvas no fluxo; `CLAUDE.md` se uma regra mudou.
7. Commit só dos arquivos da fatia (nunca `git add -A`; `data/publicacoes/registro.jsonl` e os untracked que não
   são seus ficam de fora), mensagem no padrão do histórico e a linha `Co-Authored-By` da sessão.
8. Relate em até 10 linhas (o que mudou, números do gate, ressalvas) e agende a próxima iteração em 60 s com o
   mesmo prompt.

## Parar (sem agendar nova iteração: `ScheduleWakeup` com `stop: true`) e relatar ao dono

- Todos os critérios do RF5 estão `[x]`: relatório final e a recomendação para o RF6.
- Surgiu decisão que é do dono: formato persistido que invalidaria cache ou arquivo aprovado, política, nome de
  arquivo, licença, ou qualquer ponto de "Perguntas" que você não consegue responder lendo o código. Escreva a
  pergunta com a recomendação e pare.
- O gate ou um teste falha duas vezes na mesma fatia depois de corrigida, ou o ambiente nega uma ação: relate, não
  contorne a negação.
- A fatia exigiria rede, render, TTS real, Postiz, a sonda de CPU (`cpu_probe`) ou mexer em episódio, em arquivo
  `approved`, em `.claude/settings` ou na rotina diária.
- Dois commits seguidos sem avanço de nenhum critério.
