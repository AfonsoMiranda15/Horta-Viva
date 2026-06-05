import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracao.settings')
django.setup()

from api.models import Produto

for p in Produto.objects.all():
    print(f"ID: {p.id}, Nome: {p.nome}, Imagem Principal: {p.imagem_principal}, Imagem: {p.imagem}")
