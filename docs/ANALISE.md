# Análise inicial do repositório (2026-09-24)

Questões encontradas ao organizar o projeto a partir do `CLAUDE.md`, e o que foi feito com cada uma.

| # | Questão | Situação | Ação |
|---|---|---|---|
| 1 | Arquivo se chamava `CLAUDE.MD`; o Claude Code procura `CLAUDE.md` e o Linux diferencia maiúsculas. | Resolvida | Renomeado para `CLAUDE.md`. |
| 2 | §3 dizia que o projeto vive em `~/video-pipeline`; ele está em `~/projetos/auto-play` (também no FS Linux, fora de `/mnt/c`). | Resolvida | Texto do §3 atualizado; repositório no GitHub chama-se `video-pipeline`. |
| 3 | `docs/spec-v0.4.md` é a "fonte de verdade", mas não existia. | **Aberta** | Placeholder criado. O dono do projeto precisa colar a spec original. |
| 4 | `mermaid.txt` estava vazio; o §4 aponta `docs/pipeline-flowchart.mermaid`. | Resolvida | Diagrama extraído do §4 para `docs/pipeline-flowchart.mermaid`; `mermaid.txt` removido. |
| 5 | `app/pipeline/schemas.py` e `tests/fixtures/episodes/pilot-example/` são citados no §14 mas não existem. | Aberta | Etapa 3 do roadmap. |
| 6 | Ambiente: Python 3.14 e ffmpeg presentes; **Ollama e Kokoro não instalados**; `.wslconfig` não verificado. | Aberta | Etapa 1 do roadmap. |
| 7 | Conflito §7 × §13.2: provedor de texto padrão é Ollama na spec, mas o §13 propõe Gemini/Groq gratuito. Cinco decisões do §13 não têm ADR. | Aberta | ADRs 001–005 mapeados em `docs/decisions/000-template.md`; etapas 1, 8, 19, 25, 28. |
| 8 | A ordem do §11 (A→G) coloca pesquisa e roteiro (F) depois de render e ativos. Um episódio real precisa de F antes de D/E. | Aceita | O roadmap mantém a ordem da spec para o piloto técnico: um roteiro de teste fixo (etapa 5) alimenta as etapas B–E; F entra antes do piloto real (etapa 29). |
| 9 | Python 3.14 local vs. "3.11+" da spec: compatível, mas algumas libs de TTS (Kokoro/torch) podem não ter wheels para 3.14. | Aberta | Verificar na etapa 1; se preciso, criar o venv com 3.11/3.12. |
