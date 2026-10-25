"""Comandos offline para o registro SQLite de consumo e orçamento editorial."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from app.bootstrap import build_usage
from app.pipeline.ports import Context
from app.pipeline.usage import AgentRun, UsageBudget, UsageError, UsageRequest


def _scope(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("episode_id", help="episódio ao qual o consumo pertence")
    parser.add_argument("--project", default="auto-play", help="projeto (padrão: auto-play)")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="usage_command", required=True)
    commands.add_parser("init", help="cria o banco local, sem coletar nem chamar modelos")
    budget = commands.add_parser("budget", help="define ou atualiza um teto por episódio e modelo")
    _scope(budget)
    budget.add_argument("--id", required=True, help="id estável do orçamento")
    budget.add_argument("--metric", choices=["tokens_total", "cost_usd_micros"], required=True)
    budget.add_argument("--limit", type=int, required=True, help="teto na unidade da métrica")
    budget.add_argument("--model", default="*", help="id exato do modelo; padrão: todos")
    start = commands.add_parser("start", help="registra uma execução; não inicia o Claude Code")
    _scope(start)
    start.add_argument("--id", help="id da execução (padrão: UUID)")
    start.add_argument("--stage", required=True)
    start.add_argument("--agent", required=True)
    start.add_argument("--session", help="id da sessão de origem")
    start.add_argument("--parent", help="execução que originou este subagente")
    reserve = commands.add_parser("reserve", help="reserva saldo de todos os tetos em uma transação")
    reserve.add_argument("run_id")
    reserve.add_argument("allocations", type=Path, help="JSON com id do orçamento -> quantidade reservada")
    ingest = commands.add_parser("import", help="importa eventos de uso em JSONL, sem prompts ou respostas")
    ingest.add_argument("run_id")
    ingest.add_argument("events", type=Path, help="eventos normalizados, um objeto JSON por linha")
    finish = commands.add_parser("finish", help="encerra ou marca uma execução para conciliação")
    finish.add_argument("run_id")
    finish.add_argument(
        "--reconciled", action="store_true", help="confirma que todo o consumo desta execução foi importado"
    )
    _scope(commands.add_parser("report", help="consumo, reservas e saldo do episódio em JSON"))


def report_error(message: str) -> int:
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    return 1


def run(args: argparse.Namespace, context: Context) -> int:
    try:
        ledger = build_usage(context.settings)
        match args.usage_command:
            case "init":
                result = {"database": str(ledger.path), "schema_version": 1}
            case "budget":
                budget = UsageBudget(
                    id=args.id,
                    project=args.project,
                    episode_id=args.episode_id,
                    model_filter=args.model,
                    metric=args.metric,
                    limit_value=args.limit,
                )
                ledger.set_budget(budget)
                result = budget.model_dump()
            case "start":
                execution = AgentRun(
                    id=args.id or uuid4().hex,
                    project=args.project,
                    episode_id=args.episode_id,
                    stage=args.stage,
                    agent_name=args.agent,
                    session_id=args.session,
                    parent_run_id=args.parent,
                )
                ledger.create_run(execution)
                result = execution.model_dump()
            case "reserve":
                allocations = json.loads(args.allocations.read_text(encoding="utf-8"))
                if not isinstance(allocations, dict):
                    raise UsageError("Reservas precisam ser um objeto JSON: id do orçamento -> quantidade.")
                ledger.reserve(args.run_id, allocations)
                result = {"run_id": args.run_id, "reserved": allocations}
            case "import":
                events = [
                    UsageRequest.model_validate_json(line)
                    for line in args.events.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                result = {"run_id": args.run_id, **ledger.record(args.run_id, events)}
            case "finish":
                result = {
                    "run_id": args.run_id,
                    "status": ledger.finish(args.run_id, reconciled=args.reconciled),
                }
            case "report":
                result = ledger.report(args.project, args.episode_id)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ValidationError:
        error = "Metadados inválidos: confira ids, fuso horário e contadores inteiros não negativos."
    except UsageError as exc:
        error = str(exc)
    except (json.JSONDecodeError, UnicodeError):
        error = "O arquivo precisa conter JSON válido no formato documentado em docs/usage.md."
    except OSError:
        error = "Não foi possível abrir o banco ou o arquivo de metadados."
    except sqlite3.Error:
        error = "Falha no banco de consumo; confira integridade, permissões ou bloqueio por outro processo."
    return report_error(error)
