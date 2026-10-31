"""Cadeia de provas do agendamento (ADR 025, emenda): pacote de decisão, pedido do dono e registro.

O `pacote` monta o que o dono lê antes de dizer "pode" (o quê, evidência, riscos, como desfazer,
recomendação) e grava esse pacote no registro. A `duvida` grava o parecer do agente `duvida-cega`, que leu só
o pacote, sem a conversa. O `schedule` só envia um JSON que tem pacote com recomendação de agendar e, depois
desse pacote, um parecer "segue"; o "pode" em si é a confirmação que o Claude Code pede pela regra `ask` do
`.claude/settings.json`. Envios de mídia, pacotes, pareceres, agendamentos e falhas entram, nessa ordem, no
registro `publicacoes/registro.jsonl` da pasta de dados, que só cresce.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.pipeline.gates import gate_report
from app.pipeline.ports import Context
from app.pipeline.schemas import Decision, Step
from app.providers.errors import ProviderError
from app.providers.postiz_validation import visible_text

REGISTRO = Path("publicacoes/registro.jsonl")
UNDO = (
    "Antes do horário: apagar o post no Postiz (os ids saem no registro e em `vp postiz posts`). "
    "Depois do horário: apagar a publicação na rede; o Postiz não desfaz o que já saiu."
)
FIXED_RISKS = (
    "O Postiz não garante idempotência: se o envio falhar, consultar a fila antes de repetir.",
    "A API não marca conteúdo alterado ou sintético: com voz ou imagem gerada, marcar à mão na rede.",
    "Depois de publicar: conferir no Studio (ERROR no Postiz não prova falha), fixar o primeiro comentário "
    "e marcar o conteúdo alterado, tudo à mão.",
)
Clock = Callable[[], datetime]


def _now() -> datetime:
    return datetime.now(UTC)


def registro_path(context: Context) -> Path:
    return context.settings.data_dir / REGISTRO


def payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def append(path: Path, event: str, fields: dict, now: Clock = _now) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {"at": now().isoformat(timespec="seconds"), "event": event, **fields}
    with path.open("a", encoding="utf-8") as registro:
        registro.write(json.dumps(line, ensure_ascii=False) + "\n")


def read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def record_upload(context: Context, file: Path, sha256: str, media: dict, now: Clock = _now) -> None:
    resolved = file.resolve()
    try:
        shown = str(resolved.relative_to(context.settings.data_dir.resolve().parent))
    except ValueError:
        shown = str(resolved)
    append(
        registro_path(context),
        "upload",
        {"arquivo": shown, "sha256": sha256, "midia": media},
        now,
    )


def gate4(context: Context, episode_id: str | None) -> str:
    """Gate 4 do episódio: "aprovado", "não aprovado", "mudou depois da aprovação" ou "sem episódio"."""
    if episode_id is None:
        return "sem episódio"
    status = next(s for s in gate_report(context.store, context.review, episode_id) if s.step is Step.PREVIEW)
    if status.entry is None or status.entry.decision is not Decision.APPROVED:
        return "não aprovado"
    return "aprovado" if status.valid else "mudou depois da aprovação"


LINK = re.compile(r"https?://[^\s<>\"')]+")
LINK_TIMEOUT_S = 8
GONE = (404, 410)  # o que um repositório privado ou apagado devolve a quem não está logado

LinkFetch = Callable[[str], "int | None"]


def link_status(url: str) -> int | None:
    """Código HTTP do link (HEAD, depois GET se o HEAD não for aceito); None se não houve resposta."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "vp-postiz-pacote"})
        try:
            with urllib.request.urlopen(request, timeout=LINK_TIMEOUT_S) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if method == "GET" or error.code not in (403, 405, 501):
                return error.code
        except (urllib.error.URLError, TimeoutError, OSError):
            return None
    return None


def caption_links(text: str) -> list[str]:
    """Os links da legenda, sem pontuação final e sem repetição, na ordem em que aparecem."""
    return list(dict.fromkeys(url.rstrip(".,;:!?") for url in LINK.findall(text)))


def link_findings(posts: list[dict], fetch: LinkFetch) -> tuple[list[str], list[str]]:
    """(bloqueios, riscos) dos links das legendas: 404/410 bloqueia; outro erro ou sem resposta é risco."""
    blocking, risks, seen = [], [], {}
    for post in posts:
        for url in caption_links(post["legenda"]):
            if url not in seen:
                seen[url] = fetch(url)
            status = seen[url]
            if status is None:
                risks.append(f"Link da legenda de {post['canal']} sem resposta, não conferido: {url}")
            elif status in GONE:
                blocking.append(f"Link da legenda de {post['canal']} não abre (HTTP {status}): {url}")
            elif status >= 400:
                risks.append(f"Link da legenda de {post['canal']} respondeu HTTP {status}: {url}")
    return blocking, risks


