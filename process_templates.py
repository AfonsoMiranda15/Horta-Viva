import os
import re
import glob

# URLs to map
url_map = {
    'index.html': 'index',
    'cadastro.html': 'cadastro',
    'carrinho.html': 'carrinho',
    'categorias.html': 'categorias',
    'checkout.html': 'checkout',
    'contato.html': 'contato',
    'detalhes-conta.html': 'detalhes-conta',
    'favoritos.html': 'favoritos',
    'login.html': 'login',
    'minha-conta.html': 'minha-conta',
    'moradas.html': 'moradas',
    'produto.html': 'produto',
    'promocoes.html': 'promocoes',
    'quem-somos.html': 'quem-somos',
}

files = glob.glob('software/templates/web/*.html')

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()

    # Add load static and i18n
    if '{% load static i18n %}' not in content:
        content = '{% load static i18n %}\n' + content

    # Replace header.js script and app-header with django include
    content = re.sub(r'<script src="header\.js"></script>', '', content)
    content = re.sub(r'<app-header></app-header>', '{% include "web/components/header.html" %}', content)

    # Replace app.js
    content = re.sub(r'<script src="app\.js.*?(?:"></script>)', '<script src="{% static \'web/app.js\' %}"></script>', content)
    content = re.sub(r'<script src="sw\.js.*?(?:"></script>)', '<script src="{% static \'web/sw.js\' %}"></script>', content)

    # Replace images
    content = re.sub(r'src="images/([^"]+)"', r'src="{% static \'web/images/\1\' %}"', content)

    # Replace .html links with {% url %}
    for html_file, url_name in url_map.items():
        # Using lookarounds to avoid replacing parameters (e.g., categorias.html?tipo=fruta)
        content = re.sub(f'href="{html_file}(#[^"]*)?"', f'href="{{% url \'{url_name}\' %}}\\1"', content)
        content = re.sub(f'href="{html_file}\\?([^"]*)"', f'href="{{% url \'{url_name}\' %}}?\\1"', content)
        # Handle cases like window.location.href = 'minha-conta.html'
        content = re.sub(f"window\.location\.href = '{html_file}'", f"window.location.href = \"{{% url '{url_name}' %}}\"", content)
        content = re.sub(f"window\.location\.pathname\.includes\('{html_file}'\)", f"window.location.pathname.includes(\"{{% url '{url_name}' %}}\")", content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print(f"Processed {len(files)} files.")
