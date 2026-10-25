"""Molde do nicho como entrada de FORMA do roteiro longo (ADR 031, partes B e D).

A skill `analise-de-formato` resume a amostra do nicho em `molde.json` (mediana, quartis e n de cada medida,
prevalência de cada traço, curvas por décimo) e a `partitura.py` copia a versão datada para a pasta do
episódio, junto da `partitura.md` que o roteirista lê. Aqui a cópia é lida e comparada com o roteiro: só
alertas, só do que dá para medir no texto, e nunca fonte de fato (§2.2). O que depende de ouvir ou ver o vídeo
fica para a prévia e a revisão humana.
"""

from __future__ import annotations

import re
import statistics
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.schemas import OVERLAY_SHOT_KINDS, Scene, ScenesManifest, effective_shots
from app.pipeline.shots import shot_bounds

MOLDE_FILE = "molde.json"
PARTITURA_FILE = "partitura.md"
OPENING_S = 60.0  # a abertura que o molde mede em `cortes_60s` e `voce_60s`
DURATION_TOLERANCE = 0.2  # a duração estimada pode ficar 20% longe da que a partitura pede
CUT_RATIO = 2.0  # planos por minuto acima do dobro do molde viram alerta
CLOSING_RISE = 1.3  # o molde "sobe" uma palavra no fecho quando o último décimo tem 30% a mais que o corpo
MIN_VIDEOS = 8  # abaixo disso o molde é descrição, e o alerta diz isso
STATEMENT_MIN_WORDS = 6  # frase curta sem claims (ponte, pergunta retórica) não é afirmação de fato
TITLE_MIN_LETTERS = 4  # palavra de conteúdo do título: 4 letras ou mais, fora de TITLE_STOP
# A mesma lista de `STOP_TITULO` em `.agents/skills/analise-de-formato/molde.py`: o molde mede o nicho com
# ela e o check mede o roteiro com ela (um teste confere que as duas são iguais).
TITLE_STOP = frozenset({
    "como", "para", "pelo", "pela", "pelos", "pelas", "você", "voce", "vocês", "voces", "isso", "isto",
    "esse", "essa", "este", "esta", "aquele", "aquela", "mais", "menos", "muito", "tudo", "nada", "quando",
    "onde", "porque", "então", "ainda", "sobre", "entre", "até", "depois", "antes", "mesmo", "cada", "sempre",
    "nunca", "quem", "qual", "quais", "coisa", "coisas", "vídeo", "video", "parte", "episódio", "episodio",
    "minutos", "pode", "podem", "deve", "devem", "está", "estão", "foram", "sendo", "tinha", "teria", "fazer",
    "ouvir", "enquanto", "outra", "outro", "outras", "outros", "também", "assim", "aqui", "agora", "hoje",
    "anos", "todo", "toda", "todos", "todas", "primeiro", "primeira", "deveria", "devia", "deviam", "estava",
    "estavam", "gente", "certo", "certa", "nosso", "nossa", "ninguém", "ninguem", "alguém", "alguem",
})

_VOCE = re.compile(r"\bvoc[êe]s?\b", re.IGNORECASE)
_EU = re.compile(r"\beu\b", re.IGNORECASE)
_CONFISSAO = re.compile(
    r"\beu (vou )?(admitir|admito|confesso|confessar)\b|\beu (acreditei|achava|errei|errava)\b"
    r"|\bvergonha\b|\beu (ia|tinha) (come[çc]ar|escrito)\b|\bestava escrito aqui\b",
    re.IGNORECASE,
)
_SENTENCE_END = re.compile(r"(?<=[.?!…])\s+")
_WORD = re.compile(r"\w+", re.UNICODE)
_FIRST_PERSON = re.compile(r"^(eu\b|pra mim|para mim|acho|na minha|confesso|admito|a meu ver)", re.IGNORECASE)
_STOP = frozenset({
    "a", "o", "e", "de", "do", "da", "que", "em", "um", "uma", "para", "com", "não", "por", "se", "os", "as",
    "no", "na", "é", "mais", "você", "vocês", "ele", "ela", "isso", "esse", "essa", "aqui", "ali", "lá", "já",
    "tá", "pra", "pro", "dos", "das", "ao", "à", "como", "mas", "ou", "também", "muito", "tudo", "nada",
    "ser", "foi", "era", "tem", "tinha", "vai", "vou", "eu", "nós", "gente", "quando", "onde", "porque",
    "então", "ainda", "sobre", "entre", "até", "depois", "antes", "mesmo", "cada", "bem", "só",
})


