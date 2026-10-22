"""Testes de `reproduzivel.py` (skill `analise-de-formato`): a regra do que a pipeline reproduz, em código."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "analise-de-formato"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, SKILL / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rep = _load("reproduzivel")

COLS = (
    "video_id\tapresentador\tquadros_com_apresentador\tbase_principal\tpct_base_principal\tbase_secundaria"
    "\ttexto_na_tela\tmovimento\tnota\n"
)


@pytest.mark.parametrize(
    ("apresentador", "base", "secundaria", "esperado"),
    [
        ("nenhum", "pintura", "", "sim"),
        ("nenhum", "anime_parado", "texto_grafico", "sim"),
        ("nenhum", "ilustracao_propria", "anime_movimento", "parcial: base secundária"),
        ("nenhum", "misto", "", "parcial: misto"),
        ("nenhum", "anime_movimento", "", "nao: base"),
        ("nenhum", "gameplay", "", "nao: base"),
        ("real", "pintura", "", "nao: apresentador"),
        ("desenhado", "ilustracao_propria", "", "nao: apresentador"),
        ("nenhum", "", "", "sem leitura"),
    ],
)
def test_veredito(apresentador: str, base: str, secundaria: str, esperado: str) -> None:
    assert rep.veredito(apresentador, base, secundaria) == esperado


@pytest.fixture
def cache(tmp_path: Path) -> tuple[Path, Path]:
    pasta = tmp_path / "nicho"
    pasta.mkdir()
    videos = [("vidA", "A Psique", 3_000_000, 1036, "pt"), ("vidB", "Ciência", 3_400_000, 614, "pt"),
              ("vidC", "Sock", 24_000, 500, "en-US"), ("vidD", "Relry", 27_000, 300, "pt")]
    for vid, canal, views, dur, _ in videos:
        (pasta / f"{vid}.info.json").write_text(json.dumps(
            {"id": vid, "channel": canal, "view_count": views, "duration": dur, "title": f"Título {vid}"}
        ))
    (pasta / "medidas.csv").write_text(
        "video_id,canal,idioma\n" + "".join(f"{v},{c},{i}\n" for v, c, _, _, i in videos), encoding="utf-8",
    )
    imagem = tmp_path / "imagem.tsv"
    imagem.write_text(COLS + (
        "vidA\tnenhum\t0\tpintura\t90\t\tcitacao\tparado_zoom\tquadros clássicos\n"
        "vidB\treal\t22\ttexto_grafico\t25\t\tpalavra_chave\tem_movimento\tapresentador em estúdio\n"
        "vidC\tnenhum\t0\tfoto_arquivo\t80\t\tnenhum\tparado_zoom\tem inglês\n"
        "vidD\tnenhum\t0\tanime_parado\t85\t\tpalavra_chave\tparado_zoom\tpoucas views\n"
    ), encoding="utf-8")
    return pasta, imagem


def test_tabela_junta_leitura_e_metadados(cache: tuple[Path, Path]) -> None:
    pasta, imagem = cache
    linhas = rep.tabela(pasta, [imagem])
    assert [r["video_id"] for r in linhas] == ["vidB", "vidA", "vidD", "vidC"]  # por views
    por_id = {r["video_id"]: r for r in linhas}
    assert por_id["vidA"]["reproduzivel"] == "sim" and por_id["vidA"]["canal"] == "A Psique"
    assert por_id["vidB"]["reproduzivel"] == "nao: apresentador"
    assert por_id["vidA"]["duracao_min"] == 17.3 and por_id["vidA"]["idioma"] == "pt"


def test_topo_filtra_por_veredito_views_e_idioma(cache: tuple[Path, Path]) -> None:
    pasta, imagem = cache
    linhas = rep.tabela(pasta, [imagem])
    assert [r["video_id"] for r in rep.topo(linhas, 400_000)] == ["vidA"]
    assert [r["video_id"] for r in rep.topo(linhas, 10_000)] == ["vidA", "vidD"]  # vidC é en-US


def test_cli_grava_tabela_e_amostra(cache: tuple[Path, Path], capsys: Any) -> None:
    pasta, imagem = cache
    saida = pasta / "analise" / "reproduzivel"
    assert rep.main([str(pasta), str(imagem), "--minimo-views", "400000"]) == 0
    assert (saida / "reproduzivel.tsv").exists()
    amostra = (saida / "amostra-topo.tsv").read_text(encoding="utf-8").splitlines()
    assert amostra[0].startswith("video_id\tgrupo\tcanal")
    assert amostra[1].startswith("vidA\tTOPO\tA Psique\t3000000\t1036\t")
    assert "1 no grupo TOPO" in capsys.readouterr().out
    vazio = pasta / "vazio.tsv"
    vazio.write_text(COLS, encoding="utf-8")
    assert rep.main([str(pasta), str(vazio)]) == 1
