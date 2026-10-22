"""Testes de `molde.py` e `partitura.py` da skill `analise-de-formato` (ADR 031, parte B)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "analise-de-formato"

BATIDAS_A = """# assunto: voce
# tese: a gente guarda objeto velho por medo de perder quem era
# mensagem: você também faz isso
00:00\tCASO\t0\t\tas caixas no corredor
01:00\tPROMESSA\t0\t\tpor que é difícil jogar fora
01:30\tGANCHO-PLANTA\t0\tg1\to bilhete
02:00\tCAPITULO\t1\t\to navio
02:00\tCASO\t1\t\to navio que troca as tábuas
03:30\tCONCEITO\t1\t\tidentidade
04:30\tAPLICA\t1\t\ta gaveta como se fosse a gente
05:00\tCAPITULO\t2\t\to psicólogo
05:00\tCONCEITO\t2\t\to apego medido
06:00\tPERGUNTA\t2\t\to que sobra de você?
07:00\tCONFISSAO\t2\t\ta gaveta de cabos
08:00\tGANCHO-PAGA\t2\tg1\to bilhete lido
08:00\tFECHO-VOLTA\t2\t\tas caixas de novo
10:00\tFIM\t2\t\t
"""

BATIDAS_B = """# assunto: obra
# tese: o vilão é um espelho
# mensagem: veja a obra de novo
00:00\tCASO\t0\t\ta cena do trem
01:00\tCAPITULO\t1\t\to plano
01:00\tCONCEITO\t1\t\tfins e meios
02:30\tCASO\t1\t\to primeiro assassinato
04:00\tCAPITULO\t2\t\to espelho
04:00\tCASO\t2\t\to espectador no sofá
05:00\tOPINIAO\t2\t\tnarrador discorda
06:00\tFIM\t2\t\t
"""


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, SKILL / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


molde_mod = _load("molde")
partitura_mod = _load("partitura")


def _transcricao(linhas: list[tuple[int, str]]) -> str:
    return "\n".join(f"[{s // 60:02d}:{s % 60:02d}] {t}" for s, t in linhas) + "\n"


@pytest.fixture
def cache(tmp_path: Path) -> tuple[Path, Path]:
    pasta = tmp_path / "nicho"
    pasta.mkdir()
    notas = tmp_path / "notas"
    (notas / "batidas").mkdir(parents=True)
    videos = [("vidA", "FILO", 1000, 600), ("vidB", "FILO", 500, 360), ("vidC", "OUTRO", 2000, 480)]
    (pasta / "amostra.tsv").write_text(
        "video_id\tgrupo\tcanal\tviews\tduracao_s\tmotivo\ttitulo\n"
        + "".join(f"{v}\t{g}\t@canal\t{views}\t{dur}\ttop\tTítulo {v}\n" for v, g, views, dur in videos),
        encoding="utf-8",
    )
    cabecalho = ("video_id,canal,idioma,inscritos,views,publicado,duracao_s,legenda,arquivo_legenda,palavras,"
                 "palavras_min,cortes_min,plano_medio_s,voce_por_mil,nos_por_mil,eu_por_mil,fonte_por_mil,"
                 "palavras_60s,voce_60s,cortes_60s,capitulos,titulo\n")
    linhas = [
        "vidA,Canal,pt-BR,1,1000,20260101,600,auto,a.vtt,1800,180,2.0,30,8,2,10,0.5,190,2,1,3,t\n",
        "vidB,Canal,pt-BR,1,500,20260101,360,auto,b.vtt,1140,190,1.0,60,4,1,6,0.0,170,1,0,3,t\n",
        "vidC,Canal,en,1,2000,20260101,480,auto,c.vtt,1600,200,5.0,12,0,0,0,0.0,200,0,5,0,t\n",
    ]
    (pasta / "medidas.csv").write_text(cabecalho + "".join(linhas), encoding="utf-8")
    janelas = ["video_id,janela,inicio_s,posicao,palavras,palavras_min,cortes_min,voce,nos,eu,fonte\n"]
    for vid, _grupo, _views, dur in videos[:2]:
        n = dur // 30
        for j in range(n):
            voce = 2 if j in (0, n - 1) else 0
            janelas.append(f"{vid},{j},{j * 30},{j / n:.2f},90,180,2,{voce},0,1,0\n")
    (pasta / "janelas.csv").write_text("".join(janelas), encoding="utf-8")
    capitulos_a = [
        {"start_time": 0, "end_time": 120, "title": "As caixas"},
        {"start_time": 120, "end_time": 300, "title": "O navio de Teseu"},
        {"start_time": 300, "end_time": 600, "title": "O psicólogo do apego"},
    ]
    info_a = {"id": "vidA", "duration": 600, "chapters": capitulos_a}
    (pasta / "vidA.info.json").write_text(json.dumps(info_a))
    (pasta / "vidB.info.json").write_text(json.dumps({"id": "vidB", "duration": 360, "chapters": []}))
    (pasta / "vidA.txt").write_text(_transcricao([
        (0, "Eu abri a caixa da minha avó em 2019."),
        (20, "Você guarda coisa velha? Por quê?"),
        (125, "Teseu tinha um navio, e o navio trocava as tábuas."),
        (305, "Um psicólogo mediu o apego com uma régua."),
    ]), encoding="utf-8")
    (pasta / "vidB.txt").write_text(_transcricao([
        (0, "Nesse vídeo eu vou te mostrar o trem."),
        (40, "E você, torceu por ele?"),
    ]), encoding="utf-8")
    (notas / "batidas" / "vidA.batidas.tsv").write_text(BATIDAS_A, encoding="utf-8")
    (notas / "batidas" / "vidB.batidas.tsv").write_text(BATIDAS_B, encoding="utf-8")
    return pasta, notas


def test_molde_resume_medidas_prevalencia_e_curvas(cache: tuple[Path, Path]) -> None:
    pasta, notas = cache
    molde = molde_mod.construir(pasta, notas, ["FILO"], None)

    assert molde["videos"]["n"] == 2  # vidC é de outro grupo
    assert molde["videos"]["com_batidas"] == 2
    palavras = molde["medidas"]["palavras_min"]
    assert palavras["mediana"] == 185.0 and palavras["n"] == 2 and palavras["origem"] == "medidas.csv"
    assert "topo" not in palavras  # terços só com 6 ou mais vídeos
    assert molde["medidas"]["duracao_min"]["origem"] == "amostra"
    assert molde["medidas"]["plano_medio_s"]["origem"] == "medidas.csv"

    # capítulos: só vidA tem 3 ou mais; a abertura é o fim do primeiro capítulo
    assert molde["medidas"]["capitulos_n"] == {"mediana": 3.0, "n": 1, "origem": "capitulos"}
    assert molde["medidas"]["abertura_capitulo_s"]["mediana"] == 120.0
    assert molde["prevalencia"]["capitulos"] == {
        "com": 1, "n": 2, "pct": 50, "forca": "indicio", "unidade": "videos",
    }
    # "As caixas" não é dito (a fala diz "caixa"); "navio" e "psicólogo" são
    assert molde["prevalencia"]["titulo_dito"]["com"] == 2 and molde["prevalencia"]["titulo_dito"]["n"] == 3

    # transcrição: marcos da abertura e promessa explícita
    assert molde["medidas"]["primeiro_eu_s"]["mediana"] == 0.0
    assert molde["medidas"]["primeiro_voce_s"]["mediana"] == 30.0  # mediana de 20 e 40
    assert molde["medidas"]["primeiro_ano_s"] == {"mediana": 0.0, "n": 1, "origem": "transcricao"}
    assert molde["prevalencia"]["promessa_explicita"]["com"] == 1

    # batidas: estrutura e traços
    assert molde["medidas"]["batidas_pct_caso"]["n"] == 2
    assert molde["prevalencia"]["confissao"]["com"] == 1
    assert molde["prevalencia"]["gancho_pago"]["com"] == 1
    assert molde["prevalencia"]["fecho_volta"]["com"] == 1
    # vidA: bloco 1 abre com caso, bloco 2 com conceito; vidB: bloco 1 com conceito, bloco 2 com caso
    assert molde["prevalencia"]["bloco_abre_com_caso"] == {
        "com": 2, "n": 4, "pct": 50, "forca": "indicio", "unidade": "blocos",
    }
    assert molde["prevalencia"]["caso_antes_do_conceito"]["com"] == 1  # só o bloco 1 de vidA

    # curvas: 10 décimos, "você" nas pontas
    curva = molde["curvas"]["voce_por_10min"]
    assert len(curva) == 10 and curva[0] > 0 and curva[9] > 0 and curva[4] == 0.0


def test_molde_filtra_por_assunto_das_batidas(cache: tuple[Path, Path]) -> None:
    pasta, notas = cache
    molde = molde_mod.construir(pasta, notas, [], "obra")
    assert molde["videos"]["ids"] == ["vidB"]
    assert molde["assunto"] == "obra"


def test_molde_ignora_idioma_fora_do_portugues(cache: tuple[Path, Path]) -> None:
    pasta, notas = cache
    molde = molde_mod.construir(pasta, notas, [], None)
    assert "vidC" not in molde["videos"]["ids"]


def test_molde_cli_grava_json(cache: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    pasta, notas = cache
    assert molde_mod.main([str(pasta), "--notas", str(notas), "--grupo", "FILO"]) == 0
    saida = pasta / "analise" / "molde.json"
    assert saida.exists()
    assert json.loads(saida.read_text(encoding="utf-8"))["grupos"] == ["FILO"]
    assert "2 vídeo(s)" in capsys.readouterr().out
    assert molde_mod.main([str(pasta), "--grupo", "NADA"]) == 1


@pytest.mark.parametrize(
    ("com", "n", "esperado"), [(12, 13, "padrao"), (7, 13, "indicio"), (5, 5, "indicio")],
)
def test_forca(com: int, n: int, esperado: str) -> None:
    assert molde_mod.forca(com, n) == esperado


def _molde_exemplo() -> dict[str, Any]:
    return {
        "gerado_em": "2026-10-22", "grupos": ["FILO"], "assunto": None,
        "videos": {"n": 13, "ids": [], "com_batidas": 13, "canais": {}},
        "medidas": {
            "duracao_min": {"mediana": 22.8, "q1": 20.9, "q3": 29.4, "n": 13, "origem": "amostra"},
            "abertura_capitulo_s": {
                "mediana": 202.0, "q1": 184.0, "q3": 233.5, "n": 13, "origem": "capitulos",
            },
            "capitulo_min": {"mediana": 3.8, "q1": 3.5, "q3": 4.0, "n": 13, "origem": "capitulos"},
            "primeiro_eu_s": {"mediana": 3.0, "n": 13, "origem": "transcricao"},
            "primeira_pergunta_s": {"mediana": 29.0, "n": 13, "origem": "transcricao"},
            "primeiro_voce_s": {"mediana": 11.0, "n": 13, "origem": "transcricao"},
            "batidas_posicao_confissao_pct": {"mediana": 68.0, "n": 11, "origem": "batidas"},
            "batidas_confissoes": {"mediana": 3.0, "q1": 1.0, "q3": 9.0, "n": 13, "origem": "batidas"},
            "batidas_pct_caso": {"mediana": 38.8, "q1": 21.4, "q3": 53.9, "n": 13, "origem": "batidas"},
            "palavras_min": {"mediana": 184.0, "q1": 179.0, "q3": 193.0, "n": 13, "origem": "medidas.csv"},
        },
        "prevalencia": {
            "confissao": {"com": 11, "n": 13, "pct": 85, "forca": "padrao", "unidade": "videos"},
            "gancho_pago": {"com": 7, "n": 13, "pct": 54, "forca": "indicio", "unidade": "videos"},
            "fecho_volta": {"com": 11, "n": 13, "pct": 85, "forca": "padrao", "unidade": "videos"},
            "chamada": {"com": 4, "n": 13, "pct": 31, "forca": "indicio", "unidade": "videos"},
            "promessa_explicita": {"com": 5, "n": 13, "pct": 38, "forca": "indicio", "unidade": "videos"},
            "bloco_abre_com_caso": {"com": 39, "n": 78, "pct": 50, "forca": "indicio", "unidade": "blocos"},
        },
        "curvas": {
            "decimos": 10, "n_videos": 13,
            "voce_por_10min": [20, 24, 14, 10, 15, 16, 15, 15, 10, 23],
            "eu_por_10min": [15, 16, 15, 10, 5, 16, 15, 5, 24, 40],
            "cortes_min": [0.8, 3.1, 1.6, 2.8, 2.0, 1.5, 2.0, 1.0, 2.5, 6.0],
            "palavras_min": [186, 191, 186, 183, 185, 180, 182, 182, 184, 196],
        },
    }


def test_plano_escala_abertura_e_blocos() -> None:
    molde = _molde_exemplo()
    doze = partitura_mod.plano(molde, 12)
    vinte_e_quatro = partitura_mod.plano(molde, 24)
    # abertura proporcional (202 s em 22,8 min → ~106 s em 12 min), nunca acima da do molde
    assert 100 < doze["abertura_s"] < 115
    assert vinte_e_quatro["abertura_s"] == 202.0
    # blocos do tamanho do molde: 12 min dá 2, 24 min dá 5
    assert doze["blocos"] == 2 and vinte_e_quatro["blocos"] == 5
    assert partitura_mod.plano(molde, 12, blocos_pedidos=3)["blocos"] == 3
    assert doze["fecho_inicio_s"] == 648.0
    assert doze["confissao_s"] == pytest.approx(0.68 * 720)


def test_render_traz_casas_curvas_e_alvos() -> None:
    texto = partitura_mod.render(_molde_exemplo(), 12, "obra", "teste", "molde.json")
    assert "# Partitura: teste" in texto
    assert "| até 0:03 | primeiro \"eu\" |" in texto
    assert "confissão do narrador" in texto and "85%, padrao" in texto
    assert "gancho plantado" in texto  # 54% passa do limiar de 50%
    assert "quase sem chamada" in texto  # 31% não passa
    assert "cada décimo = 1:12" in texto
    assert "| 10:48–12:00 | 2.8 | 4.8 |" in texto  # 23 e 40 por 10 min, num décimo de 72 s
    assert "| % do tempo em caso | 21.4 | 38.8 | 53.9 | 13 |" in texto
    assert "Forma, nunca fato" in texto
    # marcos em ordem de tempo
    assert texto.index('primeiro "eu"') < texto.index('primeiro "você"') < texto.index("primeira pergunta")


def test_cli_grava_no_episodio_sem_sobrescrever(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    molde_path = tmp_path / "molde.json"
    molde_path.write_text(json.dumps(_molde_exemplo()), encoding="utf-8")
    episodio = tmp_path / "ep-01"
    args = [str(molde_path), "--duracao", "12", "--assunto", "obra", "--episodio", str(episodio)]
    assert partitura_mod.main(args) == 0
    assert (episodio / "partitura.md").exists()
    copia = json.loads((episodio / "molde.json").read_text(encoding="utf-8"))
    assert copia["copiado_de"] == str(molde_path) and "copiado_em" in copia
    assert copia["episodio"]["duracao_min"] == 12 and copia["episodio"]["blocos"] == 2
    assert copia["episodio"]["assunto"] == "obra" and copia["episodio"]["fecho_inicio_s"] == 648.0
    assert "ep-01" in (episodio / "partitura.md").read_text(encoding="utf-8")

    assert partitura_mod.main(args) == 1
    assert "já existe" in capsys.readouterr().err
    assert partitura_mod.main([*args, "--sobrescrever"]) == 0


def test_cli_avisa_assunto_diferente(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    molde = _molde_exemplo()
    molde["assunto"] = "voce"
    molde_path = tmp_path / "molde.json"
    molde_path.write_text(json.dumps(molde), encoding="utf-8")
    assert partitura_mod.main([str(molde_path), "--duracao", "10", "--assunto", "obra"]) == 0
    saida = capsys.readouterr()
    assert "aviso" in saida.err and "# Partitura: episódio" in saida.out
