# Metodo Invertido CMS

Projeto Django + Wagtail do site institucional do Metodo Invertido, com modulo comercial (checkout/pagamentos) e blog.

## Estado Atual (2026-03-25)
- Frontend principal alinhado ao design aprovado do Metodo Invertido.
- Blog/Wagtail ativo em `/blog/`.
- Modulo comercial ativo em `/comprar/` e checkout.
- Fluxo de deploy oficial via Azure Pipelines em `main`.

## Arquitetura
- `software/base`: configuracao global (settings, urls, asgi/wsgi, sitemaps).
- `software/home`: paginas institucionais, cursos e workshops.
- `software/blog`: estrutura do blog no Wagtail.
- `software/comercial`: catalogo, ofertas, checkout, pedidos e pagamentos.
- `software/helpers`: utilitarios de infraestrutura (storage e suporte).

## Rotas Publicas Definitivas
### Institucional
- `/`
- `/quem-somos/`
- `/meu-servico/`
- `/cursos/criacao-e-gestao-de-sites/`
- `/cursos/programacao-web/`
- `/cursos/deploy-web-com-docker/`
- `/cursos/marketing-digital-e-presenca-online/`
- `/espaco-corporativo/`
- `/espaco-corporativo/workshops/`
- `/espaco-corporativo/workshops/<slug_workshop>/`
- `/vamos-conversar/`
- `/vamos-conversar/agendamento/`
- `/politica-de-privacidade/`
- `/termos-e-condicoes/`

### Blog/Wagtail
- `/blog/`
- `/blog/contents/` (alias para indice)

### Comercial
- `/comprar/`
- `/checkout/<slug_oferta>/`
- `/checkout/<slug_oferta>/iniciar/`
- `/checkout/processar/<transaction_id>/`
- `/checkout/retorno/`
- `/checkout/transacao/<transaction_id>/estado/`
- `/pedido/<uuid>/estado/`
- `/webhooks/sibs/`

### Admin
- `/admin/`
- `/<WAGTAIL_ADMIN_URL>/` (padrao: `/fulltasks/`)

### Compatibilidade legada (redirect 301)
- `/espaco-cooperativo/` -> `/espaco-corporativo/`
- `/espaco-cooperativo/workshops/` -> `/espaco-corporativo/workshops/`

## Frontend (Padrao de Composicao)
- HTML: `software/home/templates/home/`
- Blocos/includes: `software/home/templates/home/includes/`
- CSS: `software/home/static/home/css/`
- JS: `software/home/static/home/js/`
- Assets: `software/home/static/home/img/` e `software/home/static/home/fonts/`

Regras:
- Nao misturar HTML, CSS e JS.
- Reutilizar blocos/composicoes para manter DRY.
- Evitar regra de negocio em template.

## Branches e Deploy
- `desenvolvimento`: integração e validação.
- `main`: producao.

Fluxo configurado:
1. Commit em `desenvolvimento` e validação local.
2. Merge para `main`.
3. Push para `origin main`.
4. `main` executa build, push da imagem Docker `latest` e CD em produção.

### Azure Pipelines
- `azure-pypelines.yaml` é disparado apenas por `main`.
- `main` faz build/push da imagem Docker `latest` e publica em produção.
- A pipeline espera que cada servidor tenha:
  - `docker compose`
  - um `.env` remoto já existente no diretório de deploy
  - acesso ao Docker Registry configurado pelas variáveis seguras `usuarioDocker` e `senhaDocker`

Antes de ativar a pipeline, ajustar no Azure DevOps:
- `sshServiceConnectionProduction`
- `remoteDeployPathProduction`
- `dockerImageRepository`
- `dockerRegistryServiceConnection`

## Subida Local (desenvolvimento)
```bash
docker compose up --build
```

## Servicos Locais (docker-compose)
| Servico | URL | Usuario padrao | Senha padrao |
|---|---|---|---|
| Site | http://localhost:1975 | - | - |
| Django Admin | http://localhost:1975/admin/ | admin | admin |
| Wagtail Admin | http://localhost:1975/fulltasks/ | admin | admin |
| pgAdmin | http://localhost:5050 | admin@example.com | admin |
| MinIO Console | http://localhost:9001 | minio | minio123 |
| Mailpit | http://localhost:8025 | - | - |

## Comandos Operacionais
### Validacao rapida
```bash
docker compose exec -T web python manage.py check
./teste.sh home.tests comercial.tests blog.tests -v 1
```

### Seeds e sincronizacao comercial
```bash
# Limpa dados comerciais legados (idempotente)
docker compose exec -T web python manage.py criar_exemplo_comercial

# Libera reservas expiradas de pedidos
docker compose exec -T web python manage.py liberar_reservas_expiradas

# Atualiza token fiscal externo (quando usado)
docker compose exec -T web python manage.py atualizar_token_toconline
```

> Cursos e workshops agora seguem arquitetura estatica (templates HTML + i18n com `trans`).
> Cadastros de item/oferta de pagamento devem ser feitos no Django Admin.

### Conteudo e infraestrutura
```bash
# Garante estrutura inicial do blog/Wagtail
docker compose exec -T web python manage.py criar_exemplo_conteudos

# Garante bucket/prefixos no storage
docker compose exec -T web python manage.py preparar_armazenamento
```

## Variaveis de Ambiente
Principais arquivos:
- `docker/desenvolvimento/.env.exemple`
- `docker/producao/.env.exemplo`

Arquivos reais:
- `docker/desenvolvimento/.env` deve existir apenas localmente e nao e versionado.
- o `.env` de producao deve existir apenas no servidor remoto e nao e versionado.

Grupos relevantes:
- Django/core: `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- Banco: `POSTGRES_*`
- Storage: `STORAGE_*`, `MINIO_*`
- Comercial/checkout: `COMERCIAL_*`
- Captura de leads: `PROVEDOR_CAPTURA_LEADS`, `LEADS_*`, `MAUTIC_*`
- Menu/feature flags: `MENU_COMPRAR_HABILITADO`, `MENU_PUBLICACOES_HABILITADO`

## Documentacao Complementar
- Framework CMS: `docs/cms-framework.md`
- Admin comercial: `docs/admin-comercial.md`
- Padrao de templates: `docs/padrao-templates.md`
- Infra multisite (Traefik + Portainer): `docs/infra-multisite-portainer-traefik.md`
- Producao Jotelulu: `docs/producao-jotelulu.md`
- SEO e IA (implementado): `docs/seo-ia.md`
