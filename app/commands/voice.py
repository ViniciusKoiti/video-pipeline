"""`vp voice`: a narração de cada cena do `scenes.json` -> `voice/<cena>-<provedor>-<hash>.wav`.

- A voz dos rascunhos é a `tts` do `providers.toml` (Kokoro); com `--voz-final`, a do vídeo final
  (`tts_final`: a voz clonada do dono, ADR 016); com `--voz NOME`, uma voz registrada pelo nome, fora da
  escolha do `providers.toml`: `gemini` (Charon, ADR 012; é a do vídeo-régua), `chatterbox`,
  `chatterbox_modal` (a mesma voz numa GPU do Modal, ADR 024), `azure_speech` (voz neural pronta do Azure,
  ADR 058) ou `kokoro`.
- O hash do nome cobre o texto falado, o modelo, a voz e a direção de fala: a fala só é gerada de novo
  quando um deles muda, e uma voz não apaga as falas da outra. Cota esgotada: o comando para, as falas já
  geradas ficam e a próxima execução continua (`vp status` lista o que ficou para trás).
- A voz clonada gera uma cena por vez, dezenas de vezes mais devagar que o tempo real; o Gemini gera as
  cenas que faltam em lotes. O glossário `voice/glossary.json` (opcional) troca a grafia só no texto
  enviado à voz.
- `--conferir` ouve a fala pronta com o reconhecedor local e aponta o que foge do roteiro e do glossário,
  com uma folha de escuta dos trechos (ADR 062); sozinho, não gera fala. `--refazer S06 S43` guarda a fala
  atual dessas cenas (nesta voz) em `voice/tomadas-recusadas/` e gera outra tomada.
"""

from __future__ import annotations

import argparse
import os
import time
from datetime import datetime

from app.commands.voice_check import check_speech
from app.media.probe import duration_ms
from app.pipeline.constants.voice_retake_constants import VoiceRetakeConstants as RetakeConstants
from app.pipeline.ports import Context
from app.pipeline.production.voice import produce_voice
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice.retake import set_aside
from app.providers.tts.base import TTSProvider


def select_tts(context: Context, final: bool, named: str | None) -> TTSProvider:
    """`--voz NOME` manda; senão `--voz-final`; senão a voz dos rascunhos."""
    if named:
        return context.tts_named(named)
    return context.tts_final if final else context.tts


def run(args: argparse.Namespace, context: Context) -> int:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # pesos já em cache: a voz local não acessa a rede
    scenes = context.store.read(args.episode_id, "scenes.json", ScenesManifest)
    if not args.conferir or args.refazer or args.voz_final or args.voz:  # `--conferir` sozinho só ouve
        _produce(args, context, scenes)
    return check_speech(context, scenes, args.episode_id) if args.conferir else 0


def _produce(args: argparse.Namespace, context: Context, scenes: ScenesManifest) -> None:
    tts = select_tts(context, args.voz_final, args.voz)
    if args.refazer:
        voice_dir = context.store.path(args.episode_id, "voice")
        known = [scene.id for scene in scenes.scenes]
        moved = set_aside(voice_dir, args.refazer, known, tts.identity, datetime.now().astimezone())
        print(f"tomada anterior guardada: {len(moved)} arquivo(s) em voice/{RetakeConstants.REJECTED_DIR}/")
    started = time.monotonic()
    wavs = produce_voice(
        tts, scenes, context.store, args.episode_id, polish=context.settings.voice_polish.active(),
    )
    total = 0
    for scene in scenes.scenes:
        ms = duration_ms(wavs[scene.id])
        total += ms
        print(f"{scene.id}: {ms / 1000:5.2f} s")
    print(f"voz: {time.monotonic() - started:.0f} s; total {total / 1000:.1f} s")
