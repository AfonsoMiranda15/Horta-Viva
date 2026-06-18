# Documentacao do Framework CMS

## Objetivo
Este repositorio entrega um CMS em Django + Wagtail para site institucional, blog e checkout comercial.

## Apps
- `software/base`: configuracao global, urls raiz, storages e sitemaps.
- `software/home`: paginas institucionais, cursos, workshops e contacto.
- `software/blog`: estrutura de conteudo Wagtail.
- `software/comercial`: ofertas, checkout, pedidos, pagamentos e faturacao.
- `software/helpers`: utilitarios de infraestrutura.

## URLs Principais
### Publico
- `/`
- `/quem-somos/`
- `/meu-servico/`
- `/cursos/*`
- `/espaco-corporativo/`
- `/espaco-corporativo/workshops/`
- `/vamos-conversar/`
- `/blog/`
- `/comprar/`

### Comercial
- `/checkout/<slug_oferta>/`
- `/checkout/<slug_oferta>/iniciar/`
- `/checkout/processar/<transaction_id>/`
- `/checkout/retorno/`
- `/pedido/<uuid>/estado/`
- `/webhooks/sibs/`

### Admin
- `/admin/`
- `/<WAGTAIL_ADMIN_URL>/` (padrao: `/fulltasks/`)

## Frontend Modular
- Base: `software/home/templates/home/base.html`
- Includes: `software/home/templates/home/includes/`
- CSS: `software/home/static/home/css/`
- JS: `software/home/static/home/js/`
- Consentimento: `software/home/static/home/js/consent/`
- Tracking: `software/home/static/home/js/tracking/`

Padrao:
- Nao misturar HTML/CSS/JS.
- Reaproveitar blocos por composicao.
- Evitar logica de negocio em templates.
- Centralizar configuracoes publicas em `settings -> context processor -> data-* -> JS`.

## Idiomas
- `pt-br` e `en` configurados em `LANGUAGES`.
- Rotas publicas com `i18n_patterns`.
- Conteudo Wagtail com `wagtail_localize`.

## Feature Flags de Menu
- `MENU_COMPRAR_HABILITADO=true|false`
- `MENU_PUBLICACOES_HABILITADO=true|false`

Quando desativado, o middleware de bloqueio remove menu/rodape e retorna `404` nas rotas relacionadas.

## Paginacao Publica
- `PAGINACAO_ITENS_POR_PAGINA`

Aplicada em:
- `/comprar/`
- `/blog/conteudos/` (indice do blog)

## Captura de Leads
- `PROVEDOR_CAPTURA_LEADS=email|mautic`
- Integracoes opcionais: `CODIGO_MAUTIC`, `CODIGO_JS_EXTRA`, `GA4_MEASUREMENT_ID`, `META_PIXEL_ID`, `LINKEDIN_PARTNER_ID`

## Storage
- `STORAGE_BACKEND=filesystem|minio|s3`
- MinIO/S3 configurado por `STORAGE_*` e `MINIO_*`

## Comandos Importantes
```bash
python manage.py check
python manage.py preparar_armazenamento
python manage.py criar_exemplo_conteudos
python manage.py criar_exemplo_comercial
python manage.py liberar_reservas_expiradas
python manage.py atualizar_token_toconline
```

## Convencoes
- Views institucionais em CBV.
- Classes/metodos customizados com docstring curta e objetiva.
- Preferir `reverse(...)` para URLs internas.
- Isolar responsabilidades entre `home`, `blog` e `comercial`.
