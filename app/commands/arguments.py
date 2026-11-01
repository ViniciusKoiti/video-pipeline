"""Argumentos dos comandos de vp; separados dos handlers e do catálogo de comandos."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.pipeline.constants.gates_constants import GatesConstants
from app.pipeline.models.episode_format import EpisodeFormat


def _bench_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--models", help="modelos de texto separados por vírgula (padrão: o configurado)")
    parser.add_argument("--runs", type=int, default=2, help="execuções por modelo (padrão: 2)")
    parser.add_argument("--skip-llm", action="store_true", help="não medir o LLM")
    parser.add_argument("--skip-tts", action="store_true", help="não medir o TTS")
    parser.add_argument(
        "--render", type=Path, metavar="DIR", help="pasta de episódio para medir o motor de render"
    )

def _new_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--topic", required=True, help="tema do episódio")
    parser.add_argument(
        "--format",
        choices=[f.value for f in EpisodeFormat],
        default=EpisodeFormat.ARCHIVAL_DOCUMENTARY.value,
        help="formato do episódio; decide o motor de render (ADR 001)",
    )

def _voice_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--voz-final", action="store_true", help="a voz do vídeo final (tts_final, ADR 016)")
    names = "gemini, chatterbox, chatterbox_modal, kokoro"
    parser.add_argument("--voz", metavar="NOME", help=f"voz registrada pelo nome: {names}")


def _render_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preview", action="store_true", help="prévia em 720p")
    parser.add_argument("--no-render", action="store_true", help="confere a montagem e grava o episode.json")
    parser.add_argument(
        "--legenda-palavra", action="store_true", help="legenda palavra a palavra (Whisper remoto)"
    )
    _voice_arguments(parser)

def _decision_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--step",
        required=True,
        choices=[s.value for s in GatesConstants.GATED_STEPS],
        help="gate: sources (fontes e fichas), script (roteiro), assets (um ativo, com --asset), translation "
        "(pasta de tradução, ADR 034) ou preview (o render mais acabado, com legenda e texto do post)",
    )
    parser.add_argument("--asset", help="id do ativo, na etapa assets")
    parser.add_argument("--reviewer", help="quem decide (padrão: VP_REVIEWER, senão git config user.name)")

def _reopen_arguments(parser: argparse.ArgumentParser) -> None:
    _decision_arguments(parser)
    parser.add_argument("--reason", required=True, help="motivo, registrado no review.json")

def _approve_arguments(parser: argparse.ArgumentParser) -> None:
    _decision_arguments(parser)
    parser.add_argument("--notes", default="", help="observação registrada no review.json")
    parser.add_argument(
        "--sem-checagem",
        dest="skip_check",
        metavar="MOTIVO",
        help="aprova o gate 2 sem parecer do verificador; o motivo vai para o review.json",
    )

def _checagem_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("parecer", type=Path, help='JSON com "verdict" (approved | rejected) e "problems"')
    parser.add_argument("--reviewer", default="verificador", help="quem conferiu (padrão: verificador)")

def _reject_arguments(parser: argparse.ArgumentParser) -> None:
    _decision_arguments(parser)
    parser.add_argument("--reason", required=True, help="motivo, registrado no review.json")
    parser.add_argument("--changes", action="store_true", help="mudanças pedidas em vez de reprovação")

def _numeros_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--escrever", action="store_true", help="grava o bloco no outline.md e regrava o plano-imagens.md"
    )
    parser.add_argument(
        "--used-in-scenes",
        dest="used_in_scenes",
        action="store_true",
        help="acerta o used_in_scenes dos ativos ainda não aprovados (ativo aprovado não muda, §2.6)",
    )
