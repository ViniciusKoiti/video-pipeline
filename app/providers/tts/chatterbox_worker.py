"""Processo do Chatterbox (ADR 016). Roda no ambiente próprio do modelo, nunca no deste projeto.

Uso: `<python do ambiente do Chatterbox> chatterbox_worker.py <modelo> <threads>`. Não importa nada de `app`.

Carrega o modelo uma vez e atende um pedido por linha da entrada padrão, em JSON:
`{"parts": ["..."], "language_id": "pt", "reference": "voz.wav", "out_path": "S01.wav", "pause_ms": 400,
"exaggeration": 0.5, "cfg_weight": 0.5}`; os dois últimos são a entrega da fala (ADR 022) e, sem eles,
vale o padrão do modelo.
Cada parte é uma síntese; entre duas partes entra `pause_ms` de silêncio (as `<short pause>` da ADR 015).
Responde uma linha por pedido: `{"ok": true, "seconds": 6.8}` ou `{"ok": false, "error": "..."}`. A primeira
linha, depois de carregar o modelo, é `{"ready": true, "sample_rate": 24000}`.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def answer(out: Any, payload: dict[str, Any]) -> None:
    out.write(json.dumps(payload, ensure_ascii=False) + "\n")
    out.flush()


def main() -> None:
    model_name, threads = sys.argv[1], int(sys.argv[2])
    # A pasta deste arquivo entra no caminho de importação e tem um `chatterbox.py` (o adapter), que
    # esconderia o pacote do modelo.
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != here]
    # As bibliotecas escrevem avisos e barras de progresso na saída padrão: ela vira a de erro, e as
    # respostas saem por uma cópia guardada antes.
    out = os.fdopen(os.dup(1), "w", encoding="utf-8")
    os.dup2(2, 1)

    import torch
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    torch.set_num_threads(threads)
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu", t3_model=model_name)
    answer(out, {"ready": True, "sample_rate": model.sr})

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            job = json.loads(line)
            silence = torch.zeros(1, round(model.sr * job["pause_ms"] / 1000))
            chunks = []
            for i, part in enumerate(job["parts"]):
                if i:
                    chunks.append(silence)
                chunks.append(
                    model.generate(
                        part,
                        language_id=job["language_id"],
                        audio_prompt_path=job["reference"],
                        exaggeration=float(job.get("exaggeration", 0.5)),
                        cfg_weight=float(job.get("cfg_weight", 0.5)),
                    )
                )
            audio = torch.cat(chunks, dim=-1)
            torchaudio.save(job["out_path"], audio, model.sr, encoding="PCM_S", bits_per_sample=16)
            answer(out, {"ok": True, "seconds": audio.shape[-1] / model.sr})
        except Exception as error:  # o adapter decide o que fazer; o processo segue para o próximo pedido
            answer(out, {"ok": False, "error": f"{type(error).__name__}: {error}"})


if __name__ == "__main__":
    main()
