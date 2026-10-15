"""Argumentos, execução e respostas JSON dos comandos Postiz."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.bootstrap import ConfigurationError, build_postiz
from app.commands import postiz_cadeia
from app.pipeline.ports import Context
from app.providers.errors import ProviderError


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="postiz_command", required=True)
    commands.add_parser("integrations", help="lista os canais conectados")
    posts = commands.add_parser("posts", help="lista posts no intervalo informado")
    posts.add_argument("--start", required=True, help="início ISO 8601 com fuso horário")
    posts.add_argument("--end", required=True, help="fim ISO 8601 com fuso horário")
    connect = commands.add_parser("connect", help="obtém o link de conexão do canal")
    connect.add_argument("provider", choices=["instagram-standalone"])
    settings = commands.add_parser("settings", help="consulta as opções de publicação do canal")
    settings.add_argument("integration_id")
    upload = commands.add_parser("upload", help="envia um arquivo de mídia ao Postiz")
    upload.add_argument("file", type=Path)
    package = commands.add_parser(
        "pacote", help="confere o agendamento sem criar nada e grava o pacote de decisão para o dono"
    )
    package.add_argument("payload", type=Path)
    package.add_argument("--episode", help="episódio cujo gate 4 (prévia) precisa estar aprovado")
    schedule = commands.add_parser(
        "schedule", help="agenda o JSON nativo do Postiz que já tem pacote; pede a confirmação do dono"
    )
    schedule.add_argument("payload", type=Path)


def report_error(message: str) -> int:
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    return 1


def run(args: argparse.Namespace, context: Context) -> int:
    try:
        client = build_postiz(context.settings)
        match args.postiz_command:
            case "integrations":
                result = client.integrations()
            case "posts":
                result = client.posts(args.start, args.end)
            case "connect":
                result = client.connect(args.provider)
            case "settings":
                result = client.integration_settings(args.integration_id)
            case "upload":
                digest = postiz_cadeia.file_sha256(args.file)  # antes do envio: o registro não falha depois
                result = client.upload(args.file)
                postiz_cadeia.record_upload(context, args.file, digest, result)
            case "pacote":
                payload = json.loads(args.payload.read_text(encoding="utf-8"))
                result = postiz_cadeia.package(context, client, payload, args.episode)
            case "schedule":
                payload = json.loads(args.payload.read_text(encoding="utf-8"))
                result = postiz_cadeia.schedule(context, client, payload)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ConfigurationError:
        error = "Configure POSTIZ_API_KEY e POSTIZ_API_URL no .env."
    except (ProviderError, postiz_cadeia.ChainError) as exc:
        error = str(exc)
    except json.JSONDecodeError:
        error = "O arquivo de agendamento precisa conter JSON válido."
    except OSError:
        error = "Não foi possível ler o arquivo informado."
    except ValueError:
        error = "Argumentos ou payload de agendamento inválidos."
    return report_error(error)