class _Molde(BaseModel):
    # O contrato é da skill e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True)


class Medida(_Molde):
    mediana: float
    n: int
    q1: float | None = None
    q3: float | None = None
    origem: str = ""


class Traco(_Molde):
    com: int
    n: int
    pct: int
    forca: str  # padrao | indicio
    unidade: str = "videos"


class Casas(_Molde):
    """O que a `partitura.py` pediu para este episódio, gravado na cópia do molde."""

    duracao_min: float
    assunto: str | None = None
    blocos: int | None = None
    abertura_s: float | None = None
    fecho_inicio_s: float | None = None
    confissao_s: float | None = None


class MoldeVideos(_Molde):
    n: int
    com_batidas: int = 0


class Molde(_Molde):
    gerado_em: str
    grupos: list[str] = []
    assunto: str | None = None
    videos: MoldeVideos
    medidas: dict[str, Medida] = {}
    prevalencia: dict[str, Traco] = {}
    curvas: dict[str, Any] = {}  # `decimos`, `n_videos` e uma lista por décimo para cada medida
    episodio: Casas | None = None
    copiado_em: str | None = None

    def curva(self, chave: str) -> list[float | None]:
        valores = self.curvas.get(chave)
        return list(valores) if isinstance(valores, list) else []

    def padrao(self, traco: str) -> Traco | None:
        """O traço, só quando a prevalência o sustenta como padrão."""
        item = self.prevalencia.get(traco)
        return item if item is not None and item.forca == "padrao" else None


def molde_summary(molde: Molde) -> str:
    grupos = ", ".join(molde.grupos) or "todos os grupos"
    line = (
        f"{MOLDE_FILE}: {molde.videos.n} vídeo(s) de {grupos}, {molde.videos.com_batidas} com batidas, "
        f"gerado em {molde.gerado_em}"
    )
    if molde.episodio is not None:
        line += f"; partitura: {molde.episodio.duracao_min:g} min"
        if molde.episodio.blocos:
            line += f", {molde.episodio.blocos} bloco(s)"
    return line


def _timed_scenes(scenes: ScenesManifest, chars_per_second: float) -> list[tuple[Scene, float, float]]:
    """(cena, início, fim) em segundos, estimados pela narração (o tempo real vem do WAV, §9)."""
    timed, cursor = [], 0.0
    for scene in scenes.scenes:
        duration = timeline_length(scene.narration) / chars_per_second
        timed.append((scene, cursor, cursor + duration))
        cursor += duration
    return timed


def _cut_times(timed: list[tuple[Scene, float, float]]) -> list[float]:
    """Instante estimado de cada plano que troca o que está na tela (tarja, número e carimbo vão por cima)."""
    times: list[float] = []
    for scene, start, end in timed:
        planned = effective_shots(scene)
        try:
            bounds = shot_bounds(scene.narration, planned, max(1, round((end - start) * 1000)))
        except ValueError:
            continue  # o `vp check` já acusa a âncora fora de ordem
        times += [
            start + offset / 1000
            for shot, (offset, _) in zip(planned, bounds, strict=True)
            if shot.kind not in OVERLAY_SHOT_KINDS
        ]
    return times


def _content_trigrams(text: str) -> set[tuple[str, str, str]]:
    words = [w.lower() for w in _WORD.findall(text) if w.lower() not in _STOP and len(w) > 2]
    return {tuple(words[i : i + 3]) for i in range(len(words) - 2)}  # type: ignore[misc]


def _text_between(timed: list[tuple[Scene, float, float]], start: float, end: float) -> str:
    return " ".join(strip_pauses(s.narration) for s, a, b in timed if b > start and a < end)


def _rate_per_10min(count: int, seconds: float) -> float:
    return 600 * count / seconds if seconds > 0 else 0.0


def title_words(title: str) -> list[str]:
    """Palavras de conteúdo do título, na ordem e sem repetição: a regra de `assunto_do_titulo` da skill."""
    seen: list[str] = []
    for word in _WORD.findall(title.lower()):
        if len(word) >= TITLE_MIN_LETTERS and word not in TITLE_STOP and word not in seen:
            seen.append(word)
    return seen


