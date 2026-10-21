"""Testes do `narrativa.py` da skill `analise-de-formato` (contagem sobre batidas marcadas por agente)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]

BATIDAS = """# assunto: voce
# tese: a gente guarda objeto velho por medo de perder quem era
# mensagem: você também faz isso
00:00\tCASO\t0\t\tas caixas no corredor
01:00\tPROMESSA\t0\t\tpor que é difícil jogar fora
01:00\tCONFISSAO\t0\t\ta gaveta de cabos
01:30\tGANCHO-PLANTA\t0\tg1\to bilhete
02:00\tCAPITULO\t1\t\to navio
02:00\tCASO\t1\t\to navio que troca as tábuas
03:30\tCONCEITO\t1\t\tidentidade
04:30\tAPLICA\t1\t\ta gaveta como se fosse a gente
05:00\tCAPITULO\t2\t\to psicólogo
05:00\tCONCEITO\t2\t\to apego medido
06:00\tPERGUNTA\t2\t\to que sobra de você?
08:00\tGANCHO-PAGA\t2\tg1\to bilhete lido
08:00\tFECHO-CONTRA-SI\t2\t\tele não jogou a gaveta fora
10:00\tFIM\t2\t\t
"""


def narrativa() -> Any:
    path = ROOT / ".agents" / "skills" / "analise-de-formato" / "narrativa.py"
    spec = importlib.util.spec_from_file_location("narrativa_skill", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def escrever(tmp_path: Path, nome: str, texto: str) -> Path:
    caminho = tmp_path / f"{nome}.batidas.tsv"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def test_segundos_aceita_minuto_hora_e_srt() -> None:
    mod = narrativa()
    assert mod.segundos("03:12") == 192
    assert mod.segundos("1:02:03") == 3723
    assert mod.segundos("00:12:46,097") == pytest.approx(766.097)


def test_medidas_contam_o_que_o_agente_marcou(tmp_path: Path) -> None:
    mod = narrativa()
    linha = mod.medidas(mod.ler_batidas(escrever(tmp_path, "X", BATIDAS)))
    assert linha["video_id"] == "X"
    assert linha["assunto"] == "voce"
    assert linha["duracao_min"] == 10.0
    assert linha["abertura_s"] == 120
    assert linha["blocos"] == 2
    # caso de 0:00–1:00 e 2:00–3:30; batida de ponto não interrompe a batida longa
    assert linha["pct_caso"] == pytest.approx(25.0)
    assert linha["pct_voce"] == pytest.approx(5.0 + 20.0)  # aplica 4:30–5:00, pergunta 6:00–8:00
    # bloco 1: 90 s de caso antes do conceito; bloco 2: conceito primeiro (0 s); mediana 45
    assert linha["caso_antes_conceito_s"] == 45
    assert linha["blocos_conceito_primeiro"] == 1
    assert linha["primeiro_voce_s"] == 270
    assert linha["confissoes"] == 1
    assert linha["posicao_confissoes_pct"] == "10"
    assert (linha["ganchos_plantados"], linha["ganchos_pagos"], linha["gancho_distancia_min"]) == (1, 1, 6.5)
    assert (linha["fecho_volta"], linha["fecho_contra_si"], linha["chamadas"]) == (0, 1, 0)


def test_tipo_desconhecido_e_falta_de_fim_param(tmp_path: Path) -> None:
    mod = narrativa()
    with pytest.raises(ValueError, match="tipo desconhecido"):
        mod.ler_batidas(escrever(tmp_path, "A", "00:00\tHISTORIA\t0\t\tx\n01:00\tFIM\t0\t\t\n"))
    with pytest.raises(ValueError, match="FIM"):
        mod.ler_batidas(escrever(tmp_path, "B", "00:00\tCASO\t0\t\tx\n"))
    with pytest.raises(ValueError, match="assunto"):
        mod.ler_batidas(escrever(tmp_path, "C", "# assunto: anime\n00:00\tCASO\t0\t\tx\n01:00\tFIM\t0\t\t\n"))


def test_comparar_marcacoes(tmp_path: Path) -> None:
    mod = narrativa()
    a = mod.ler_batidas(escrever(tmp_path, "a", BATIDAS))
    igual = mod.comparar(a, a)
    assert igual["concordancia_pct"] == 100.0
    outra = BATIDAS.replace("00:00\tCASO\t0", "00:00\tCONCEITO\t0")
    diferente = mod.comparar(a, mod.ler_batidas(escrever(tmp_path, "b", outra)))
    assert diferente["concordancia_pct"] == pytest.approx(90.0)
    assert diferente["trocas"][0] == (("CASO", "CONCEITO"), 60)
    assert diferente["pontos"]["CAPITULO"] == (2, 2, 2)


def test_candidatos_leem_txt_e_srt(tmp_path: Path) -> None:
    mod = narrativa()
    txt = tmp_path / "v.txt"
    txt.write_text("[00:10] e aí eu vou admitir uma coisa\n[00:12] guarda esse nome\n", encoding="utf-8")
    tipos = {(inicio, tipo) for inicio, tipo, _ in mod.candidatos(mod.ler_transcricao(txt))}
    assert (10, "CONFISSAO") in tipos
    assert (12, "GANCHO") in tipos
    srt = tmp_path / "v.srt"
    srt.write_text("1\n00:01:05,500 --> 00:01:08,000\nSegue o canal e\ncompartilha\n", encoding="utf-8")
    assert mod.ler_transcricao(srt) == [(65.5, "Segue o canal e compartilha")]
    assert [t for _, t, _ in mod.candidatos(mod.ler_transcricao(srt))] == ["CHAMADA"]


def test_medir_grava_csv_e_md(tmp_path: Path) -> None:
    mod = narrativa()
    escrever(tmp_path, "X", BATIDAS)
    amostra = tmp_path / "amostra.tsv"
    amostra.write_text("video_id\tgrupo\nX\tFILO\n", encoding="utf-8")
    assert mod.main(["medir", str(tmp_path), "--amostra", str(amostra)]) == 0
    assert "FILO" in (tmp_path / "narrativa.md").read_text(encoding="utf-8")
    assert (tmp_path / "narrativa.csv").read_text(encoding="utf-8").startswith("video_id,")