def build_package(
    payload: dict,
    check: dict,
    uploads: list[dict],
    gate: str,
    episode_id: str | None,
    fetch: LinkFetch | None = None,
) -> dict:
    by_media = {u["midia"]["id"]: u for u in uploads}
    posts, risks, blocking = [], list(FIXED_RISKS), []
    for post in payload["posts"]:
        integration_id = post["integration"]["id"]
        media = []
        for value in post["value"]:
            for item in value.get("image", []):
                sent = by_media.get(item["id"])
                if sent is None:
                    risks.append(
                        f"Mídia {item['id']} sem envio no registro: o arquivo local não foi conferido."
                    )
                media.append(
                    {
                        "id": item["id"],
                        "arquivo": sent["arquivo"] if sent else None,
                        "sha256": sent["sha256"] if sent else None,
                    }
                )
        posts.append(
            {
                "canal": check["integrations"].get(integration_id, integration_id),
                "canal_id": integration_id,
                "legenda": visible_text(post["value"][0]["content"]),
                "midia": media,
            }
        )
    if fetch is not None:
        link_blocking, link_risks = link_findings(posts, fetch)
        blocking += link_blocking
        risks += link_risks
    if gate == "sem episódio":
        risks.append("Sem episódio informado: o gate 4 não foi conferido pelo código, só pelo dono.")
    elif gate != "aprovado":
        blocking.append(f"Gate 4 do episódio {episode_id}: {gate}.")
    return {
        "o_que": {"data": check["date"], "posts": posts},
        "evidencia": {
            "episodio": episode_id,
            "gate_4": gate,
            "defesas": "data futura, canal ativo, sem duplicata na fila",
        },
        "riscos": blocking + risks,
        "como_desfazer": UNDO,
        "recomendacao": "não agendar: " + " ".join(blocking) if blocking else "agendar, se o dono autorizar",
    }


def package(
    context: Context,
    client: Any,
    payload: dict,
    episode_id: str | None,
    now: Clock = _now,
    fetch: LinkFetch | None = link_status,
) -> dict:
    check = client.check_schedule(payload)
    uploads = [e for e in read(registro_path(context)) if e["event"] == "upload"]
    result = build_package(payload, check, uploads, gate4(context, episode_id), episode_id, fetch)
    result = {"payload": payload_hash(payload), **result}
    append(registro_path(context), "pacote", result, now)
    return result


class ChainError(ValueError):
    """O agendamento não tem o pacote de decisão ou a dúvida cega exigidos."""


VERDICTS = ("segue", "não segue")
NO_PACKAGE = "sem pacote de decisão para este JSON: rode `vp postiz pacote` e mostre o pacote ao dono"


def _last_package(entries: list[dict], digest: str) -> int:
    for index in range(len(entries) - 1, -1, -1):
        if entries[index]["event"] == "pacote" and entries[index]["payload"] == digest:
            return index
    raise ChainError(NO_PACKAGE)


def record_doubt(context: Context, payload: dict, report: dict, now: Clock = _now) -> dict:
    """Grava o parecer da dúvida cega sobre o último pacote deste JSON."""
    digest = payload_hash(payload)
    _last_package(read(registro_path(context)), digest)
    report = report if isinstance(report, dict) else {}
    risks, reviewer = report.get("riscos"), report.get("revisor")
    if (
        report.get("veredito") not in VERDICTS
        or not isinstance(risks, list)
        or not all(isinstance(r, str) and r.strip() for r in risks)
        or not isinstance(reviewer, str)
        or not reviewer.strip()
    ):
        raise ChainError('parecer precisa de "veredito" (segue | não segue), "riscos" (textos) e "revisor"')
    line = {"payload": digest, "veredito": report["veredito"], "riscos": risks, "revisor": reviewer}
    append(registro_path(context), "duvida", line, now)
    return line


def schedule(context: Context, client: Any, payload: dict, now: Clock = _now) -> list[dict]:
    digest = payload_hash(payload)
    entries = read(registro_path(context))
    index = _last_package(entries, digest)
    last = entries[index]
    doubts = [e for e in entries[index + 1 :] if e["event"] == "duvida" and e["payload"] == digest]
    if not doubts:
        raise ChainError(
            "sem dúvida cega sobre o pacote atual: rode o agente duvida-cega e `vp postiz duvida`"
        )
    if doubts[-1]["veredito"] != "segue":
        raise ChainError("a dúvida cega disse 'não segue': resolva os riscos e refaça o pacote")
    episode_id = last["evidencia"]["episodio"]
    if not last["recomendacao"].startswith("agendar") or gate4(context, episode_id) not in {
        "aprovado",
        "sem episódio",
    }:
        raise ChainError("o pacote recomenda não agendar ou o gate 4 mudou: refaça o pacote")
    try:
        created = client.schedule(payload)
    except ProviderError as error:
        append(registro_path(context), "falha", {"payload": digest, "erro": str(error)}, now)
        raise
    append(
        registro_path(context),
        "agendado",
        {"payload": digest, "data": last["o_que"]["data"], "posts": created},
        now,
    )
    return created
