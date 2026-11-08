"""Uma rodada da demonstração de índice no SQLite (Short "eu medi", índices).

Cenário: a tela "meus pedidos" de uma loja busca os pedidos de um cliente,
`SELECT id, descricao FROM pedidos WHERE cliente_id = ?`, numa tabela de um milhão de pedidos.

A rodada cria o banco do zero (semente fixa, os mesmos dados em toda rodada), mede a consulta sem
índice, a inserção de pedidos novos sem índice, o `CREATE INDEX`, a mesma consulta com índice e a
mesma inserção com índice. Imprime uma linha `chave=valor` com os tempos e os tamanhos e, com
`--planos`, os dois `EXPLAIN QUERY PLAN`.

Só biblioteca padrão. Uso: `python3 indice.py <pasta-temporaria> [--planos]`.
O banco é um arquivo da própria rodada e é apagado no fim dela.
"""

import os
import random
import sqlite3
import sys
import time

LINHAS = 1_000_000
CLIENTES = 100_000
CONSULTAS_SEM_INDICE = 20
CONSULTAS_COM_INDICE = 1_000
INSERCOES = 10_000
SEMENTE = 20261103
CONSULTA = "SELECT id, descricao FROM pedidos WHERE cliente_id = ?"


def descricao(rng: random.Random) -> str:
    letras = "abcdefghijklmnopqrstuvwxyz "
    return "".join(rng.choice(letras) for _ in range(60))


def criar(conexao: sqlite3.Connection, rng: random.Random) -> None:
    conexao.execute(
        "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL, descricao TEXT NOT NULL)"
    )
    textos = [descricao(rng) for _ in range(1_000)]
    linhas = ((rng.randint(1, CLIENTES), textos[i % 1_000]) for i in range(LINHAS))
    with conexao:
        conexao.executemany("INSERT INTO pedidos (cliente_id, descricao) VALUES (?, ?)", linhas)


def consultar(conexao: sqlite3.Connection, clientes: list[int]) -> tuple[float, int]:
    """Tempo médio por consulta, em ms, e o total de linhas devolvidas."""
    linhas = 0
    inicio = time.perf_counter()
    for cliente in clientes:
        linhas += len(conexao.execute(CONSULTA, (cliente,)).fetchall())
    return (time.perf_counter() - inicio) * 1000 / len(clientes), linhas


def inserir(conexao: sqlite3.Connection, rng: random.Random) -> float:
    """Tempo total, em ms, para inserir INSERCOES pedidos numa transação."""
    novos = [(rng.randint(1, CLIENTES), descricao(rng)) for _ in range(INSERCOES)]
    inicio = time.perf_counter()
    with conexao:
        conexao.executemany("INSERT INTO pedidos (cliente_id, descricao) VALUES (?, ?)", novos)
    return (time.perf_counter() - inicio) * 1000


def plano(conexao: sqlite3.Connection) -> str:
    return " | ".join(linha[3] for linha in conexao.execute("EXPLAIN QUERY PLAN " + CONSULTA, (1,)))


def tamanho_mb(conexao: sqlite3.Connection) -> float:
    paginas = conexao.execute("PRAGMA page_count").fetchone()[0]
    pagina = conexao.execute("PRAGMA page_size").fetchone()[0]
    return paginas * pagina / 1_000_000


def main() -> None:
    pasta = sys.argv[1]
    planos = "--planos" in sys.argv
    caminho = os.path.join(pasta, f"pedidos-{os.getpid()}.db")
    rng = random.Random(SEMENTE)
    conexao = sqlite3.connect(caminho)
    try:
        criar(conexao, rng)
        clientes_sem = [rng.randint(1, CLIENTES) for _ in range(CONSULTAS_SEM_INDICE)]
        clientes_com = [rng.randint(1, CLIENTES) for _ in range(CONSULTAS_COM_INDICE)]
        tamanho_antes = tamanho_mb(conexao)
        plano_sem = plano(conexao)
        sem_ms, linhas_sem = consultar(conexao, clientes_sem)
        inserir_sem_ms = inserir(conexao, rng)
        # Contagem de referência, ainda sem índice e já com os pedidos novos: a consulta com índice
        # precisa devolver o mesmo número de linhas.
        marcas = ",".join("?" * len(clientes_sem))
        esperadas = conexao.execute(
            f"SELECT count(*) FROM pedidos WHERE cliente_id IN ({marcas})", clientes_sem
        ).fetchone()[0]
        inicio = time.perf_counter()
        conexao.execute("CREATE INDEX pedidos_cliente ON pedidos(cliente_id)")
        criar_indice_ms = (time.perf_counter() - inicio) * 1000
        tamanho_depois = tamanho_mb(conexao)
        plano_com = plano(conexao)
        # As mesmas 20 consultas do caso sem índice, para conferir que devolvem as mesmas linhas.
        _, linhas_com_indice = consultar(conexao, clientes_sem)
        com_ms, _ = consultar(conexao, clientes_com)
        inserir_com_ms = inserir(conexao, rng)
        cache = conexao.execute("PRAGMA cache_size").fetchone()[0]
    finally:
        conexao.close()
        os.remove(caminho)
    print(
        f"sem_indice_ms={sem_ms:.3f} com_indice_ms={com_ms:.4f} criar_indice_ms={criar_indice_ms:.1f} "
        f"inserir_sem_indice_ms={inserir_sem_ms:.1f} inserir_com_indice_ms={inserir_com_ms:.1f} "
        f"tamanho_antes_mb={tamanho_antes:.1f} tamanho_depois_mb={tamanho_depois:.1f} "
        f"linhas_sem={linhas_sem} linhas_esperadas={esperadas} linhas_com_indice={linhas_com_indice} "
        f"confere={'sim' if esperadas == linhas_com_indice else 'nao'} cache_size={cache}"
    )
    if planos:
        print(f"plano_sem_indice={plano_sem}")
        print(f"plano_com_indice={plano_com}")


if __name__ == "__main__":
    main()
