"""Voz clonada do dono numa GPU do Modal (ADR 024): o mesmo Chatterbox do `lab-voz`, por requisição.

Publicar (uma vez, e de novo quando este arquivo ou a lista de pacotes mudarem):

    modal deploy deploy/modal_chatterbox.py

A gravação de referência fica no volume privado `voz-dono-referencia` da conta do dono, enviada por ele
(`modal volume put`). O código do modelo é o mesmo commit do `lab-voz` (`chatterbox-requirements.txt`), com
a mesma geração do `app/providers/tts/chatterbox_worker.py`: partes separadas por `pause_ms` de silêncio e a
entrega da fala (`exaggeration`, `cfg_weight`, ADR 022). Cada pedido diz o hash da gravação esperada: se o
volume tiver outra, o pedido falha em vez de sair com outra voz.

Este arquivo roda no Modal (o pacote `modal` vem da CLI instalada com `uv tool install modal`) e não importa
nada de `app`.
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any

import modal

APP_NAME = "voz-dono"
REFERENCE_DIR = "/voz"
HF_HOME = "/cache/hf"

reference_volume = modal.Volume.from_name("voz-dono-referencia", create_if_missing=True)
weights_volume = modal.Volume.from_name("voz-dono-pesos", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1")
    .pip_install_from_requirements(str(Path(__file__).with_name("chatterbox-requirements.txt")))
    .env({"HF_HOME": HF_HOME})
)

app = modal.App(APP_NAME, image=image)


@app.cls(
    gpu="T4",
    volumes={REFERENCE_DIR: reference_volume, "/cache": weights_volume},
    scaledown_window=120,  # entre uma cena e a próxima o contêiner fica de pé; depois, nada é cobrado
    timeout=600,
)
class Chatterbox:
    model_name: str = modal.parameter(default="v3")

    @modal.enter()
    def load(self) -> None:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        self.model = ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model=self.model_name)
        weights_volume.commit()  # os pesos baixados na primeira vez ficam para os próximos contêineres

    @modal.method()
    def generate(self, job: dict[str, Any]) -> dict[str, Any]:
        import torch
        import torchaudio

        try:
            reference = Path(REFERENCE_DIR) / job["reference_name"]
            if not reference.is_file():
                return {"ok": False, "error": f"gravação {job['reference_name']!r} ausente no volume"}
            digest = hashlib.sha256(reference.read_bytes()).hexdigest()[:12]
            if digest != job["reference_hash"]:
                return {"ok": False, "error": f"a gravação do volume ({digest}) não é a da máquina "
                        f"({job['reference_hash']}): envie de novo com `modal volume put`"}
            sample_rate = self.model.sr
            silence = torch.zeros(1, round(sample_rate * job["pause_ms"] / 1000))
            chunks = []
            for i, part in enumerate(job["parts"]):
                if i:
                    chunks.append(silence)
                wav = self.model.generate(
                    part,
                    language_id=job["language_id"],
                    audio_prompt_path=str(reference),
                    exaggeration=float(job.get("exaggeration", 0.5)),
                    cfg_weight=float(job.get("cfg_weight", 0.5)),
                )
                chunks.append(wav.detach().cpu())
            audio = torch.cat(chunks, dim=-1)
            buffer = io.BytesIO()
            torchaudio.save(buffer, audio, sample_rate, format="wav", encoding="PCM_S", bits_per_sample=16)
            return {"ok": True, "seconds": audio.shape[-1] / sample_rate, "wav": buffer.getvalue()}
        except Exception as error:  # o cliente relata ao adapter; o contêiner segue para o próximo pedido
            return {"ok": False, "error": f"{type(error).__name__}: {error}"}
