"""Storages de staticfiles com manifest sem pós-processamento de CSS legado."""

from __future__ import annotations

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageSemReescrita(ManifestStaticFilesStorage):
    """Gera nomes hashados sem reescrever URLs internas de CSS legado."""

    patterns = ()
