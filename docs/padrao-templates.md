# Padrao de Templates (Home)

Este documento define a convencao oficial para templates do modulo `home`.

## Objetivo

- Garantir a mesma logica de composicao em todas as paginas.
- Evitar duplicidade de estrutura HTML.
- Manter os blocos reutilizaveis e previsiveis.

## Convencao de nomes

- `bloco-*.html`: secao reutilizavel de pagina.
- `composicao-*.html`: arquivo que apenas orquestra blocos.
- `menu.html`, `rodape.html`, `rgpd.html`: componentes de infraestrutura compartilhados.

## Estrutura obrigatoria de paginas

Cada pagina publica deve seguir este fluxo:

1. incluir `menu.html`
2. incluir um unico `composicao-*.html`
3. incluir `rodape.html`

Exemplo:

```django
<div id="page" class="page">
  {% include 'home/includes/menu.html' %}
  {% include 'home/includes/composicao-home.html' %}
  {% include 'home/includes/rodape.html' %}
</div>
```

## Regras de DRY

- Nao repetir estrutura de layout em pagina final.
- Centralizar variacoes de conteudo em `bloco-*`.
- Usar `composicao-*` para ordenar blocos por pagina.
- Ao criar novo bloco, avaliar reutilizacao antes de criar outro arquivo.

## Mapa atual de composicoes

- `composicao-home.html`
- `composicao-quem-somos.html`
- `composicao-meu-servico.html`
- `composicao-criacao-e-gestao-de-sites.html`
- `composicao-programacao-web.html`
- `composicao-deploy-web-com-docker.html`
- `composicao-markting-digital-presenca-online.html`
- `composicao-workshops.html`
- `composicao-workshop-detalhe.html`
- `composicao-espaco-corporativo.html`
- `composicao-vamos-conversar.html`
- `composicao-agendamento.html`
- `composicao-politica-privacidade.html`
- `composicao-termos-condicoes.html`
- `composicao-blog.html`

## Checklist para novas paginas

1. Criar `composicao-nome-pagina.html`.
2. Reusar `bloco-*` existentes.
3. Na pagina final, manter apenas `menu + composicao + rodape`.
4. Rodar:
   - `python manage.py makemessages -l pt -l en`
   - `python manage.py compilemessages`
   - `python manage.py check`
