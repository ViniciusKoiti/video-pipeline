"""Tradução de uma narração para outro idioma, em pasta própria, com gate (ADR 034).

A tradução mora em `data/episodes/<id>-<idioma>/`, com um `traducao.json` que aponta para o episódio de
origem. Antes de o dono ver o texto, o código confere o que dá para conferir sem entender a língua: as mesmas
cenas, as mesmas entregas e pausas e **os mesmos números**, na narração (por extenso ou em dígitos) e na tela.
Quem traduz é um agente que escreve só arquivo de dados (ADR 009); aqui só se valida.

Limite conhecido: o "um/uma" e o "one" não entram na conta (são artigo ou pronome com a mesma frequência que
numeral); números de 2 em diante, os dígitos e as escalas (`mil`, `thousand`, `milhão`, `million`) entram, e
dígitos seguidos de escala formam um número só ("100 mil" é 100000; "1 milhão", 1000000).
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from app.media.constants.narration_constants import NarrationConstants
from app.pipeline.constants.translation_constants import TranslationConstants as Constants
from app.pipeline.models.narration import Narration as Narration
from app.pipeline.models.narration_line import NarrationLine as NarrationLine
from app.pipeline.models.translation_link import TranslationLink as TranslationLink
from app.pipeline.ports import ManifestNotFound, ManifestStore

# --- números ditos ---------------------------------------------------------------------------------------


def _digits(token: str, lang: str) -> float | int:
    thousands, decimal = (".", ",") if lang == "pt" else (",", ".")
    if re.fullmatch(rf"\d{{1,3}}(?:\{thousands}\d{{3}})+", token):
        return int(token.replace(thousands, ""))
    value = float(token.replace(thousands, "").replace(decimal, "."))
    return int(value) if value.is_integer() else value


def spoken_numbers(text: str, language: str) -> list[float | int]:
    """Os números do texto na ordem em que aparecem, por extenso ou em dígitos (`language`: `pt-BR`, `en`)."""
    lang = language.lower().split("-")[0]
    values, scales, connectors, _ = Constants._LEXICONS.get(lang, Constants._LEXICONS["en"])
    tokens = [t.lower() for t in Constants._WORD.findall(text.replace(NarrationConstants.PAUSE_TAG, " "))]
    found: list[float | int] = []
    total: float = 0
    current: float = 0
    active = False
    for i, token in enumerate(tokens):
        if token[0].isdigit():  # dígitos entram na conta como uma palavra-número: "100 mil" é 100000
            if active:
                found.append(total + current)
                total = current = 0
            current = _digits(token, lang)
            active = True
            continue
        is_scale = token in scales
        is_value = token in values or (lang == "en" and token == Constants._EN_HUNDRED)
        if is_value or is_scale:
            active = True
            if is_scale:
                total += (current or 1) * scales[token]
                current = 0
            elif lang == "en" and token == Constants._EN_HUNDRED:
                current = (current or 1) * 100
            else:
                current += values[token]
            continue
        keeps_going = token in connectors and active and i + 1 < len(tokens) and (
            tokens[i + 1] in values or tokens[i + 1] in scales or tokens[i + 1] == Constants._EN_HUNDRED
        )
        if keeps_going:
            continue
        if active:
            found.append(total + current)
            total = current = 0
            active = False
    if active:
        found.append(total + current)
    return found


def _numeric_leaves(node: Any) -> list[float | int]:
    if isinstance(node, bool):
        return []
    if isinstance(node, int | float):
        return [node]
    if isinstance(node, dict):
        return [n for value in node.values() for n in _numeric_leaves(value)]
    if isinstance(node, list):
        return [n for value in node for n in _numeric_leaves(value)]
    return []


# --- conferência -----------------------------------------------------------------------------------------


def narration_problems(source: Narration, target: Narration) -> list[str]:
    """O que a tradução trocou e não devia: línguas, cenas, entregas, pausas e números de cada fala."""
    problems: list[str] = []
    if source.language == target.language:
        problems.append(f"o idioma da tradução é o mesmo do original ({target.language})")
    if len(source.lines) != len(target.lines):
        problems.append(f"{len(target.lines)} fala(s) na tradução, {len(source.lines)} no original")
    for index, (src, dst) in enumerate(zip(source.lines, target.lines, strict=False), start=1):
        name = src.scene or f"fala {index}"
        if src.scene != dst.scene:
            problems.append(f"{name}: a cena é '{dst.scene}' na tradução")
        if src.delivery != dst.delivery:
            problems.append(f"{name}: entrega '{dst.delivery}' na tradução, '{src.delivery}' no original")
        if src.text.count(NarrationConstants.PAUSE_TAG) != dst.text.count(NarrationConstants.PAUSE_TAG):
            problems.append(f"{name}: o número de pausas mudou")
        if not dst.text.strip():
            problems.append(f"{name}: fala vazia na tradução")
        expected = sorted(spoken_numbers(src.text, source.language))
        got = sorted(spoken_numbers(dst.text, target.language))
        if expected != got:
            problems.append(f"{name}: números ditos {got} na tradução, {expected} no original")
    return problems


def content_problems(source: dict[str, Any], target: dict[str, Any]) -> list[str]:
    """Na tela: as mesmas cenas, nos mesmos tipos, com os mesmos valores numéricos."""
    problems: list[str] = []
    src_scenes, dst_scenes = source.get("scenes", []), target.get("scenes", [])
    shape = [(s.get("id"), s.get("type")) for s in src_scenes]
    if shape != [(s.get("id"), s.get("type")) for s in dst_scenes]:
        problems.append("as cenas do vídeo (id e tipo) mudaram na tradução")
    if _numeric_leaves(source) != _numeric_leaves(target):
        problems.append("os números do vídeo por JSON mudaram na tradução")
    return problems


def translation_problems(store: ManifestStore, episode_id: str) -> list[str]:
    """Tudo o que a conferência em código acha numa tradução; vazio = o dono pode ler o texto."""
    try:
        link = store.read(episode_id, Constants.LINK_FILE, TranslationLink)
        target = store.read(episode_id, Constants.NARRATION_FILE, Narration)
        source = store.read(link.derived_from, Constants.NARRATION_FILE, Narration)
    except ManifestNotFound as error:
        return [f"falta arquivo para conferir a tradução ({error})"]
    except ValueError as error:
        return [f"arquivo inválido ({error})"]
    problems = narration_problems(source, target)
    if link.language != target.language or link.source_language != source.language:
        problems.append("traducao.json não bate com o idioma das duas narrações")
    src_content = store.path(link.derived_from, Constants.CONTENT_FILE)
    dst_content = store.path(episode_id, Constants.CONTENT_FILE)
    if src_content.is_file() and dst_content.is_file():
        problems += content_problems(
            json.loads(src_content.read_text(encoding="utf-8")),
            json.loads(dst_content.read_text(encoding="utf-8")),
        )
    elif src_content.is_file() != dst_content.is_file():
        problems.append("só um dos dois episódios tem content.json")
    return problems


def translation_hash(store: ManifestStore, episode_id: str) -> str:
    """O que o gate de tradução carimba: a tradução, o vínculo e o original de que ela vem.

    Mudar a narração (ou a tela) do original derruba a aprovação da tradução (§5)."""
    link = store.read(episode_id, Constants.LINK_FILE, TranslationLink)
    own = (Constants.NARRATION_FILE, Constants.LINK_FILE, Constants.CONTENT_FILE)
    origin = (Constants.NARRATION_FILE, Constants.CONTENT_FILE)
    labelled = [(f"{episode_id}/{n}", store.path(episode_id, n)) for n in own]
    labelled += [(f"{link.derived_from}/{n}", store.path(link.derived_from, n)) for n in origin]
    digest = hashlib.sha256()
    for label, path in labelled:
        if path.is_file():
            digest.update(label.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return "sha256:" + digest.hexdigest()
