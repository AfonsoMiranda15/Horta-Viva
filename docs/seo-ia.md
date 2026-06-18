# SEO e IA (Implementacao Atual)

Este documento resume o que foi implementado para melhorar indexacao organica, compartilhamento social e consumo por crawlers de IA.

## Objetivo
- Melhorar descoberta das paginas principais (cursos, workshops e institucionais).
- Aumentar qualidade semantica para buscadores e sistemas de IA.
- Manter baixo impacto arquitetural (sem alterar fluxo de negocio).

## O que foi implementado
1. Metadados base por pagina:
- `title`, `meta description`, `canonical`, `hreflang`.
- Open Graph e Twitter Cards com imagem OG por pagina.

2. Dados estruturados (`application/ld+json`):
- Base global: `EducationalOrganization`, `WebSite`, `WebPage`, `SiteNavigationElement`.
- Home: `ItemList` para cursos e workshops.
- Paginas de curso: `Course`, `CourseInstance`, `BreadcrumbList`, `FAQPage`.
- Pagina de workshop: `Event`, `BreadcrumbList`, `FAQPage`.

3. Sitemap:
- Inclusao explicita das paginas de cursos e Espaco Corporativo no sitemap estatico.
- Sitemap publico em `/sitemap.xml`.

4. Politica para crawlers de IA:
- `robots.txt` com grupos explicitos para:
`GPTBot`, `ChatGPT-User`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`.
- Bloqueio mantido para areas administrativas (`/admin/` e `/fulltasks/`).

5. Endpoint `llms.txt`:
- Publicado em `/llms.txt`.
- Lista canonica das paginas principais e politicas.
- Referenciado dentro do `robots.txt`.

6. Conteudo editorial atemporal:
- Datas e horarios removidos de titulos, subtitulos e FAQ de apresentacao.
- Datas/horarios mantidos apenas nos cards de venda (bloco comercial), para evitar conflito em turmas futuras.

## Endpoints tecnicos
- `GET /robots.txt`
- `GET /llms.txt`
- `GET /sitemap.xml`

## Conversao e analytics
- Implementada camada GA4 com consentimento RGPD e eventos de funil comercial.
- Documentacao detalhada em `docs/marketing-tags-conversao.md`.

## Como validar rapidamente
```bash
docker compose exec -T web python manage.py check
curl -s http://localhost:1975/robots.txt
curl -s http://localhost:1975/llms.txt
curl -s http://localhost:1975/sitemap.xml
```

## Escopo que ficou fora nesta rodada
- Otimizacao pesada de performance (compressao de imagem em pipeline, CDN edge tuning, cache HTTP agressivo por tipo de asset).
- Ajustes avancados de crawl budget por ambiente.
