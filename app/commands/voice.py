"""`vp voice`: a narração de cada cena do `scenes.json` -> `voice/<cena>-<provedor>-<hash>.wav`.

- A voz dos rascunhos é a `tts` do `providers.toml` (Kokoro); com `--voz-final`, a do vídeo final
  (`tts_final`: a voz clonada do dono, ADR 016); com `--voz NOME`, uma voz registrada pelo nome, fora da
  escolha do `providers.toml`: `gemini` (Charon, ADR 012; é a do vídeo-régua), `chatterbox`,
  `chatterbox_modal` (a mesma voz numa GPU do Modal, ADR 024) ou `kokoro`.
- O hash do nome cobre o texto falado, o modelo, a voz e a direção de fala: a fala só é gerada de novo
  quando um deles muda, e uma voz não apaga as falas da outra. Cota esgotada: o comando para, as falas já
  geradas ficam e a próxima execução continua (`vp status` lista o que ficou para trás).
- A voz clonada gera uma cena por vez, dezenas de vezes mais devagar que o tempo real; o Gemini gera as
  cenas que faltam em lotes. O glossário `voice/glossary.json` (opcional) troca a grafia só no texto
  enviado à voz.
"""

from __future__ import annotations

import argparse
import os
import time

from app.media.probe import duration_ms
from app.pipeline.ports import Context
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice_production import produce_voice
from app.providers.tts.base import TTSProvider


def select_tts(context: Context, final: bool, named: str | None) -> TTSProvider:
    """`--voz NOME` manda; senão `--voz-final`; senão a voz dos rascunhos."""
    if named:
        return context.tts_named(named)
    return context.tts_final if final else context.tts


def run(args: argparse.Namespace, context: Context) -> int:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # pesos já em cache: a voz local não acessa a rede
    scenes = context.store.read(args.episode_id, "scenes.json", ScenesManifest)
    started = time.monotonic()
    wavs = produce_voice(
        select_tts(context, args.voz_final, args.voz), scenes, context.store, args.episode_id
    )
    total = 0
    for scene in scenes.scenes:
        ms = duration_ms(wavs[scene.id])
        total += ms
        print(f"{scene.id}: {ms / 1000:5.2f} s")
    print(f"voz: {time.monotonic() - started:.0f} s; total {total / 1000:.1f} s")
    return 0