def _title_said_at(timed: list[tuple[Scene, float, float]], words: list[str]) -> float | None:
    """Segundo estimado em que a narração já disse metade das palavras de conteúdo do título (ao menos uma),
    na precisão da frase; None se nunca diz. A regra de `titulo_video_dito_em` da skill: uma palavra conta
    quando a fala tem uma palavra que começa por ela ("navio" vale por "navios")."""
    target = max(1, len(words) // 2)
    patterns = [re.compile(r"\b" + re.escape(word)) for word in words]
    spoken = ""
    for scene, start, end in timed:
        text = strip_pauses(scene.narration)
        offset = 0
        for sentence in _SENTENCE_END.split(text):
            offset += len(sentence) + 1
            spoken += " " + sentence.lower()
            if sum(1 for pattern in patterns if pattern.search(spoken)) >= target:
                return start + (end - start) * min(offset, len(text)) / max(1, len(text))
    return None


def _title_warnings(
    scenes: ScenesManifest, molde: Molde, timed: list[tuple[Scene, float, float]], tag: str
) -> list[str]:
    """Título provisório (`title`) contra o molde: tamanho fora de q1–q3 e assunto do título dito tarde."""
    chars = molde.medidas.get("titulo_video_chars")
    said = molde.medidas.get("titulo_video_dito_s")
    said_trait = molde.prevalencia.get("titulo_video_dito")
    if scenes.title is None:
        if chars is not None or said is not None:
            return [f"{tag}: scenes.json sem title; o molde mede o título do vídeo e não há o que comparar"]
        return []
    warnings: list[str] = []
    if chars is not None and chars.q1 is not None and chars.q3 is not None:
        length = len(scenes.title)
        if length < chars.q1 or length > chars.q3:
            warnings.append(
                f"{tag}: título com {length} caracteres; o molde fica {_range(chars, ' caracteres')}"
            )
    words = title_words(scenes.title)
    if words and (said is not None or said_trait is not None):
        at = _title_said_at(timed, words)
        if at is None:
            shown = ", ".join(words[:4])
            prevalence = f"; o molde diz em {said_trait.com} de {said_trait.n} vídeos" if said_trait else ""
            warnings.append(f"{tag}: a narração nunca diz o assunto do título ({shown}){prevalence}")
        elif said is not None and said.q3 is not None and at > said.q3:
            warnings.append(
                f"{tag}: a fala só diz o assunto do título aos ~{at:.0f} s; o molde diz {_range(said, ' s')}"
            )
    return warnings


def _range(item: Medida, unit: str = "") -> str:
    if item.q1 is None or item.q3 is None:
        return f"mediana {item.mediana:g}{unit}, n {item.n}"
    return f"entre {item.q1:g} e {item.q3:g}{unit} (mediana {item.mediana:g}, n {item.n})"


def molde_warnings(scenes: ScenesManifest, molde: Molde, chars_per_second: float) -> list[str]:
    """Onde o roteiro foge do molde, no que o código sabe medir: duração pedida pela partitura, planos por
    minuto na abertura e depois, "você" por mil palavras, "você" e "eu" no fecho, os dois traços que o molde
    sustenta como padrão e uma expressão regular alcança (confissão do narrador, fim que retoma a abertura) e,
    com `title` no scenes.json, o tamanho do título e o segundo em que a fala diz o assunto dele (emenda de
    2026-10-23 da ADR 031). Alertas, nunca erros; o molde mede fala em português."""
    if scenes.language != "pt-BR" or not scenes.scenes:
        return []
    warnings: list[str] = []
    tag = "molde" if molde.videos.n >= MIN_VIDEOS else f"molde ({molde.videos.n} vídeos, só descrição)"
    timed = _timed_scenes(scenes, chars_per_second)
    total_s = timed[-1][2]
    text = _text_between(timed, 0, total_s)
    words = len(_WORD.findall(text))

    casas = molde.episodio
    if casas is not None:
        target = casas.duracao_min * 60
        if abs(total_s - target) > DURATION_TOLERANCE * target:
            warnings.append(
                f"{tag}: duração estimada ~{total_s / 60:.1f} min; a partitura pede {casas.duracao_min:g} min"
            )

    cuts = _cut_times(timed)
    opening = sum(1 for t in cuts if t < OPENING_S)
    if (m60 := molde.medidas.get("cortes_60s")) is not None and m60.q3 is not None and opening > m60.q3:
        warnings.append(
            f"{tag}: abertura com {opening} planos nos primeiros 60 s; o molde corta {_range(m60)}"
        )
    body_minutes = (total_s - OPENING_S) / 60
    body_curve = [v for v in molde.curva("cortes_min")[1:9] if v is not None]
    if body_minutes > 0 and body_curve:
        reference = statistics.median(body_curve)
        rate = sum(1 for t in cuts if t >= OPENING_S) / body_minutes
        if reference > 0 and rate > CUT_RATIO * reference:
            warnings.append(
                f"{tag}: ~{rate:.1f} planos por minuto depois da abertura; o molde troca de imagem "
                f"{reference:g} vez(es) por minuto no corpo"
            )

    if words and (voce := molde.medidas.get("voce_por_mil")) is not None and voce.q1 is not None:
        per_mil = 1000 * len(_VOCE.findall(text)) / words
        if per_mil < voce.q1 or per_mil > voce.q3:
            warnings.append(f'{tag}: "você" {per_mil:.1f} por mil palavras; o molde fica {_range(voce)}')

    decile = total_s / 10
    for chave, pattern, nome in (("voce_por_10min", _VOCE, "você"), ("eu_por_10min", _EU, "eu")):
        curve = molde.curva(chave)
        body_ref = [v for v in curve[1:9] if v is not None]
        if len(curve) < 10 or curve[9] is None or not body_ref or decile <= 0:
            continue
        body_median = statistics.median(body_ref)
        if body_median <= 0 or curve[9] < CLOSING_RISE * body_median:
            continue
        last = len(pattern.findall(_text_between(timed, 9 * decile, total_s)))
        before = len(pattern.findall(_text_between(timed, decile, 9 * decile)))
        ours_last, ours_before = _rate_per_10min(last, decile), _rate_per_10min(before, 8 * decile)
        if ours_last < ours_before or last == 0:
            warnings.append(
                f'{tag}: o molde sobe "{nome}" no fecho ({curve[9]:g} por 10 min contra {body_median:g} no '
                f"corpo); o roteiro tem {ours_last:.0f} no último décimo contra {ours_before:.0f} antes"
            )

    warnings += _title_warnings(scenes, molde, timed, tag)

    if (confissao := molde.padrao("confissao")) is not None and not _CONFISSAO.search(text):
        warnings.append(
            f"{tag}: confissão do narrador em {confissao.com} de {confissao.n} vídeos; nenhuma frase de "
            "confissão no roteiro (eu confesso, eu admito, eu errei, eu achava)"
        )
    if (volta := molde.padrao("fecho_volta")) is not None and total_s > 2 * OPENING_S:
        first = _content_trigrams(_text_between(timed, 0, OPENING_S))
        last_text = _content_trigrams(_text_between(timed, total_s - OPENING_S, total_s))
        if not first & last_text:
            warnings.append(
                f"{tag}: o fim retoma a abertura em {volta.com} de {volta.n} vídeos; o último minuto não "
                "repete nenhuma expressão do primeiro"
            )
    return warnings


def _proper_nouns(scenes: ScenesManifest) -> set[str]:
    """Palavras que aparecem com maiúscula fora do começo da frase: nomes próprios do roteiro."""
    nouns: set[str] = set()
    for scene in scenes.scenes:
        for sentence in _SENTENCE_END.split(strip_pauses(scene.narration)):
            words = _WORD.findall(sentence)
            nouns.update(w.lower() for w in words[1:] if w[:1].isupper() and len(w) > 2)
    return nouns


def claimless_statements(scenes: ScenesManifest) -> list[str]:
    """Frase afirmativa com cara de fato (número ou nome próprio) numa cena sem claims (ADR 031, parte D): o
    verificador reprovou rodadas por isso. Pergunta e frase em primeira pessoa não contam; uma por cena."""
    nouns = _proper_nouns(scenes)
    warnings: list[str] = []
    for scene in scenes.scenes:
        if scene.claims or any(shot.claims for shot in scene.shots):
            continue
        for sentence in _SENTENCE_END.split(strip_pauses(scene.narration).strip()):
            sentence = sentence.strip()
            if not sentence or sentence.endswith("?") or _FIRST_PERSON.match(sentence):
                continue
            words = _WORD.findall(sentence)
            if len(words) < STATEMENT_MIN_WORDS:
                continue
            if any(w.isdigit() for w in words) or any(w.lower() in nouns for w in words):
                warnings.append(f"{scene.id}: frase afirmativa em cena sem claims: {sentence[:80]!r}")
                break
    return warnings
