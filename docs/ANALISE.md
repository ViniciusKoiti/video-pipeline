# Análise inicial do repositório (2026-09-24)

Questões encontradas ao organizar o projeto a partir do `CLAUDE.md`, e o que foi feito com cada uma.

| # | Questão | Situação | Ação |
|---|---|---|---|
| 1 | Arquivo se chamava `CLAUDE.MD`; o Claude Code procura `CLAUDE.md` e o Linux diferencia maiúsculas. | Resolvida | Renomeado para `CLAUDE.md`. |
| 2 | §3 dizia que o projeto vive em `~/video-pipeline`; ele está em `~/projetos/auto-play` (também no FS Linux, fora de `/mnt/c`). | Resolvida | Texto do §3 atualizado; repositório no GitHub chama-se `video-pipeline`. |
| 3 | `docs/spec-v0.4.md` é a "fonte de verdade", mas não existia. | **Aberta** | Placeholder criado. O dono do projeto precisa colar a spec original. |
| 4 | `mermaid.txt` estava vazio; o §4 aponta `docs/pipeline-flowchart.mermaid`. | Resolvida | Diagrama extraído do §4 para `docs/pipeline-flowchart.mermaid`; `mermaid.txt` removido. |
| 5 | `app/pipeline/schemas.py` e `tests/fixtures/episodes/pilot-example/` são citados no §14 mas não existem. | Resolvida | Etapa 3; decisões na ADR 007. |
| 6 | Ambiente: Python 3.14 e ffmpeg presentes; **Ollama e Kokoro não instalados**; `.wslconfig` limitava o WSL a 8 GB / 4 CPUs. | Resolvida | Etapa 1: Ollama de usuário, Kokoro no `.venv`, `.wslconfig` 12 GB / 12 CPUs; ADR 004. |
| 7 | Conflito §7 × §13.2: provedor de texto padrão é Ollama na spec, mas o §13 propõe Gemini/Groq gratuito. Cinco decisões do §13 não têm ADR. | Aberta | ADRs 001–005 mapeados em `docs/decisions/000-template.md`; etapas 1, 9, 20, 26, 29. |
| 8 | A ordem do §11 (A→G) coloca pesquisa e roteiro (F) depois de render e ativos. Um episódio real precisa de F antes de D/E. | Aceita | O roadmap mantém a ordem da spec para o piloto técnico: um roteiro de teste fixo (etapa 6) alimenta as etapas B–E; F entra antes do piloto real (etapa 30). |
| 9 | Python 3.14 local vs. "3.11+" da spec: `kokoro`/`misaki` 0.9.4 exigem `<3.13`. | Resolvida | `.venv` com Python 3.12 via `uv`; `pyproject` da etapa 2 fixa `<3.13`. |
| 10 | O §7 e o §14 pedem um `Protocol` por função, mas nenhuma etapa definia essas interfaces antes dos adapters, e o experimento de motor não tinha um contrato comum. | Resolvida | Etapa 4 (arquitetura: portas e adaptadores) inserida antes dos protótipos de motor e dos adapters; ADR 006. |
| 11 | O `misaki` instala o modelo spaCy `en_core_web_sm` pela rede na primeira execução, fora do controle do projeto. | Resolvida | Etapa 2: `en_core_web_sm==3.8.0` fixado por URL no extra `tts` do `pyproject.toml`. |
| 12 | LLM local lento nesta máquina. Medido na etapa 5 com a máquina ociosa: 3–5 tok/s gerando e 16–30 tok/s lendo; um roteiro real deve levar ~11–19 min por chamada (não 20–40). | Parcialmente resolvida | Velocidade medida (`data/benchmarks/README.md`). Falta a fidelidade por leitura humana e a comparação com remotos: etapa 29 (ADR 003, §13.2). |
| 13 | O Ollama usa contexto de 4096 tokens por padrão; um roteiro com 6–10 mil tokens de trechos seria cortado sem aviso, e contexto maior aumenta a memória. | Aberta | Etapa 27: definir `num_ctx` pelo tamanho do prompt, medir a memória e falhar (`InvalidOutput`) se o prompt não couber. |
| 14 | `loc.gov` e `cdn.loc.gov` respondem 403 (desafio do Cloudflare) a requisições automatizadas; a API JSON da Library of Congress não é utilizável daqui. | Aberta | Etapa 20: o Commons espelha boa parte do acervo (LC-USZ62, Lot-4262, com metadados); avaliar a API oficial da LoC com limites e identificação adequados antes de manter a LoC como provedor próprio. |
| 15 | Com jogo aberto no Windows (MTGA) e contêineres de outro projeto, o Ryzen 5700U (15 W, GPU integrada no mesmo orçamento) caiu para ~25% de desempenho: um laço Python levou 26,6 s em vez de ~1,5 s. A média de carga não mostra isso. | Mitigada | `vp bench` mede uma sonda de CPU e avisa; benchmarks só valem sem apps pesados. Plano de energia "Equilibrado" também limita o turbo. |
| 16 | Um runner do GitHub Actions do `markagenda` roda jobs nesta máquina (load 3–7 durante builds) e distorce benchmarks sem aviso prévio. | Mitigada | Comparações entre motores rodadas em sequência, nas mesmas condições; números absolutos só com o runner parado. |

