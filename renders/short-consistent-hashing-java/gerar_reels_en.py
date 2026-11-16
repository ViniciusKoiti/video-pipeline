"""Versão em inglês dos três Reels de consistent hashing (texto e conferência; sem voz nem render).

Uso: python3 gerar_reels_en.py
- public/lottie/anel-en.json: o Lottie do anel com os textos internos traduzidos 
  (importa gerar_animacoes sem rodar o main).
- reels/<empresa>/content.en.json: tradução do content.pt.json por tabela; texto sem entrada na tabela aborta.
- data/episodes/reel-consistent-hashing-<empresa>-en/: narracao.json, content.json, traducao.json,
  voice/glossary.json, medicao.json.
"""

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import gerar_animacoes as g  # noqa: E402  (só funções; o main não roda)
import montar_episodios_reels as m  # noqa: E402

LOTTIE_TR = {
    "o anel de consistent hashing": "the consistent hashing ring",
    "primeiro servidor no": "first server",
    "sentido horário": "clockwise",
    "3 de 12 chaves trocaram, todas para S5": "3 of 12 keys moved, all to S5",
    "exemplo didático": "teaching example",
}

TR = {
    "Amazon · Dynamo": "Amazon · Dynamo",
    "Akamai · CDN": "Akamai · CDN",
    "Discord · 2017": "Discord · 2017",
    "Como a Amazon adiciona um servidor sem esvaziar o cache?"
    : "How does Amazon add a server without emptying the cache?",
    "sem esvaziar o cache": "without emptying the cache",
    "Quem trocou de servidor? (4 → 5)": "Who changed server? (4 → 5)",
    "Módulo (hash % N)": "Modulo (hash % N)",
    "80,18%": "80.18%",
    "das sessões trocaram": "of the sessions moved",
    "Anel, 100 pontos": "Ring, 100 points",
    "20,13%": "20.13%",
    "trocaram, todas para o novo": "moved, all to the new one",
    "Carga do servidor mais cheio, em % da ideal": "Load on the fullest server, as % of ideal",
    "Anel, 1 ponto": "Ring, 1 point",
    "Anel, 10 pontos": "Ring, 10 points",
    "Quantos pontos virtuais por servidor?": "How many virtual points per server?",
    "Comenta o seu número": "Comment your number",
    "Amazon Dynamo (SOSP 2007) · medição de 08/11/2026 · Java 25 · 100 mil sessões · 4 → 5 servidores · 15 "
    "rodadas"
    : "Amazon Dynamo (SOSP 2007) · measured 2026-11-08 · Java 25 · 100k sessions · 4 → 5 servers · 15 runs",
    "Como a Akamai decide qual servidor entrega cada arquivo?"
    : "How does Akamai decide which server delivers each file?",
    "qual servidor": "which server",
    "Dentro de um cluster da Akamai": "Inside an Akamai cluster",
    "Pedido do arquivo": "File request",
    "Escolhe o cluster": "Picks the cluster",
    "Hash consistente": "Consistent hash",
    "escolhe o servidor": "picks the server",
    "Servidor de borda": "Edge server",
    "Aguenta mover 80% do cache?": "Can it move 80% of the cache?",
    "Comenta o que você faria": "Comment what you would do",
    "Maggs e Sitaraman (ACM CCR, 2015) · medição de 08/11/2026 · Java 25 · 100 mil sessões · 4 → 5 servidores"
    : "Maggs and Sitaraman (ACM CCR, 2015) · measured 2026-11-08 · Java 25 · 100k sessions · 4 → 5 servers",
    "Como o Discord descobre em qual nó está cada comunidade?"
    : "How does Discord find which node holds each community?",
    "qual nó": "which node",
    "Achar o nó da comunidade": "Finding the community's node",
    "Sessão": "Session",
    "quer a comunidade": "wants the community",
    "Anel de hash": "Hash ring",
    "consistent hashing": "consistent hashing",
    "Nó da comunidade": "Community node",
    "consulta": "lookup",
    "devolve o nó": "returns the node",
    "Muitos reconectando de uma vez": "Many reconnecting at once",
    "Usuários": "Users",
    "reconectando juntos": "reconnecting together",
    "Processo do anel": "Ring process",
    "um só": "just one",
    "Sistema": "System",
    "consultas": "lookups",
    "espera": "waiting",
    "Anel em memória compartilhada: 12 µs → 0,3 µs": "Ring in shared memory: 12 µs → 0.3 µs",
    "Sessões": "Sessions",
    "leem direto": "read directly",
    "Anel": "Ring",
    "memória só de leitura": "read-only memory",
    "0,3 µs": "0.3 µs",
    "Seu anel está na memória de quem consulta?": "Is your ring in the memory of whoever queries it?",
    "Comenta como você faz": "Comment how you do it",
    "Discord Engineering (06/07/2017) · números do Discord, não medidos aqui":
        "Discord Engineering (2017-07-06) · numbers are Discord's, not measured here",
}
CHAVES = {"title", "text", "highlight", "kicker", "sub", "label", "sublabel", "footer"}

