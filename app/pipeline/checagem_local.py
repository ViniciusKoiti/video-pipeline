"""Checagem local (ADR 009, #27): uma afirmação do roteiro contra o trecho que ela cita, num modelo pequeno.

O prompt mora em `prompts/local/checagem.md`. Este módulo carrega o prompt, monta o gabarito de um episódio
aprovado (afirmações reais mais mutações mecânicas) e pontua os vereditos. Fala só com a porta de texto.
O veredito é alerta para a revisão humana; quem aprova é o dono (§2.5).
"""

from __future__ import annotations

import json
import random
import re
import statistics
import time
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field

from app.pipeline.excerpts import excerpts_of
from app.pipeline.schemas import Model, ScenesManifest, SourcesManifest
from app.providers.errors import ProviderError
from app.providers.text.base import TextProvider, TextRequest

Rotulo = Literal["SUSTENTA", "DIVERGE", "SEM_SUPORTE", "EXAGERO"]
KINDS = ("real", "numero", "trecho_alheio", "superlativo")
EXPECTED: dict[str, Rotulo] = {
    "real": "SUSTENTA",
    "numero": "DIVERGE",
    "trecho_alheio": "SEM_SUPORTE",
    "superlativo": "EXAGERO",
}
PROMPT_FILE = Path("prompts/local/checagem.md")
_FICHA = re.compile(r"\s*\(F\d+(?:[,;]\s*F\d+)*\)")
_NUMBER = re.compile(r"\d[\d.]*")
_WORD = re.compile(r"\w{5,}")
SUPERLATIVE = " Foi o maior de todo o país."


class Veredito(Model):
    """`confronto` vem antes: o modelo escreve a comparação e só depois decide."""

    confronto: str = Field(min_length=1, pattern=r"\S")
    veredito: Rotulo


@dataclass(frozen=True)
class Case:
    id: str
    kind: str
    claim: str
    excerpt_ids: tuple[str, ...]
    excerpt: str

    @property
    def expected(self) -> Rotulo:
        return EXPECTED[self.kind]


@dataclass(frozen=True)
class Result:
    case: Case
    verdict: Rotulo | None  # None = o modelo não devolveu JSON válido
    confronto: str
    error: str
    seconds: float