## Revisão de 2026-09-29

Estado depois da ADR 011 e do episódio de teste `votorantim-dinheiro`. As pendências em ordem estão no "Etapa
atual" do `CLAUDE.md`; a situação por issue, no `ROADMAP.md`. O item 3 (spec v0.4 ausente) continua aberto.

| # | Questão | Situação | Ação |
|---|---|---|---|
| 17 | Nenhum vídeo publicado. Os cinco episódios em `data/episodes/` são da mesma empresa, e a maior incógnita do projeto é a audiência (§12), que o pipeline não responde. | Aberta | Levar o `votorantim-completo` (gates 1 e 2 aprovados) até o gate 4 e a publicação manual. |
| 18 | O §1 ainda dá como recorte da validação as expedições de 1880–1930 em inglês; desde 2026-09-26 todo o trabalho é o explicativo em pt-BR. O §12 pede 4 vídeos no mesmo recorte. | Aberta, decisão do dono | Registrar o recorte numa ADR quando decidido. |
| 19 | O roteiro do `votorantim-completo` é anterior à ADR 011: nenhum tipo novo, carimbos em 32 de 128 planos (limite de alerta: 10%), 7 planos com "Fonte:" no texto (duplica o rodapé) e até 18 planos gráficos seguidos sem imagem (S27–S34). `vp check`: sem erros, com alertas. | Aberta, decisão do dono | Sair como está ou reescrever com os planos novos (reabre o gate 2 e cumpre os critérios das #73 e #76–#79). |
| 20 | Custo da checagem: no `votorantim-dinheiro` (93 s, 10 cenas), os agentes informaram ~1,6 milhão de tokens e ~1 h 31 min; só a checagem, ~944 mil em 5 rodadas. Ela achou erros reais. Um episódio de 5–7 min tem de 4 a 5 vezes mais cenas, e o limite do plano do Claude pode virar o gargalo de 4 vídeos em 4–6 semanas. | Aberta | Mandar ao verificador só as cenas que mudaram e juntar correções pequenas numa rodada (lição registrada em `data/benchmarks/episodio-votorantim-dinheiro.md`); medir o próximo episódio inteiro. |
| 21 | Horas humanas por episódio não medidas, embora o §11 peça. É o número que decide se o formato é viável. | Aberta | Anotar no próximo episódio, por gate. |
| 22 | Imagens de história empresarial brasileira: no `votorantim-dinheiro`, 5 de 10 planos de imagem ficaram sem ativo (nada no Commons); a Brasiliana Fotográfica recusou o acesso automatizado (403), como a LoC no item 14. | Aberta | Buscar as imagens antes do roteiro, ou escolher recortes com acervo; Brasiliana e Arquivo Nacional à mão. |
| 23 | Nenhum código gera `captions.srt`, `credits.txt` nem `description.txt`; o script provisório faz só voz e render. | Aberta | #17 e #18, ou scripts provisórios, antes do gate 4. |
| 24 | Perfil crítico de família e empresa ativas, com fatos de fonte única, de fonte interessada ou de biógrafo em comum (`votorantim-completo/lacunas.md`, seção 0). O `revisor-de-risco` do §15 ainda é candidato. | Aberta | Criar o agente antes do gate 4 do primeiro episódio publicado. |
| 25 | A ADR 010 (busca por vetor) é citada no `CLAUDE.md`, mas não existe em `docs/decisions/`. | Aberta | `CLAUDE.md` passou a dizer "ainda sem arquivo"; escrever quando a busca for necessária. |
| 26 | Issues desatualizadas: #70–#80 abertas sem marcação, embora os PRs #85–#87 tenham entregue as peças; o checklist da #69 sem marcação; a #75 com os critérios cumpridos; a #43 só com o bench limpo pendente. | Aberta | Situação por issue no `ROADMAP.md`; fechar a #75 e marcar a #69 no GitHub. |
| 27 | `mermaid.txt` voltou à raiz, fora do Git, com uma versão antiga do diagrama (sem fichas, agentes nem bancos de imagem). O atual é `docs/pipeline-flowchart.mermaid` (item 4). | Aberta | Apagar, se o dono não usa a cópia. |
