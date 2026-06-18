from urllib.parse import quote

from django.conf import settings
from storages.backends.s3 import S3Storage
from storages.backends.s3 import S3ManifestStaticStorage

import helpers.storages.mixins as mixins


class MinioStorage(S3Storage):
    pass


class StaticFileStorage(mixins.DefaultACLMixin, MinioStorage):
    """
    For staticfiles
    """

    location = "static"
    default_acl = "public-read"
    file_overwrite = True


class StaticManifestFileStorage(mixins.DefaultACLMixin, S3ManifestStaticStorage):
    """Storage de estáticos com nomes hashados para MinIO/S3."""

    patterns = ()
    location = "static"
    default_acl = "public-read"
    file_overwrite = True


class MediaFileStorage(mixins.DefaultACLMixin, MinioStorage):
    """
    For general uploads
    """

    location = "media"
    default_acl = "private"
    file_overwrite = False

    def url(self, name):
        """Retorna URL de mídia.

        Quando `STORAGE_MEDIA_SERVIR_VIA_DJANGO` estiver ativo, mantém URL local
        `/media/...` para o app servir arquivos a partir do storage remoto.
        """

        if getattr(settings, "STORAGE_MEDIA_SERVIR_VIA_DJANGO", False):
            nome_normalizado = str(name or "").replace("\\", "/").lstrip("/")
            media_url = str(getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/")
            return f"{media_url}/{quote(nome_normalizado, safe='/')}"
        return super().url(name)
