"""Fila e registro das imagens geradas pelo navegador (parte sem navegador de `imagens_navegador.py`).

pedidos.json: lista de {"id": "s03-patio", "prompt": "...", "refs": ["folha-do-boneco.png"]}. `refs` opcional;
os caminhos relativos valem a partir da pasta do pedidos.json. O `id` vira o nome do arquivo.

Cada tentativa vira uma linha em `<saida>/registro.jsonl`, só acrescentada: estado `gerada` (com arquivo e
sha256) ou `falhou` (com o motivo). Um pedido está pronto quando tem linha `gerada` e o arquivo existe com o
mesmo sha256; rodar de novo só faz o que falta. Nada aqui registra ativo no episódio: as imagens ficam em
`needs_review` fora do pipeline até o dono escolher (gate 3).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.errors import PipelineError

ID_VALIDO = re.compile(r"^[a-z0-9][a-z0-9\-]{0,79}$")
REGISTRO = "registro.jsonl"
ASSINATURAS = ((b"\x89PNG", ".png"), (b"\xff\xd8\xff", ".jpg"), (b"RIFF", ".webp"))


class FilaError(PipelineError, ValueError):
    pass


@dataclass(frozen=True)
class Pedido:
    id: str
    prompt: str
    refs: tuple[Path, ...] = ()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extensao(data: bytes) -> str:
    """Extensão pelo começo do arquivo; o que não é PNG, JPEG ou WebP não é imagem aceita."""
    for inicio, ext in ASSINATURAS:
        if data.startswith(inicio):
            return ext
    raise FilaError("o que o site devolveu não é PNG, JPEG nem WebP")


def ler_pedidos(path: Path) -> list[Pedido]:
    if not path.is_file():
        raise FilaError(f"{path} não existe")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise FilaError(f"{path} precisa ser uma lista de pedidos, não vazia")
    pedidos: list[Pedido] = []
    vistos: set[str] = set()
    for i, item in enumerate(raw):
        ident, prompt = str(item.get("id", "")), str(item.get("prompt", "")).strip()
        if not ID_VALIDO.match(ident):
            raise FilaError(f"pedido {i}: id {ident!r} inválido (minúsculas, números e hífen)")
        if ident in vistos:
            raise FilaError(f"pedido {i}: id {ident!r} repetido")
        if not prompt:
            raise FilaError(f"pedido {ident}: prompt vazio")
        refs = tuple((path.parent / r).resolve() for r in item.get("refs", []))
        for ref in refs:
            if not ref.is_file():
                raise FilaError(f"pedido {ident}: referência {ref} não existe")
        vistos.add(ident)
        pedidos.append(Pedido(ident, prompt, refs))
    return pedidos


def ler_registro(saida: Path) -> list[dict]:
    path = saida / REGISTRO
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def prontos(saida: Path) -> set[str]:
    """Ids com imagem gerada, arquivo presente e sha256 igual ao registrado."""
    feitos: set[str] = set()
    for linha in ler_registro(saida):
        if linha.get("estado") != "gerada":
            continue
        arquivo = saida / linha["arquivo"]
        if arquivo.is_file() and sha256(arquivo.read_bytes()) == linha["sha256"]:
            feitos.add(linha["id"])
    return feitos


def pendentes(pedidos: list[Pedido], saida: Path) -> list[Pedido]:
    feitos = prontos(saida)
    return [p for p in pedidos if p.id not in feitos]


def _anotar(saida: Path, linha: dict) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    linha = {**linha, "data": datetime.now().astimezone().isoformat(timespec="seconds")}
    with (saida / REGISTRO).open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def guardar(saida: Path, pedido: Pedido, site: str, data: bytes) -> Path:
    """Grava a imagem inteira (temporário + rename) e a linha `gerada`. Não troca imagem já pronta."""
    if pedido.id in prontos(saida):
        raise FilaError(f"pedido {pedido.id} já tem imagem pronta; apague a linha do registro para refazer")
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"{pedido.id}{extensao(data)}"
    tmp = destino.with_suffix(destino.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.rename(destino)
    _anotar(saida, {
        "id": pedido.id, "estado": "gerada", "site": site, "arquivo": destino.name, "sha256": sha256(data),
        "prompt": pedido.prompt, "refs": [str(r) for r in pedido.refs],
    })
    return destino


def anotar_falha(saida: Path, pedido: Pedido, site: str, motivo: str) -> None:
    _anotar(saida, {"id": pedido.id, "estado": "falhou", "site": site, "motivo": motivo})
