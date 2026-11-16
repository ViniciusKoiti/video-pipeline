"""Fila das imagens geradas pelo navegador: só a parte sem navegador (sem rede, sem Playwright)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "fila_imagens", Path(__file__).resolve().parents[1] / "scripts/provisorio/fila_imagens.py"
)
assert SPEC and SPEC.loader
fila = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fila  # o dataclass procura o módulo pelo nome
SPEC.loader.exec_module(fila)

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPG = b"\xff\xd8\xff\xe0" + b"1" * 32


def pedidos_em(tmp_path: Path, itens: list[dict]) -> Path:
    path = tmp_path / "pedidos.json"
    path.write_text(json.dumps(itens), encoding="utf-8")
    return path


def test_le_pedidos_e_resolve_referencia_pela_pasta_do_arquivo(tmp_path: Path) -> None:
    (tmp_path / "folha.png").write_bytes(PNG)
    path = pedidos_em(tmp_path, [{"id": "s01-loja", "prompt": " uma loja ", "refs": ["folha.png"]}])
    [pedido] = fila.ler_pedidos(path)
    assert (pedido.id, pedido.prompt, pedido.refs) == ("s01-loja", "uma loja", ((tmp_path / "folha.png"),))


@pytest.mark.parametrize(
    "itens",
    [
        [],
        [{"id": "S01 Loja", "prompt": "x"}],
        [{"id": "../fora", "prompt": "x"}],
        [{"id": "s01", "prompt": "  "}],
        [{"id": "s01", "prompt": "x"}, {"id": "s01", "prompt": "y"}],
        [{"id": "s01", "prompt": "x", "refs": ["nao-existe.png"]}],
    ],
)
def test_recusa_pedido_invalido(tmp_path: Path, itens: list[dict]) -> None:
    with pytest.raises(fila.FilaError):
        fila.ler_pedidos(pedidos_em(tmp_path, itens))


def test_guardar_grava_imagem_e_tira_o_pedido_dos_pendentes(tmp_path: Path) -> None:
    pedidos = fila.ler_pedidos(pedidos_em(tmp_path, [{"id": "a", "prompt": "x"}, {"id": "b", "prompt": "y"}]))
    saida = tmp_path / "saida"
    destino = fila.guardar(saida, pedidos[0], "gemini", JPG)
    assert destino.name == "a.jpg" and destino.read_bytes() == JPG
    assert not list(saida.glob("*.tmp"))
    assert [p.id for p in fila.pendentes(pedidos, saida)] == ["b"]
    [linha] = fila.ler_registro(saida)
    assert linha["estado"] == "gerada" and linha["site"] == "gemini" and linha["sha256"] == fila.sha256(JPG)


def test_nao_troca_imagem_pronta(tmp_path: Path) -> None:
    [pedido] = fila.ler_pedidos(pedidos_em(tmp_path, [{"id": "a", "prompt": "x"}]))
    fila.guardar(tmp_path / "saida", pedido, "gemini", PNG)
    with pytest.raises(fila.FilaError):
        fila.guardar(tmp_path / "saida", pedido, "gemini", JPG)
    assert (tmp_path / "saida/a.png").read_bytes() == PNG


def test_falha_arquivo_sumido_ou_alterado_continuam_pendentes(tmp_path: Path) -> None:
    pedidos = fila.ler_pedidos(
        pedidos_em(tmp_path, [{"id": i, "prompt": "x"} for i in ("falhou", "sumiu", "mudou")])
    )
    saida = tmp_path / "saida"
    fila.anotar_falha(saida, pedidos[0], "gemini", "sem imagem nova em 180 s")
    fila.guardar(saida, pedidos[1], "gemini", PNG).unlink()
    fila.guardar(saida, pedidos[2], "gemini", PNG).write_bytes(JPG)
    assert [p.id for p in fila.pendentes(pedidos, saida)] == ["falhou", "sumiu", "mudou"]


def test_recusa_o_que_nao_e_imagem(tmp_path: Path) -> None:
    [pedido] = fila.ler_pedidos(pedidos_em(tmp_path, [{"id": "a", "prompt": "x"}]))
    with pytest.raises(fila.FilaError):
        fila.guardar(tmp_path / "saida", pedido, "gemini", b"<html>entre na sua conta</html>")
    assert fila.pendentes([pedido], tmp_path / "saida") == [pedido]
