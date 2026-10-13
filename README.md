# video-pipeline

Pipeline local, retomável e auditável para produzir vídeos narrados em inglês ou pt-BR a partir de fontes
verificáveis e imagens com licença registrada. O piloto documental aborda expedições e desastres de
1880–1930; o formato explicativo também aceita vídeos verticais. Publicação sempre manual, após revisão humana.

- Contexto e regras: [CLAUDE.md](CLAUDE.md)
- Agentes Codex/OpenAI e skills do workspace: [AGENT.MD](AGENT.MD)
- Análise da pipeline e do processo editorial: [docs/analise-pipeline-agentes.md](docs/analise-pipeline-agentes.md)
- Prompts locais e limites da validação: [docs/analise-prompts-locais.md](docs/analise-prompts-locais.md)
- Fluxo com radar, ambiente de voz e motion-kit: [docs/pipeline-hoje.mermaid](docs/pipeline-hoje.mermaid)
- Funcionamento atual e componentes pendentes: [docs/WORKSPACE-ATUAL-E-COMPONENTES.md](docs/WORKSPACE-ATUAL-E-COMPONENTES.md)
- Fluxo originalmente planejado: [docs/pipeline-flowchart.mermaid](docs/pipeline-flowchart.mermaid)
- Plano de entregas (31 etapas): [docs/ROADMAP.md](docs/ROADMAP.md)
- Questões abertas da análise inicial: [docs/ANALISE.md](docs/ANALISE.md)
- Arquitetura (portas e adaptadores): [docs/arquitetura.md](docs/arquitetura.md)
- Decisões de arquitetura: [docs/decisions/](docs/decisions/)

**Fase atual:** validação do template explicativo e do processo editorial; piloto documental em pausa.
Custo zero de API. A CLI e os scripts ainda cobrem partes diferentes da produção.

## Ambiente

Pré-requisitos: WSL2/Ubuntu, `ffmpeg`, `espeak-ng`, `git`, [`uv`](https://docs.astral.sh/uv/).
Decisões e motivos em [docs/decisions/004-ambiente-wsl.md](docs/decisions/004-ambiente-wsl.md).

```bash
# 1. .wslconfig no Windows (C:\Users\<usuário>\.wslconfig): memory=12GB, processors=12, swap=8GB
#    depois, no PowerShell: wsl --shutdown

# 2. Python 3.12 + dependências do uv.lock (o extra tts traz Kokoro e PyTorch só-CPU)
uv python install 3.12
uv sync --extra tts        # sem --extra tts: só o necessário para CLI e testes

# 3. Ollama em ~/.local (sem sudo, sem CUDA) como serviço de usuário, e os modelos
#    ver ADR 004 para a extração e o serviço (OLLAMA_MAX_LOADED_MODELS=1); depois:
systemctl --user enable --now ollama
ollama pull qwen3.5:4b && ollama pull qwen3.5:9b

# 3b. Só para o formato explicativo (Remotion + motion-kit, Node.js LTS)
(cd video && npm ci && npx remotion browser ensure)

# 4. Configuração e verificação
cp .env.example .env
scripts/check_env.sh
```

## Uso

```bash
uv run vp --help           # comandos do CLAUDE.md §10; os ainda não implementados indicam a etapa
uv run vp bench --models qwen3.5:4b,qwen3.5:9b --runs 2   # rodar com a máquina ociosa
uv run pytest && uv run ruff check .
uv run pytest -m slow      # contratos com modelos locais pesados (Kokoro)
```

## Uso com agentes Codex/OpenAI

As cinco skills locais estão em [.agents/skills/](.agents/skills/). `AGENTS.md` carrega as instruções de
[AGENT.MD](AGENT.MD). Use as invocações abaixo como mensagens ao agente dentro deste workspace:

```text
$vp-pauta Prepare a pauta do episódio <id> com o radar disponível. Quero explicar <pergunta> para <público>.
$vp-fichamento Fiche as fontes já baixadas do episódio <id> e registre as lacunas para essa pergunta.
$vp-roteiro Escreva o roteiro do episódio <id> usando as fichas aprovadas e o objetivo definido na pauta.
$vp-checagem Revise o episódio <id>, confira a promessa e as evidências e entregue um relatório sem editar os dados.
$vp-engajamento Analise o episódio <id> com as métricas fornecidas e proponha o próximo teste de tema ou abertura.
```

Sequência: pauta decidida pelo dono → fichamento → gate 1 → roteiro → checagem independente → gate 2 → produção.
Um episódio já aprovado recebe proposta de alteração separada. As skills não aprovam gates nem publicam vídeos.
Sem métricas próprias, a análise de engajamento produz hipóteses. Detalhes e limites estão em `AGENT.MD`.