def load_prompt(root: Path) -> tuple[str, str]:
    """(sistema, modelo do usuário) das seções `## Sistema` e `## Usuário` do arquivo de prompt."""
    text = (root / PROMPT_FILE).read_text(encoding="utf-8")
    found = re.finditer(r"^## (\S+)\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    sections = {m.group(1): m.group(2).strip() for m in found}
    return sections["Sistema"], sections["Usuário"]


def render(template: str, case: Case) -> str:
    # Uma substituição: placeholders e quebras de linha das fontes continuam dados literais.
    data = json.dumps(
        {"afirmacao": case.claim, "excerpt_ids": case.excerpt_ids, "trecho": case.excerpt},
        ensure_ascii=False,
    )
    return template.replace("{{dados}}", data)


def clean_claim(text: str) -> str:
    """Tira o id da ficha ("(F54)"): o modelo confere o texto, não a ficha."""
    return _FICHA.sub("", text).strip()


def _claims(scenes: ScenesManifest) -> Iterable[tuple[str, list[str], str]]:
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for scene in scenes.scenes:
        found = list(scene.claims)
        for shot in scene.shots:
            found.extend(getattr(shot, "claims", []))
        for claim in found:
            key = (claim.text, tuple(claim.excerpt_ids))
            if claim.excerpt_ids and key not in seen:
                seen.add(key)
                yield scene.id, claim.excerpt_ids, clean_claim(claim.text)


def _mutate_number(claim: str, excerpt: str, rng: random.Random) -> str | None:
    """Troca o primeiro algarismo da afirmação que também está no trecho por outro que o trecho não traz."""
    for match in _NUMBER.finditer(claim):
        token = match.group().rstrip(".")
        if token not in excerpt or not token.replace(".", "").isdigit():
            continue
        value = int(token.replace(".", ""))
        for candidate in (value + 7, value * 2, value * 3, value + 11):
            if str(candidate) not in excerpt and candidate != value:
                return claim[: match.start()] + str(candidate) + claim[match.start() + len(token) :]
    return None


def _overlap(a: str, b: str) -> float:
    words_a, words_b = set(_WORD.findall(a.lower())), set(_WORD.findall(b.lower()))
    return len(words_a & words_b) / max(1, min(len(words_a), len(words_b)))


def _case(scene_id: str, kind: str, claim: str, ids: list[str], excerpt: str) -> Case:
    return Case(f"{scene_id}:{ids[0]}:{kind}", kind, claim, tuple(ids), excerpt)


def build_cases(
    episode_dir: Path, *, per_kind: int = 8, real: int = 12, seed: int = 1
) -> list[Case]:
    """Afirmações reais do episódio (gabarito `SUSTENTA`: passaram pela checagem e pelos gates) e mutações
    mecânicas delas (gabarito do tipo). Determinístico para a mesma semente."""
    rng = random.Random(seed)
    sources = SourcesManifest.model_validate_json((episode_dir / "sources.json").read_text(encoding="utf-8"))
    pool: dict[str, str] = {}
    for source in sources.sources:
        pool.update(excerpts_of(source, (episode_dir / source.local_path).read_text(encoding="utf-8")))
    scenes = ScenesManifest.model_validate_json((episode_dir / "scenes.json").read_text(encoding="utf-8"))
    base = [
        (scene_id, ids, claim, " ".join(pool[i] for i in ids))
        for scene_id, ids, claim in _claims(scenes)
        if all(i in pool for i in ids)
    ]
    rng.shuffle(base)
    cases: list[Case] = []
    for scene_id, ids, claim, excerpt in base[:real]:
        cases.append(_case(scene_id, "real", claim, ids, excerpt))
    counts: dict[str, int] = defaultdict(int)
    for scene_id, ids, claim, excerpt in base:
        number = _mutate_number(claim, excerpt, rng)
        if number and counts["numero"] < per_kind:
            counts["numero"] += 1
            cases.append(_case(scene_id, "numero", number, ids, excerpt))
        if "maior" not in excerpt.lower() and counts["superlativo"] < per_kind:
            counts["superlativo"] += 1
            stretched = claim.rstrip(" .") + "." + SUPERLATIVE
            cases.append(_case(scene_id, "superlativo", stretched, ids, excerpt))
        if counts["trecho_alheio"] < per_kind:
            other = [(i, t) for i, t in pool.items() if i.split("#")[0] not in {x.split("#")[0] for x in ids}
                     and len(t) >= 200 and _overlap(claim, t) < 0.05]
            if other:
                other_id, other_text = rng.choice(other)
                counts["trecho_alheio"] += 1
                cases.append(_case(scene_id, "trecho_alheio", claim, [other_id], other_text))
    return cases


def run(
    provider: TextProvider,
    cases: Iterable[Case],
    system: str,
    template: str,
    *,
    model: str | None = None,
    tick: Callable[[], float] = time.monotonic,
) -> list[Result]:
    """Uma chamada por caso, temperatura 0. Falha do modelo num caso não para os outros (§2.1)."""
    results: list[Result] = []
    for case in cases:
        started = tick()
        try:
            answer = provider.generate_json(
                TextRequest(prompt=render(template, case), output=Veredito, system=system, model=model)
            )
            results.append(Result(case, answer.data.veredito, answer.data.confronto, "", tick() - started))
        except ProviderError as error:
            results.append(Result(case, None, "", str(error), tick() - started))
    return results


def score(results: list[Result]) -> dict[str, object]:
    """Alarme falso nas reais, erros pegos nas mutações e acerto do rótulo por tipo."""
    real = [r for r in results if r.case.kind == "real"]
    broken = [r for r in results if r.case.kind != "real"]
    by_kind: dict[str, dict[str, float]] = {}
    for kind in KINDS:
        group = [r for r in results if r.case.kind == kind]
        if group:
            by_kind[kind] = {
                "casos": len(group),
                "rotulo_certo": sum(r.verdict == r.case.expected for r in group) / len(group),
                "sem_json_valido": sum(r.verdict is None for r in group) / len(group),
            }
    return {
        "casos": len(results),
        "alarme_falso": sum(r.verdict not in (None, "SUSTENTA") for r in real) / len(real) if real else None,
        "erros_pegos": sum(r.verdict not in (None, "SUSTENTA") for r in broken) / len(broken)
        if broken
        else None,
        "erro_deixado_passar": sum(r.verdict == "SUSTENTA" for r in broken) / len(broken) if broken else None,
        "por_tipo": by_kind,
        "segundos_mediana": statistics.median(r.seconds for r in results) if results else None,
    }
