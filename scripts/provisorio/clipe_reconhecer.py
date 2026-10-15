"""Palavras com tempo de uma música pelo Whisper local, em janelas, no formato de janelas do clipe_tempos.py.

O codificador roda à parte e o `generate` recebe só a saída dele: pedir tempo por token direto faz o
transformers guardar as atenções de todas as camadas do codificador (uns 6 GB por janela no turbo), o que
derrubava o WSL.
Provisório. Rodar com teto de memória (sem ele, um estouro reinicia o WSL inteiro):
    systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=0 \
        uv run python scripts/provisorio/clipe_reconhecer.py ...

Uso: clipe_reconhecer.py musica.mp3 saida.json [modelo]; a saída entra em clipe_tempos.py.
"""

import json
import subprocess
import sys
import time

import numpy as np
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from transformers.modeling_outputs import BaseModelOutput

JANELA, PASSO = 30.0, 25.0
mp3, out = sys.argv[1], sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else "openai/whisper-large-v3-turbo"
torch.set_num_threads(4)
proc = WhisperProcessor.from_pretrained(name)
model = WhisperForConditionalGeneration.from_pretrained(name, dtype=torch.float32).eval()
dur = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
    capture_output=True, text=True, check=True,
).stdout)
eos = proc.tokenizer.eos_token_id
janelas = []
inicio = 0.0
while inicio < dur - 1:
    fim = min(dur, inicio + JANELA)
    t0 = time.time()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(inicio), "-to", str(fim), "-i", mp3, "-ac", "1",
                          "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32).copy()
    f = proc(audio, sampling_rate=16000, return_tensors="pt", return_attention_mask=True)
    with torch.inference_mode():
        enc = BaseModelOutput(last_hidden_state=model.model.encoder(f.input_features).last_hidden_state)
        res = model.generate(
            encoder_outputs=enc, attention_mask=f.attention_mask, language="pt", task="transcribe",
            max_new_tokens=220, return_token_timestamps=True, return_dict_in_generate=True,
        )
    pares = zip(res["sequences"][0], res["token_timestamps"][0], strict=False)
    tokens = [(proc.decode([int(s)]), float(x)) for s, x in pares if int(s) < eos]
    # Junta tokens em palavras: token que começa com espaço abre palavra nova; pontuação fica na palavra.
    palavras = []
    for texto, ts in tokens:
        if texto.startswith(" ") or not palavras:
            palavras.append({"w": texto.strip(), "ini": inicio + ts, "ultimo": inicio + ts})
        else:
            palavras[-1]["w"] += texto
            palavras[-1]["ultimo"] = inicio + ts
    for i, p in enumerate(palavras):
        prox = palavras[i + 1]["ini"] if i + 1 < len(palavras) else fim
        p["fim"] = round(min(prox, p.pop("ultimo") + 0.5), 2)
        p["ini"] = round(p["ini"], 2)
    palavras = [p for p in palavras if p["w"]]
    janelas.append({"janela": [inicio, fim], "palavras": palavras})
    print(f"janela {inicio:5.1f}-{fim:5.1f}: {len(palavras)} palavras em {time.time() - t0:.0f} s | "
          + " ".join(p["w"] for p in palavras), flush=True)
    inicio += PASSO
with open(out, "w") as fh:
    json.dump(janelas, fh, ensure_ascii=False, indent=1)
print(f"pronto -> {out}", flush=True)
