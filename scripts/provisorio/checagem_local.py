"""Mede o prompt de checagem local (prompts/local/checagem.md) num modelo do Ollama (provisório até a #27).

Uso: `.venv/bin/python scripts/provisorio/checagem_local.py <episode-id> --modelo qwen3:4b [--real N]
[--por-tipo N] [--semente S] [--saida ARQUIVO.json]`

- Gabarito: afirmações reais do episódio aprovado (esperado `SUSTENTA`) e mutações mecânicas delas: número
  trocado (`DIVERGE`), trecho de outra fonte (`SEM_SUPORTE`), superlativo acrescentado (`EXAGERO`).
- Só lê o episódio; o relatório vai para `--saida` (padrão `data/cache/checagem-local-<modelo>.json`, fora do
  Git). Recusa rodar com a CPU limitada (sonda acima de 0,3 s): o tempo entra na medição.
- Usa o Ollama configurado em `config/providers.toml`; nenhum provedor remoto.
- Imprime o resumo e os casos para o dono olhar: `SUSTENTA` esperado e negado nas reais (o gabarito pode estar
  errado) e erros que passaram.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap import build_context  # noqa: E402
from app.pipeline.bench import CPU_PROBE_SLOW_S, cpu_probe  # noqa: E402
from app.pipeline.checagem_local import build_cases, load_prompt, run, score  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("episode_id")
    parser.add_argument("--modelo", help="modelo do Ollama (padrão: o de config/providers.toml)")
    parser.add_argument("--real", type=int, default=12, help="afirmações reais (padrão 12)")
    parser.add_argument("--por-tipo", type=int, default=8, help="casos de cada mutação (padrão 8)")
    parser.add_argument("--semente", type=int, default=1)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()

    probe = cpu_probe()
    if probe > CPU_PROBE_SLOW_S:
        raise SystemExit(f"CPU limitada (sonda {probe:.2f} s, limite {CPU_PROBE_SLOW_S} s): feche os apps")
    context = build_context(ROOT)
    episode_dir = context.settings.data_dir / "episodes" / args.episode_id
    cases = build_cases(episode_dir, per_kind=args.por_tipo, real=args.real, seed=args.semente)
    system, template = load_prompt(ROOT)
    model = args.modelo or context.settings.providers.ollama.model
    print(f"{len(cases)} casos · modelo {model} · sonda de CPU {probe:.2f} s", flush=True)

    results = run(context.text, cases, system, template, model=model)
    summary = score(results)
    out = args.saida or ROOT / "data" / "cache" / f"checagem-local-{model.replace(':', '-')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "episodio": args.episode_id,
        "modelo": model,
        "prompt_sha256": hashlib.sha256(f"{system}\n\n{template}".encode()).hexdigest(),
        "sonda_cpu_s": round(probe, 3),
        "resumo": summary,
        "casos": [
            {
                **asdict(r.case),
                "esperado": r.case.expected,
                "veredito": r.verdict,
                "confronto": r.confronto,
                "erro": r.error,
                "segundos": round(r.seconds, 1),
            }
            for r in results
        ],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for r in results:
        if r.case.kind == "real" and r.verdict not in (None, "SUSTENTA"):
            print(f"REAL NEGADA  {r.case.id}: {r.verdict} · {r.confronto}")
        if r.case.kind != "real" and r.verdict == "SUSTENTA":
            print(f"PASSOU       {r.case.id} ({r.case.kind}): {r.confronto}")
    print(f"relatório: {out}")


if __name__ == "__main__":
    main()
