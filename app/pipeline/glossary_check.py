"""Trava fonética no `vp check` (CLAUDE.md §6; ADR 062, etapa seguinte).

Todo termo de fora presente na narração em português precisa de entrada em `voice/glossary.json` antes da voz
final. Aqui se acham candidatos por traço: sigla ("CVV"), letra ou encontro que o português quase não usa
("Thorfinn", "Empty", "Oath"), letra dobrada, ou fim de palavra que o português não tem ("Vinland"). Nome de
fora sem nenhum desses traços ("Einar") escapa: a conferência depois da voz (`vp voice --conferir`) pega.
Ficam de fora letra solta, ordinal, aspas simples, palavra em CAIXA ALTA que o roteiro também escreve em
minúscula (ênfase) e as poucas palavras do português com um desses traços ("sob", "pizza").
Com a voz final do Azure, cada termo precisa também de `ipa`, porque só o fonema é garantido nela.
"""

from __future__ import annotations

import re

from app.media.narration import strip_pauses
from app.media.pronunciation import Glossary
from app.pipeline.constants.glossary_check_constants import GlossaryCheckConstants as Constants
from app.pipeline.schemas import ScenesManifest


def _looks_foreign(word: str) -> bool:
    if re.match(Constants.ACRONYM, word):
        return True
    lower = word.lower()
    if any(re.search(pattern, lower) for pattern in Constants.FOREIGN_PATTERNS):
        return True
    return lower[-1] not in Constants.NATIVE_FINALS and not lower[-1].isdigit()


def _covered(glossary: Glossary) -> set[str]:
    return {word.lower() for term in glossary.termos for word in re.findall(r"\w+", term.escrita)}


def _words(scenes: ScenesManifest) -> list[str]:
    """As palavras da narração, sem aspas simples coladas ("'bom'"), ordinal ("1º") nem letra solta
    ("opção C")."""
    words = [w for scene in scenes.scenes for w in re.findall(Constants.WORD, strip_pauses(scene.narration))]
    return [word for word in words if len(word) > 1]


def missing_terms(scenes: ScenesManifest, glossary: Glossary) -> list[str]:
    """Os candidatos a termo de fora que nenhuma entrada do glossário cobre, na ordem em que aparecem."""
    if scenes.language != Constants.LANGUAGE:
        return []
    words = _words(scenes)
    lowercase = {word for word in words if word.islower()}
    covered, found = _covered(glossary), dict[str, None]()
    for word in words:
        lower = word.lower()
        emphasis = word.isupper() and lower in lowercase  # "SIM" com "sim" no roteiro é ênfase, não sigla
        if lower in covered or lower in Constants.NATIVE_WORDS:
            continue
        if _looks_foreign(lower if emphasis else word):
            found.setdefault(word)
    return list(found)


def glossary_attention(scenes: ScenesManifest, glossary: Glossary, final_voice: str | None) -> list[str]:
    lines = []
    missing = missing_terms(scenes, glossary)
    if missing:
        lines.append(
            f"glossário: {len(missing)} termo(s) de fora sem entrada em voice/glossary.json: "
            f"{', '.join(missing)} (antes da voz final; CLAUDE.md §6)"
        )
    if final_voice in Constants.VOICES_WITH_IPA:
        words = [term for term in glossary.termos if re.search(r"[^\W\d_]", term.escrita)]  # número não
        without = [term.escrita for term in words if not term.ipa]
        if without:
            lines.append(f"glossário: a voz final ({final_voice}) só garante o fonema; falta `ipa` em: "
                         f"{', '.join(without)}")
    return lines


def colon_pause_warnings(scenes: ScenesManifest) -> list[str]:
    """Dois-pontos que abrem pergunta ou fala interna sem `<short pause>` logo depois."""
    return [
        f"{scene.id}: dois-pontos antes de pergunta sem `<short pause>` depois deles; a voz tende a colar "
        "as palavras (CLAUDE.md §6)"
        for scene in scenes.scenes
        if re.search(Constants.COLON_QUESTION, scene.narration)
    ]
