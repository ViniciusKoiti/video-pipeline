"""Cliente do Chatterbox no Modal (ADR 024): o protocolo do `chatterbox_worker.py`, com a síntese na nuvem.

Uso: `<python com o pacote modal> chatterbox_modal_client.py <app> <modelo> <gravação no volume>`. Roda no
ambiente da CLI do Modal (`uv tool install modal`), que traz o pacote e o token do dono (`~/.modal.toml`); não
importa nada de `app`, e o auto-play não ganha dependência.

Lê um pedido JSON por linha (o do worker local), manda ao Modal as partes, o idioma, a pausa, a entrega e o
hash da gravação de referência da máquina, grava o WAV que volta em `out_path` e responde uma linha:
`{"ok": true, "seconds": 6.8}` ou `{"ok": false, "error": "..."}`. A primeira linha é `{"ready": true}`; o
contêiner da GPU só sobe no primeiro pedido.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TextIO

FORWARDED = ("parts", "language_id", "pause_ms", "exaggeration", "cfg_weight")


def answer(out: TextIO, payload: dict[str, Any]) -> None:
    out.write(json.dumps(payload, ensure_ascii=False) + "\n")
    out.flush()


Call = Callable[[dict[str, Any]], dict[str, Any]]


def handle(job: dict[str, Any], reference_name: str, call: Call) -> dict[str, Any]:
    """Um pedido: o que vai ao Modal e o que volta para o adapter. A gravação não vai no pedido, só o hash."""
    reference = Path(job["reference"])
    remote_job = {key: job[key] for key in FORWARDED if key in job}
    remote_job["reference_name"] = reference_name
    remote_job["reference_hash"] = hashlib.sha256(reference.read_bytes()).hexdigest()[:12]
    result = call(remote_job)
    if not result.get("ok"):
        return {"ok": False, "error": str(result.get("error") or "o Modal não devolveu áudio")}
    out_path = Path(job["out_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(result["wav"])
    return {"ok": True, "seconds": result.get("seconds")}


def serve(lines: Iterable[str], out: TextIO, reference_name: str, call: Call) -> None:
    answer(out, {"ready": True})
    for line in lines:
        if not line.strip():
            continue
        try:
            answer(out, handle(json.loads(line), reference_name, call))
        except Exception as error:  # o adapter decide; o cliente segue para o próximo pedido
            answer(out, {"ok": False, "error": f"{type(error).__name__}: {error}"})


def main() -> None:
    app_name, model_name, reference_name = sys.argv[1], sys.argv[2], sys.argv[3]
    # A pasta deste arquivo tem um `chatterbox.py` (o adapter): fora do caminho de importação.
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != here]
    out = os.fdopen(os.dup(1), "w", encoding="utf-8")
    os.dup2(2, 1)  # avisos do cliente do Modal vão para a saída de erro

    import modal

    remote = modal.Cls.from_name(app_name, "Chatterbox")(model_name=model_name)
    serve(sys.stdin, out, reference_name, remote.generate.remote)


if __name__ == "__main__":
    main()