NARRACAO_EN = {
    "amazon": [
        "How does Amazon add a server without emptying the cache?",
        "In Dynamo, keys and servers sit on a ring, and each key goes to the first server clockwise, and "
        "when a server joins, only its neighbors feel the change.",
        "In my measurement, the remainder of the hash moved eighty in every hundred keys, and the ring with "
        "a hundred points per server, twenty.",
        "With a single point the load comes out lopsided, and that is why Dynamo uses several points per "
        "server, the virtual nodes.",
        "How many virtual points would you give each server?",
    ],
    "akamai": [
        "How does Akamai decide which server delivers each file?",
        "Files and servers go onto the same circle, and each file goes to the next server clockwise.",
        "That method was the first algorithmic innovation in Akamai's delivery network, and it splits the "
        "load inside a cluster.",
        "When a server joins, only the files that fall on it need to move, and in my measurement, with a "
        "hundred points per server, it was twenty in every hundred, against eighty with the hash remainder.",
        "Could your system move eighty in every hundred cache entries at once?",
    ],
    "discord": [
        "How does Discord find which node holds each community?",
        "In 2017, they used a consistent hashing ring to find the node of each community.",
        "But when many users reconnected together, the process that owned the ring could not keep up, and "
        "the whole system became overloaded.",
        "The fix was to put the ring in shared read-only memory, and each lookup dropped from twelve "
        "microseconds to zero point three.",
        "Does your ring live in the memory of whoever queries it, or behind a single process?",
    ],
}
GLOSSARIO_EN = [
    ("Dynamo", "Dynamo"),
    ("Akamai", "ah kuh my"),
    ("Discord", "Discord"),
    ("TreeMap", "tree map"),
    ("hash", "hash"),
    ("hashing", "hashing"),
    ("cluster", "cluster"),
    ("consistent", "consistent"),
]


def traduz(no):
    if isinstance(no, dict):
        out = {}
        for k, v in no.items():
            if k in CHAVES and isinstance(v, str):
                out[k] = TR[v]  # KeyError = texto sem tradução
            elif k == "lines":
                out[k] = [TR[x] for x in v]
            elif k == "path" and v == "lottie/anel.json":
                out[k] = "lottie/anel-en.json"
            else:
                out[k] = traduz(v)
        return out
    if isinstance(no, list):
        return [traduz(x) for x in no]
    return no


def lottie_en() -> str:
    original = g.text
    g.text = lambda layers, value, *a, **k: original(layers, LOTTIE_TR.get(value, value), *a, **k)
    try:
        dados = g.anel()
    finally:
        g.text = original
    texto = dados if isinstance(dados, str) else json.dumps(dados, ensure_ascii=False)
    destino = AQUI / "public" / "lottie" / "anel-en.json"
    destino.write_text(texto, encoding="utf-8")
    licencas = AQUI / "licencas.json"
    lista = [x for x in json.loads(licencas.read_text(encoding="utf-8")) if x["id"] != "anel-en"]
    lista.append(
        {
            "id": "anel-en",
            "file": "public/lottie/anel-en.json",
            "license": "Original",
            "sha256": hashlib.sha256(texto.encode()).hexdigest(),
            "usage_notes": "Gráfico vetorial original gerado por gerar_reels_en.py (gerar_animacoes.anel com "
                "os textos em inglês); exemplo didático, sem mídia externa.",
        }
    )
    licencas.write_text(json.dumps(lista, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(destino)


if __name__ == "__main__":
    print(lottie_en())
    for emp in ("amazon", "discord", "akamai"):
        pt = json.loads((AQUI / "reels" / emp / "content.pt.json").read_text(encoding="utf-8"))
        en = traduz(pt)
        en["locale"] = "en"
        (AQUI / "reels" / emp / "content.en.json").write_text(
            json.dumps(en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        pasta = RAIZ / "data" / "episodes" / f"reel-consistent-hashing-{emp}-en"
        (pasta / "voice").mkdir(parents=True, exist_ok=True)
        orig = json.loads(
            (RAIZ / "data" / "episodes" / f"reel-consistent-hashing-{emp}-pt" / "narracao.json").read_text(
                encoding="utf-8"
            )
        )
        linhas = []
        for lp, txt in zip(orig["lines"], NARRACAO_EN[emp], strict=True):
            d = {"scene": lp["scene"], "text": txt}
            if "delivery" in lp:
                d["delivery"] = lp["delivery"]
            linhas.append(d)
        (pasta / "narracao.json").write_text(
            json.dumps({"language": "en", "lines": linhas}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (pasta / "content.json").write_text(
            json.dumps(en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (pasta / "traducao.json").write_text(
            json.dumps(
                {
                    "derived_from": f"reel-consistent-hashing-{emp}-pt",
                    "language": "en",
                    "source_language": "pt-BR",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (pasta / "voice" / "glossary.json").write_text(
            json.dumps(
                {"termos": [{"escrita": e, "fala": f} for e, f in GLOSSARIO_EN]}, ensure_ascii=False, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
        (pasta / "medicao.json").write_text(
            json.dumps(m.MEDICAO[emp](), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(pasta)
