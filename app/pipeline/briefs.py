"""Cópia de um resumo (radar do nicho, perfil de formato) para a pasta do episódio (RF5, ADR 047).

O resumo é uma cópia datada: o roteiro e o `vp check` leem a do episódio, e o original pode mudar depois sem
mudar o que este episódio usou. O contrato de substituição, igual para os dois tipos:

- o conteúdo é validado pelo contrato antes de qualquer escrita; fora dele, nada é gravado;
- o mesmo conteúdo não escreve nada, e outro conteúdo só entra com `replace`, nunca por engano;
- na troca, o anterior fica ao lado com a data dele no nome e **nunca sobrescreve** um guardado antes (nome
  repetido ganha `.2`, `.3`; conteúdo idêntico reaproveita o arquivo que já existe);
- o guardado é gravado antes da troca, e cada arquivo vai inteiro ou não vai (um `replace` por arquivo): uma
  falha no meio deixa o atual no lugar, nunca um episódio sem resumo;
- com o episódio travado, e sem criar a pasta de um episódio que não existe.
"""

from __future__ import annotations

import hashlib
from itertools import count

from pydantic import BaseModel, ValidationError

from app.errors import PipelineError
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.constants.radar_constants import RadarConstants
from app.pipeline.models.brief_action import BriefAction
from app.pipeline.models.brief_install import BriefInstall
from app.pipeline.models.brief_spec import BriefSpec
from app.pipeline.numbers import FormatBrief
from app.pipeline.ports import ManifestStore
from app.pipeline.radar import RadarBrief


class BriefError(PipelineError, ValueError):
    """Resumo fora do contrato, episódio inexistente, ou troca sem `--atualizar`; nada foi escrito."""


def radar_spec() -> BriefSpec:
    return BriefSpec(
        file=RadarConstants.BRIEF_FILE,
        archive="radar-brief.{stamp}.json",
        parse=RadarBrief.model_validate_json,
        stamp=lambda brief: f"{brief.generated_at:%Y%m%d-%H%M%S}",
        describe=lambda brief: f"{brief.niche}, de {brief.generated_at:%d/%m/%Y}",
    )


def format_spec() -> BriefSpec:
    return BriefSpec(
        file=NumbersConstants.FORMAT_FILE,
        archive="formato-brief-{stamp}.json",
        parse=FormatBrief.model_validate_json,
        stamp=lambda brief: brief.data,
        describe=lambda brief: f"{brief.nicho}, grupo {brief.grupo}, {brief.data}",
    )


def _parse(spec: BriefSpec, text: str) -> BaseModel | None:
    try:
        return spec.parse(text)
    except ValidationError:
        return None


def install_brief(
    store: ManifestStore, episode_id: str, spec: BriefSpec, text: str, *, replace: bool = False
) -> BriefInstall:
    try:
        brief = spec.parse(text)  # o contrato errado para aqui, antes de qualquer escrita
    except ValidationError as error:
        first = error.errors()[0]
        where = ".".join(map(str, first["loc"])) or "registro"
        raise BriefError(f"{spec.file}: fora do contrato ({where}: {first['msg']})") from error
    if not store.path(episode_id, "").is_dir():  # o lock criaria a pasta de um episódio que não existe
        raise BriefError(f"episódio {episode_id} não existe")
    with store.lock(episode_id):
        target = store.path(episode_id, spec.file)
        if not target.is_file():
            write_atomic(target, text.encode("utf-8"))
            return BriefInstall(BriefAction.INSTALLED, brief)
        current = target.read_text(encoding="utf-8")
        if current == text:
            return BriefInstall(BriefAction.UNCHANGED, brief)
        old = _parse(spec, current)
        if not replace:
            what = spec.describe(old) if old is not None else "ilegível"
            raise BriefError(f"{spec.file} já tem outro conteúdo ({what}); use --atualizar para trocar")
        stamp = spec.stamp(old) if old is not None else hashlib.sha256(current.encode()).hexdigest()[:8]
        kept = _keep(store, episode_id, spec, stamp, current)
        write_atomic(target, text.encode("utf-8"))
        return BriefInstall(BriefAction.REPLACED, brief, kept)


def _keep(store: ManifestStore, episode_id: str, spec: BriefSpec, stamp: str, content: str) -> str:
    """Guarda o conteúdo que sai sem apagar nenhum guardado antes (a mesma data, outro conteúdo: `.2`)."""
    for n in count(1):
        name = spec.archive.format(stamp=stamp if n == 1 else f"{stamp}.{n}")
        path = store.path(episode_id, name)
        if not path.exists():
            write_atomic(path, content.encode("utf-8"))
            return name
        if path.read_text(encoding="utf-8") == content:
            return name  # já guardado (tentativa anterior que parou antes da troca)
    raise AssertionError("inalcançável")
