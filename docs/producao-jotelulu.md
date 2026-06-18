# Produção Jotelulu

## Estado desejado
- domínio: `metodoinvertido.com`
- servidor: `149.36.249.201`
- deploy automático: apenas `main`
- imagem Docker: `wwanzeller/metodoinvertido:latest`

## O que precisa existir fora do git
### 1. `.env` remoto
Caminho:
- `/home/wenderson/sites/metodoinvertido/producao/.env`

Origem:
- copiar de `docker/producao/.env.exemplo`
- preencher segredos reais no servidor ou via secret management

Campos críticos:
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `POSTGRES_*`
- `STORAGE_*`
- `MINIO_*`
- `COMERCIAL_SIBS_*`
- `COMERCIAL_TOCONLINE_*`
- `GA4_MEASUREMENT_ID`
- `META_PIXEL_ID`
- `LINKEDIN_PARTNER_ID`

### 2. Azure DevOps
Obrigatório configurar:
- pipeline apontando para `azure-pypelines.yaml`
- service connection Docker: `DockerWanzeller`
- service connection SSH: `MetodoInvertido-Production`
- secrets:
  - `usuarioDocker`
  - `senhaDocker`

### 3. Docker Hub
Obrigatório:
- criar `wwanzeller/metodoinvertido`
- garantir permissão de push da pipeline

## Segurança atual
Implementado:
- apenas `80/443` expostos publicamente
- Portainer, PostgreSQL e MinIO presos em `127.0.0.1`
- Traefik sem dashboard público
- Gunicorn atrás do Traefik
- WhiteNoise para estáticos
- cookies seguros em produção
- HSTS ativo
- `X-Frame-Options: DENY`
- `nosniff` ativo

## Itens que ainda exigem atenção operacional
1. Confirmar que o `.env` remoto usa:
- `ALLOWED_HOSTS=metodoinvertido.com`
- `STORAGE_DEFAULT_ACL=private`
- `STORAGE_BOOTSTRAP_PUBLICO=0`

2. Só desativar:
- `COMERCIAL_MODO_SIMULADO=1`
- `COMERCIAL_TOCONLINE_MODO_SIMULADO=1`

quando as credenciais externas forem reais.

3. Sincronizar os objetos antigos do MinIO quando houver troca de servidor.

## Regra de ouro
- não versionar `.env` real
- não expor MinIO/PostgreSQL/Portainer publicamente
- não fazer deploy manual fora da `main` sem necessidade operacional clara
