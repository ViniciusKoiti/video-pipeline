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
- Evidência do limite antigo (8 GB / 4 CPUs): `qwen3.5:4b` gerou JSON válido com structured outputs, mas a
  0,8 tok/s e 200 s de carga, com só 1,4 GB livres e 1,7 GB de swap em uso.

## Medições após o reinício (2026-09-25, 12 GB / 12 CPUs)

`scripts/check_env.sh` passa. Medições indicativas, com VS Code e outro projeto usando CPU ao mesmo tempo;
o benchmark formal (etapa 5) deve rodar com a máquina ociosa.

| Teste | Resultado |
|---|---|
| `qwen3.5:4b`, JSON com claims → trechos | correto; 4,1 tok/s gerando, 9,7 tok/s lendo o prompt |
| `qwen3.5:9b`, mesmo teste | correto; 2,5 tok/s gerando, 5,0 tok/s lendo o prompt |
| `qwen3.5:4b` por `num_thread` (4 / 6 / 8 / 12) | 1,7 / 2,7 / **3,7** / 0,7 tok/s |
| Kokoro por `torch.set_num_threads` (4 / 6 / 8 / 12) | RTF 1,73 / 1,44 / **1,32** / 1,36 |

Decisões derivadas:

- **8 threads** para LLM e TTS (núcleos físicos do 5700U). Passar `num_thread=8` nas chamadas ao Ollama e
  `torch.set_num_threads(8)` no adapter do Kokoro; 12 threads (com SMT) derruba o LLM.
- Serviço do Ollama com `OLLAMA_MAX_LOADED_MODELS=1` e `OLLAMA_NUM_PARALLEL=1`: dois modelos carregados
  ao mesmo tempo disputaram CPU e memória no teste.
- `qwen3:4b` (denso, 2,5 GB) também baixado como referência para o benchmark, para separar "máquina
  lenta" de "arquitetura híbrida do qwen3.5 lenta em CPU".
- Risco aberto para a etapa 5 e a ADR 003: a 2,5–4 tok/s gerando e 5–10 tok/s lendo, um roteiro com
  6–10 mil tokens de trechos-fonte pode levar de 20 a 40 min por chamada. Isso reforça a proposta do §13.2.
- Atualizar o Ollama: baixar o novo `ollama-linux-amd64.tar.zst`, extrair sem as pastas `cuda_v*` em
  `~/.local` e `systemctl --user restart ollama`.
- `scripts/check_env.sh` verifica tudo isso e sai com 1 se algo obrigatório faltar.
