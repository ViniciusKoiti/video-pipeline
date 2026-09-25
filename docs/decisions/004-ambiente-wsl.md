# 004 — Ambiente local: .wslconfig, Python 3.12 e Ollama de usuário

- **Status:** aceito
- **Data:** 2026-09-25
- **Etapa do roadmap:** #1

## Contexto

O pipeline roda Ollama, Kokoro e ffmpeg na mesma máquina, sem GPU dedicada (AMD Ryzen 7 5700U, Radeon
integrada; host com 19,4 GB de RAM e 16 threads). O `.wslconfig` existente limitava o WSL a 8 GB e 4 CPUs.
Havia ainda três restrições descobertas na instalação:

- `kokoro` 0.9.4 e `misaki` 0.9.4 declaram `requires-python <3.13`; o Python do sistema é 3.14.
- `sudo` pede senha, então o script oficial de instalação do Ollama não roda sem intervenção.
- O pacote Linux do Ollama traz 2,1 GB de bibliotecas CUDA, inúteis sem GPU NVIDIA.

## Decisão

1. `.wslconfig` em `C:\Users\Usuario\.wslconfig`: `memory=12GB`, `processors=12`, `swap=8GB`
   (backup da versão anterior em `.wslconfig.bak-2026-09-25`). O Windows fica com ~7 GB e 4 threads.
2. `.venv` com Python 3.12 gerenciado pelo `uv` (`uv python install 3.12`), sem tocar no Python do sistema.
3. PyTorch pelo índice só-CPU (`download.pytorch.org/whl/cpu`) para evitar gigabytes de CUDA.
4. Ollama 0.34.4 instalado em `~/.local` (binário + bibliotecas CPU/Vulkan, sem `cuda_v12`/`cuda_v13`),
   rodando como serviço `systemctl --user` (`~/.config/systemd/user/ollama.service`), ouvindo só em
   `127.0.0.1:11434`.
5. Modelos de texto baixados para o benchmark: `qwen3.5:4b` e `qwen3.5:9b`. `qwen3.5:9b` é o padrão
   provisório em `.env.example` até a etapa 5.

## Consequências

- Mudança no `.wslconfig` só vale após `wsl --shutdown` no Windows.
- O `pyproject.toml` (etapa 2) precisa fixar `requires-python = ">=3.11,<3.13"` e declarar o modelo spaCy
  `en_core_web_sm`, que o `misaki` baixa sozinho na primeira execução se estiver ausente.
- `espeak-ng` (GPL-3) é usado como programa do sistema pelo `misaki` para palavras fora do vocabulário;
  uso local, sem distribuição do pipeline.
- Primeira medição do Kokoro com 4 CPUs: 9,7 s de áudio em 14,6 s (RTF 1,5, incluindo aquecimento).
  O benchmark formal é a etapa 5.
- Atualizar o Ollama: baixar o novo `ollama-linux-amd64.tar.zst`, extrair sem as pastas `cuda_v*` em
  `~/.local` e `systemctl --user restart ollama`.
- `scripts/check_env.sh` verifica tudo isso e sai com 1 se algo obrigatório faltar.
