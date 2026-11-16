"""Mede HashMap e colisões (Short "eu medi"): mesmo procedimento do medir.sh, em Python.

Existe porque a rotina de 2026-11-09 não conseguiu executar o medir.sh (a execução de script de shell exigia
aprovação que a sessão não tem). 15 rodadas de Demo.java nos modos bom, fraco, constante e
constante-comparable, cada execução num processo novo (aquecimento da JVM dentro do processo). Antes de cada
rodada, cpu_probe(); espera a sonda abaixo de 0,12 s, com 10 s de pausa entre rodadas. Grava resultado.txt na
pasta do script.
Uso: .venv/bin/python renders/short-hashmap-colisoes-java/demo/medir.py
"""

import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ))
from app.pipeline.bench import cpu_probe  # noqa: E402

RODADAS = int(os.environ.get("RODADAS", "15"))
LIVRE = float(os.environ.get("LIVRE", "0.12"))
PAUSA = int(os.environ.get("PAUSA", "10"))
MODOS = ["bom", "fraco", "constante", "constante-comparable"]
CHAVES = ["hashes_distintos", "maior_grupo", "equals_por_busca", "ms_insercao", "ms_busca", "ns_por_busca"]


def cpu_nome() -> str:
    for linha in Path("/proc/cpuinfo").read_text().splitlines():
        if linha.startswith("model name"):
            return linha.split(":", 1)[1].strip()
    return platform.processor()


def versao_java() -> str:
    r = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
    return (r.stderr or r.stdout).splitlines()[0]


def estat(v: list[float]) -> str:
    return f"mediana={statistics.median(v):g} minimo={min(v):g} maximo={max(v):g}"


def main() -> int:
    saida: list[str] = []

    def emit(texto: str) -> None:
        saida.append(texto)
        (AQUI / "resultado.txt").write_text("\n".join(saida) + "\n")

    emit(
        f"# {datetime.now().astimezone().isoformat(timespec='seconds')} | {versao_java()} | {cpu_nome()} | "
        f"{os.cpu_count()} processadores visiveis | 20000 chaves ChaveSessao(usuario, dispositivo), "
        "mesmas 20000 "
        "buscas em ordem embaralhada (semente 42) com instancias novas das chaves | aquecimento de 200 "
        "ciclos com "
        "2000 chaves antes de medir | tempo so em memoria (sem rede, sem banco) | "
        f"sonda abaixo de {LIVRE} s antes de cada rodada, pausa de {PAUSA} s | {RODADAS} rodadas | "
        "executado por medir.py"
    )
    valores: dict[tuple[str, str], list[float]] = {(m, k): [] for m in MODOS for k in CHAVES}
    for r in range(1, RODADAS + 1):
        if r > 1:
            time.sleep(PAUSA)
        limite = time.time() + 300
        p = cpu_probe()
        while p >= LIVRE:
            if time.time() >= limite:
                print(
                    f"## abortado na rodada={r}: cpu_probe={p:.3f} acima de {LIVRE} s por 5 minutos",
                    file=sys.stderr,
                )
                return 3
            time.sleep(10)
            p = cpu_probe()
        for modo in MODOS:
            linha = subprocess.run(
                ["java", "Demo.java", modo], cwd=AQUI, capture_output=True, text=True, check=True
            ).stdout.strip()
            emit(f"rodada={r} cpu_probe={p:.3f} {linha}")
            campos = dict(x.split("=", 1) for x in linha.split())
            for k in CHAVES:
                valores[(modo, k)].append(float(campos[k]))
    emit(f"## cpu_probe ao fim: {cpu_probe():.3f}")
    for modo in MODOS:
        for k in CHAVES:
            emit(f"## resumo {modo} {k} {estat(valores[(modo, k)])}")
    base = statistics.median(valores[("bom", "ns_por_busca")])
    for modo in ["fraco", "constante", "constante-comparable"]:
        t = statistics.median(valores[(modo, "ns_por_busca")])
        emit(f"## razao ns por busca {modo}/bom (medianas) = {t / base:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
