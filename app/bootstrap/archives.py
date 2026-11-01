"""Os bancos de imagem que podem ser usados agora (RF5, G11): composição, que é quem lê registro e config.

Banco sem adapter ou com chave ausente (`ConfigurationError`) é pulado com o motivo, e os outros seguem.
Qualquer outro erro ao montar um adapter é bug e sobe. `LazyContext.archives` não muda: continua abortando."""

from __future__ import annotations

from app.bootstrap import DEFAULT_REGISTRY
from app.bootstrap.registry import ConfigurationError, Registry
from app.pipeline.models.archive_availability import ArchiveAvailability
from app.pipeline.models.skipped_archive import SkippedArchive
from app.providers.archives.base import ArchiveProvider
from app.settings import Settings


def available_archives(settings: Settings, registry: Registry = DEFAULT_REGISTRY) -> ArchiveAvailability:
    archives: list[ArchiveProvider] = []
    skipped: list[SkippedArchive] = []
    for name in settings.providers.archives:
        registration = registry["archives"].get(name)
        if registration is None or registration.factory is None:
            skipped.append(SkippedArchive(name, "sem adapter (acervo ainda não implementado, ou só manual)"))
            continue
        try:
            archives.append(registration.factory(settings))
        except ConfigurationError as error:
            skipped.append(SkippedArchive(name, str(error)))
    return ArchiveAvailability(tuple(archives), tuple(skipped))
