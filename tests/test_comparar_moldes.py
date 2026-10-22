"""Testes de `comparar_moldes.py` e da opção `--amostra` do `molde.py` (skill `analise-de-formato`)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "analise-de-formato"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, SKILL / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


comparar_mod = _load("comparar_moldes")
molde_mod = _load("molde")


def molde(nome: str, **changes: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "gerado_em": "2026-10-22", "grupos": [nome], "assunto": None,
        "videos": {"n": 13, "ids": [], "com_batidas": 13, "canais": {}},
        "medidas": {
            "palavras_min": {"mediana": 184.0, "q1": 179.0, "q3": 193.0, "n": 13, "origem": "medidas.csv"},
            "capitulo_min": {"mediana": 3.8, "q1": 3.5, "q3": 4.0, "n": 13, "origem": "capitulos"},
            "primeiro_eu_s": {"mediana": 3.0, "n": 13, "origem": "transcricao"},
        },
        "prevalencia": {
            "confissao": {"com": 11, "n": 13, "pct": 85, "forca": "padrao", "unidade": "videos"},
            "fecho_volta": {"com": 11, "n": 13, "pct": 85, "forca": "padrao", "unidade": "videos"},
            "gancho_pago": {"com": 7, "n": 13, "pct": 54, "forca": "indicio", "unidade": "videos"},
        },
        "curvas": {"decimos": 10, "n_videos": 13, "eu_por_10min": [15, 16, 15, 10, 5, 16, 15, 5, 24, 40]},
    }
    base.update(changes)
    return base


def test_comparacao_le_medidas_tracos_e_curvas() -> None:
    a = molde("FILO")
    b = molde(
        "TOPO",
        medidas={
            "palavras_min": {"mediana": 150.0, "q1": 140.0, "q3": 160.0, "n": 9, "origem": "medidas.csv"},
            "capitulo_min": {"mediana": 3.7, "q1": 3.0, "q3": 4.5, "n": 9, "origem": "capitulos"},
            "voce_por_mil": {"mediana": 9.0, "q1": 5.0, "q3": 12.0, "n": 9, "origem": "medidas.csv"},
        },
        prevalencia={
            "confissao": {"com": 8, "n": 9, "pct": 89, "forca": "padrao", "unidade": "videos"},
            "fecho_volta": {"com": 3, "n": 9, "pct": 33, "forca": "indicio", "unidade": "videos"},
            "gancho_pago": {"com": 5, "n": 9, "pct": 56, "forca": "indicio", "unidade": "videos"},
        },
        curvas={"decimos": 10, "n_videos": 9, "eu_por_10min": [10] * 9 + [30]},
    )
    texto = comparar_mod.comparar(a, b, "Filosofatos", "Topo")
    assert "# Moldes lado a lado: Filosofatos × Topo" in texto
    assert "| palavras_min | 184 (179–193, n 13) | 150 (140–160, n 9) | A maior |" in texto
    assert "| capitulo_min | 3.8 (3.5–4, n 13) | 3.7 (3–4.5, n 9) | iguais |" in texto
    assert "Só em A: primeiro_eu_s. Só em B: voce_por_mil." in texto
    assert "| confissao | 11/13 (85%, padrao) | 8/9 (89%, padrao) | padrão nos dois |" in texto
    assert "| fecho_volta | 11/13 (85%, padrao) | 3/9 (33%, indicio) | divergem |" in texto
    assert "| gancho_pago | 7/13 (54%, indicio) | 5/9 (56%, indicio) | concordam |" in texto
    assert "| eu_por_10min | 15 16 15 10 5 16 15 5 24 40 | 10 10 10 10 10 10 10 10 10 30 |" in texto
    assert "- Padrão nos dois moldes: confissao." in texto
    assert "- Traços que divergem: fecho_volta." in texto
    assert "- Medidas iguais: 1; diferentes: 1." in texto


def test_leitura_sem_quartis_e_empate() -> None:
    sem = {"mediana": 3.0, "n": 2}
    com = {"mediana": 3.0, "q1": 2.0, "q3": 4.0, "n": 9}
    assert comparar_mod.leitura_medida(sem, com) == "sem quartis"
    assert comparar_mod.leitura_medida(com, com) == "iguais"
    assert comparar_mod.leitura_medida({**com, "mediana": 9.0, "q1": 8.0, "q3": 10.0}, com) == "A maior"


def test_cli_grava_markdown(tmp_path: Path, capsys: Any) -> None:
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(molde("FILO")), encoding="utf-8")
    pb.write_text(json.dumps(molde("TOPO")), encoding="utf-8")
    saida = tmp_path / "out" / "comparacao.md"
    assert comparar_mod.main([str(pa), str(pb), "--nomes", "Filosofatos", "Topo", "--saida", str(saida)]) == 0
    assert saida.exists() and "Filosofatos × Topo" in saida.read_text(encoding="utf-8")
    assert comparar_mod.main([str(pa), str(pb)]) == 0
    assert "# Moldes lado a lado: a × b" in capsys.readouterr().out


def test_molde_aceita_outra_amostra(tmp_path: Path) -> None:
    pasta = tmp_path / "nicho"
    pasta.mkdir()
    cabecalho = "video_id\tgrupo\tcanal\tviews\tduracao_s\tmotivo\ttitulo\n"
    (pasta / "amostra.tsv").write_text(cabecalho + "vidA\tH\t@a\t100\t600\tx\tt\n", encoding="utf-8")
    (pasta / "medidas.csv").write_text(
        "video_id,canal,idioma,views,duracao_s,palavras_min,cortes_min\n"
        "vidA,Canal,pt-BR,100,600,180,2\nvidB,Canal,pt-BR,900,300,200,1\n",
        encoding="utf-8",
    )
    outra = tmp_path / "amostra-topo.tsv"
    outra.write_text(cabecalho + "vidB\tTOPO\t@b\t900\t300\ttopo\tt\n", encoding="utf-8")
    padrao = molde_mod.construir(pasta, None, ["TOPO"], None)
    assert padrao["videos"]["n"] == 0  # a amostra padrão não tem o grupo TOPO
    topo = molde_mod.construir(pasta, None, ["TOPO"], None, outra)
    assert topo["videos"]["ids"] == ["vidB"] and topo["amostra"] == str(outra)
    assert topo["medidas"]["palavras_min"]["mediana"] == 200.0
