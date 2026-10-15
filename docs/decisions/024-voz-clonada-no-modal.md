# 024 — Voz clonada numa GPU do Modal, com a gravação num volume privado

- **Status:** aceito pelo dono em 2026-10-14 ("pode", na sessão, depois de ver as opções de nuvem)
- **Data:** 2026-10-14
- **Etapa do roadmap:** voz (#16), voz final dos Reels
- **Relaciona-se com:** ADR 016 (voz clonada do dono; emendada aqui), ADR 022 (entrega da fala por cena),
  ADR 004 (recursos da máquina)

## Contexto

A voz final dos Reels é o Chatterbox Multilingual com a gravação do dono (ADR 016), rodando em CPU no notebook
(Ryzen 7 5700U, WSL com 12 processadores, sem GPU NVIDIA). Em 2026-10-14 cada cena de 6 a 7 s levou cerca de
15 minutos, e os dois primeiros reels ocuparam a máquina por horas. A ADR 016 e o CLAUDE.md do workspace diziam
que a gravação de referência nunca sai da máquina; com isso, a única GPU possível era uma GPU local.

Opções vistas: o Modal (função própria numa GPU, crédito gratuito mensal), a API pronta da DeepInfra (paga por
caractere, sem controle da versão nem da entrega) e o Space público do Hugging Face (cota, fila, infraestrutura
compartilhada).

## Decisão

1. **A gravação de referência pode ficar num volume privado da conta do dono no Modal**
   (`voz-dono-referencia`). Só ali: continua fora do Git, de provedores de TTS prontos e de qualquer outro
   serviço. Quem envia é o dono (`modal volume put`); o agente não sobe a gravação.
2. **A função na nuvem é o mesmo Chatterbox do `lab-voz`** (`deploy/modal_chatterbox.py`, GPU T4): o mesmo
   commit e as mesmas versões de pacote (`deploy/chatterbox-requirements.txt`, tirado do ambiente local, sem as
   ferramentas de desenvolvimento), a mesma geração por partes com `pause_ms` e a mesma entrega da fala
   (`exaggeration`, `cfg_weight`). Cada pedido leva o hash da gravação da máquina; se o volume tiver outra, o
   pedido falha em vez de sair com outra voz.
3. **No auto-play é a voz `chatterbox_modal`**: o mesmo adapter do Chatterbox, com outro processo — um cliente
   (`app/providers/tts/chatterbox_modal_client.py`) com o protocolo do worker local, que roda no ambiente da CLI
   do Modal (`uv tool install modal`) e usa o token dela (`~/.modal.toml`). O auto-play não ganha dependência
   nem chave no `.env`. O nome dos WAVs separa as duas vozes (`S01-chatterbox_modal-<hash>.wav`), e o cache de
   uma não reaproveita a outra.
4. **Custo:** a conta usa o crédito gratuito mensal do Modal, com limite de gasto definido pelo dono no painel.
   O adapter declara custo zero por chamada, como a Groq e o Gemini na camada gratuita.
5. **A voz local continua.** `tts_final` segue `chatterbox` até o dono comparar a mesma cena gerada nos dois
   lugares; trocar para `chatterbox_modal` é uma linha no `providers.toml`.

## Consequências

- Uma cena passa de cerca de 15 minutos para segundos, mais 1 a 2 minutos para o contêiner subir na primeira
  chamada do dia (estimativa; medir na primeira rodada).
- Publicar a função de novo (`modal deploy`) quando `deploy/modal_chatterbox.py` ou a lista de pacotes mudarem.
- Trocar a gravação de referência pede enviar a nova ao volume; o hash protege contra a mistura.
- A regra do `lab-voz` no CLAUDE.md do workspace passa a ter essa exceção, e só ela.
