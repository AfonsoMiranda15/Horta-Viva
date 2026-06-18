"""Configuração central de armazenamento S3/MinIO.

Este módulo unifica a leitura de variáveis de ambiente para suportar
os padrões usados no projeto CMS e o padrão observado no projeto de referência.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse


def obter_variavel_ambiente(nome: str, valor_padrao: str | None = None) -> str | None:
    """Retorna uma variável de ambiente com fallback para valor padrão.

    Args:
        nome: Nome da variável de ambiente.
        valor_padrao: Valor usado quando a variável não está definida.

    Returns:
        Valor final da configuração.
    """

    valor = os.environ.get(nome)
    if valor in (None, ""):
        return valor_padrao
    return valor


def obter_booleano_ambiente(nome: str, padrao: bool = False) -> bool:
    """Converte uma variável de ambiente textual em booleano."""

    valor = obter_variavel_ambiente(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def montar_opcoes_minio() -> dict[str, Any]:
    """Monta opções para o backend S3Boto3 usado com MinIO."""

    access_key = (
        obter_variavel_ambiente("STORAGE_ACCESS_KEY")
        or obter_variavel_ambiente("MINIO_ROOT_USER")
        or obter_variavel_ambiente("MINIO_ACCESS_KEY")
    )
    secret_key = (
        obter_variavel_ambiente("STORAGE_SECRET_KEY")
        or obter_variavel_ambiente("MINIO_ROOT_PASSWORD")
        or obter_variavel_ambiente("MINIO_SECRET_KEY")
    )
    endpoint_url = (
        obter_variavel_ambiente("STORAGE_ENDPOINT_URL")
        or obter_variavel_ambiente("MINIO_ENDPOINT")
    )
    bucket_name = (
        obter_variavel_ambiente("STORAGE_BUCKET_NAME")
        or obter_variavel_ambiente("MINIO_BUCKET", "cms")
    )

    if not (access_key and secret_key and endpoint_url and bucket_name):
        return {}

    endpoint_publico = (
        obter_variavel_ambiente("STORAGE_PUBLIC_ENDPOINT_URL")
        or obter_variavel_ambiente("MINIO_CDN_DOMAIN")
        or None
    )

    opcoes: dict[str, Any] = {
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "access_key": access_key,
        "secret_key": secret_key,
        "signature_version": "s3v4",
        "region_name": obter_variavel_ambiente("STORAGE_REGION_NAME", "us-east-1"),
        "addressing_style": obter_variavel_ambiente("STORAGE_ADDRESSING_STYLE", "path"),
        "querystring_auth": obter_booleano_ambiente("STORAGE_QUERYSTRING_AUTH", False),
        "default_acl": obter_variavel_ambiente("STORAGE_DEFAULT_ACL", "public-read"),
        "object_parameters": {"CacheControl": "public, max-age=31536000"},
    }

    if endpoint_publico:
        endpoint_publico = endpoint_publico.rstrip("/")
        if endpoint_publico.startswith("http://") or endpoint_publico.startswith("https://"):
            url = urlparse(endpoint_publico)
            if url.netloc:
                caminho_publico = url.path.rstrip("/")
                dominio_personalizado = url.netloc
                if caminho_publico:
                    dominio_personalizado = f"{dominio_personalizado}{caminho_publico}"
                opcoes["custom_domain"] = dominio_personalizado
                opcoes["url_protocol"] = f"{url.scheme}:"
        else:
            opcoes["custom_domain"] = endpoint_publico

    return opcoes


MINIO_CONFIG_OPTIONS = montar_opcoes_minio()
