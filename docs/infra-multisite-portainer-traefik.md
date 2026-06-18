# Infraestrutura Atual

## Topologia oficial
- Branches operacionais: `desenvolvimento` e `main`
- CI/CD com deploy automático apenas de `main`
- Servidor de produção: `149.36.249.201`
- Domínio público: `metodoinvertido.com`
- Proxy reverso: Traefik
- Aplicação Django: container `metodoinvertido-web`
- Banco: PostgreSQL dedicado (`core-postgres`)
- Objetos: MinIO (`core-minio`)
- Administração de containers: Portainer (`edge-portainer`)

## Exposição de rede em produção
Público:
- `80/tcp`
- `443/tcp`

Apenas loopback do servidor:
- `127.0.0.1:9443` Portainer
- `127.0.0.1:15432` PostgreSQL
- `127.0.0.1:19000` MinIO API
- `127.0.0.1:19001` MinIO Console

Não fazem parte da produção atual:
- pgAdmin
- Mailpit
- Backrest
- dashboard público do Traefik
- promoção manual `local -> produção`

## Fluxo de deploy
1. Push em `main`
2. Azure DevOps faz build da imagem `wwanzeller/metodoinvertido:latest`
3. A pipeline copia apenas os ficheiros de `docker/producao/` para o servidor
4. O `SSH@0` faz `docker pull`, executa `init` e sobe `web`

Observação importante:
- O `.env` de produção **não é enviado** pela pipeline.
- O ficheiro remoto precisa existir previamente em:
- `/home/wenderson/sites/metodoinvertido/producao/.env`

## Serviço HTTP da aplicação
Produção usa:
- `gunicorn` atrás do Traefik

Não usamos mais:
- `uWSGI`
- `django.views.static.serve` para estáticos em produção

Estáticos em produção:
- `WhiteNoise`
- nomes hashados via manifest

## Storage
- Estáticos: filesystem do container + `collectstatic`
- Mídia: MinIO
- Mídia pública do site continua proxied por Django em `/media/`
- ACL padrão de mídia em produção: privada

## Requisitos obrigatórios de produção
1. Docker Hub
- repositório: `wwanzeller/metodoinvertido`
- tag usada: `latest`

2. Azure DevOps
- service connection Docker: `DockerWanzeller`
- service connection SSH: `MetodoInvertido-Production`
- secrets da pipeline:
  - `usuarioDocker`
  - `senhaDocker`

3. Servidor remoto
- diretório do deploy: `/home/wenderson/sites/metodoinvertido/producao`
- `.env` remoto criado manualmente a partir de `docker/producao/.env.exemplo`

4. Dados
- base PostgreSQL migrada para o novo servidor
- buckets MinIO de produção precisam conter os objetos antigos quando houver migração de ambiente

## Checklist mínimo pós-deploy
- `https://metodoinvertido.com` responde `200`
- admin responde em `/admin/`
- `collectstatic` executou sem erro no `init`
- checkout permanece simulado enquanto houver credenciais de homologação
- `ALLOWED_HOSTS` do `.env` remoto não usa `*`
- buckets MinIO esperados existem
