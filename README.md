# video-pipeline

Pipeline local, retomável e auditável para produzir vídeos narrados em inglês (5–7 min, 16:9) sobre
histórias reais — expedições e desastres de 1880–1930 — a partir de fontes verificáveis e imagens com
licença registrada. Publicação sempre manual, após revisão humana.

- Contexto e regras: [CLAUDE.md](CLAUDE.md)
- Fluxo: [docs/pipeline-flowchart.mermaid](docs/pipeline-flowchart.mermaid)
- Plano de entregas (31 etapas): [docs/ROADMAP.md](docs/ROADMAP.md)
- Questões abertas da análise inicial: [docs/ANALISE.md](docs/ANALISE.md)
- Decisões de arquitetura: [docs/decisions/](docs/decisions/)

**Fase atual:** piloto técnico (Fase 0 + primeiro episódio). Custo zero de API.

## Ambiente

Pré-requisitos: WSL2/Ubuntu, `ffmpeg`, `espeak-ng`, `git`, [`uv`](https://docs.astral.sh/uv/).
Decisões e motivos em [docs/decisions/004-ambiente-wsl.md](docs/decisions/004-ambiente-wsl.md).

```bash
# 1. .wslconfig no Windows (C:\Users\<usuário>\.wslconfig): memory=12GB, processors=12, swap=8GB
#    depois, no PowerShell: wsl --shutdown

# 2. Python 3.12 + Kokoro (PyTorch só-CPU)
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch
uv pip install --python .venv/bin/python kokoro soundfile

# 3. Ollama em ~/.local (sem sudo, sem CUDA) como serviço de usuário, e os modelos
#    ver ADR 004 para a extração e o serviço (OLLAMA_MAX_LOADED_MODELS=1); depois:
systemctl --user enable --now ollama
ollama pull qwen3.5:4b && ollama pull qwen3.5:9b

# 4. Configuração e verificação
cp .env.example .env
scripts/check_env.sh
```
