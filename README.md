# video-pipeline

Pipeline local, retomável e auditável para produzir vídeos narrados em inglês ou pt-BR a partir de fontes
verificáveis e imagens com licença registrada. O piloto documental aborda expedições e desastres de
1880–1930; o formato explicativo também aceita vídeos verticais. Agendamento e publicação dependem de revisão
e autorização humanas.

- Contexto e regras: [CLAUDE.md](CLAUDE.md)
- Agentes Codex/OpenAI e skills do workspace: [AGENT.MD](AGENT.MD)
- Exploração estrutural com codebase-memory: [guia e configuração local](docs/opencode-codebase-memory-mcp.md)
- Análise da pipeline e do processo editorial: [docs/analise-pipeline-agentes.md](docs/analise-pipeline-agentes.md)
- Prompts locais e limites da validação: [docs/analise-prompts-locais.md](docs/analise-prompts-locais.md)
- Fluxo com radar, ambiente de voz e motion-kit: [docs/pipeline-hoje.mermaid](docs/pipeline-hoje.mermaid)
- Funcionamento atual e componentes pendentes: [docs/WORKSPACE-ATUAL-E-COMPONENTES.md](docs/WORKSPACE-ATUAL-E-COMPONENTES.md)
- Fluxo originalmente planejado: [docs/pipeline-flowchart.mermaid](docs/pipeline-flowchart.mermaid)
- Plano de entregas (31 etapas): [docs/ROADMAP.md](docs/ROADMAP.md)
- Questões abertas da análise inicial: [docs/ANALISE.md](docs/ANALISE.md)
- Arquitetura (portas e adaptadores): [docs/arquitetura.md](docs/arquitetura.md)
- Arquitetura atual em PlantUML: [fonte](docs/arquitetura-atual.puml) e [diagrama SVG](docs/arquitetura-atual.svg)
- Visão para apresentação, com a camada de IA destacada: [docs/arquitetura-ia.md](docs/arquitetura-ia.md)
- Evolução do fluxo por camadas, busca de evidências e atuação 2D: [docs/evolucao-por-camadas.md](docs/evolucao-por-camadas.md)
- Análise técnica com gaps e verificações: [docs/analise-gaps-tecnicos.md](docs/analise-gaps-tecnicos.md)
- Pesquisa sobre crescimento no YouTube, embalagem e testes: [afirmações e hipóteses](docs/pesquisa/crescimento-youtube-embalagem-hipoteses-2026-10-23.md)
- Decisões de arquitetura: [docs/decisions/](docs/decisions/)

**Fase atual:** validação do template explicativo e do processo editorial; piloto documental em pausa.
Custo zero de API. A CLI e os scripts ainda cobrem partes diferentes da produção.

**Direção de montagem:** evoluir primeiro o JSON e o template do auto-play, usando o
motion-kit já integrado. O fluxo atual é `scenes.json` → produção → `episode.json` →
props JSON → template React/motion-kit → render. O JSON expressa apenas os recursos
integrados, não qualquer composição React. Avaliar o `motion-video` na sequência,
sem migração agora. Decisão e limites: [ADR 033](docs/decisions/033-montagem-json-no-auto-play.md).

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

## Consumo dos agentes em SQLite

`vp usage` registra consumo por episódio, etapa e modelo e coordena reservas de orçamento
em `data/telemetry/usage.sqlite3`, fora do Git. Inicialização e consulta são offline:

```bash
.venv/bin/vp usage init
.venv/bin/vp usage --help
.venv/bin/vp usage report <id>
```

Importação de eventos e exemplos: [docs/usage.md](docs/usage.md). A coleta automática e o
bloqueio do lançamento de agentes ainda não estão conectados; o comando controla as reservas.

## Agendamento pelo Postiz

A CLI lê `POSTIZ_API_KEY` e `POSTIZ_API_URL` do `.env`, com precedência das variáveis do ambiente.
Os comandos retornam JSON para facilitar o uso por ferramentas e agentes:

```bash
.venv/bin/vp postiz integrations
.venv/bin/vp postiz connect instagram-standalone
.venv/bin/vp postiz posts --start 2026-10-15T00:00:00-03:00 --end 2026-10-20T00:00:00-03:00
.venv/bin/vp postiz upload renders/clipe/v3/reel-1-quem-sangra-e-refrao.mp4
.venv/bin/vp postiz schedule post.json
```

`schedule` cria agendamentos reais. Use após autorização do dono; o login do Instagram é feito por ele.
Configuração, formato do JSON e limites: [docs/postiz.md](docs/postiz.md).

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
