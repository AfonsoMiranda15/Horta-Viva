import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracao.settings')
django.setup()

from api.models import Produto, Categoria, Pedido

def seed():
    # Delete all
    print("Deleting existing products and categories...")
    Pedido.objects.all().delete()
    Produto.objects.all().delete()
    Categoria.objects.all().delete()

    print("Creating categories...")
    cat_fruta = Categoria.objects.create(nome="Fruta")
    cat_legume = Categoria.objects.create(nome="Legume")
    cat_verdura = Categoria.objects.create(nome="Verdura")
    cat_tempero = Categoria.objects.create(nome="Tempero")
    cat_mercearia = Categoria.objects.create(nome="Mercearia")

    print("Creating products...")
    # Fruta
    Produto.objects.create(nome="Maçã Gala", sku="FRU-001", preco=1.50, categoria=cat_fruta, unidade="kg")
    Produto.objects.create(nome="Banana Prata", sku="FRU-002", preco=1.20, categoria=cat_fruta, unidade="kg")
    Produto.objects.create(nome="Laranja Pera", sku="FRU-003", preco=0.99, categoria=cat_fruta, unidade="kg")
    Produto.objects.create(nome="Morango", sku="FRU-004", preco=2.50, categoria=cat_fruta, unidade="bandeja")

    # Legume
    Produto.objects.create(nome="Cenoura", sku="LEG-001", preco=1.10, categoria=cat_legume, unidade="kg")
    Produto.objects.create(nome="Batata Inglesa", sku="LEG-002", preco=0.85, categoria=cat_legume, unidade="kg")
    Produto.objects.create(nome="Cebola Roxa", sku="LEG-003", preco=1.80, categoria=cat_legume, unidade="kg")
    Produto.objects.create(nome="Tomate Italiano", sku="LEG-004", preco=2.10, categoria=cat_legume, unidade="kg")

    # Verdura
    Produto.objects.create(nome="Alface Crespa", sku="VER-001", preco=0.90, categoria=cat_verdura, unidade="unid")
    Produto.objects.create(nome="Couve Manteiga", sku="VER-002", preco=1.20, categoria=cat_verdura, unidade="mol")
    Produto.objects.create(nome="Rúcula", sku="VER-003", preco=1.50, categoria=cat_verdura, unidade="mol")
    Produto.objects.create(nome="Espinafre", sku="VER-004", preco=1.30, categoria=cat_verdura, unidade="mol")

    # Tempero
    Produto.objects.create(nome="Salsa", sku="TEM-001", preco=0.80, categoria=cat_tempero, unidade="mol")
    Produto.objects.create(nome="Cebolinha", sku="TEM-002", preco=0.80, categoria=cat_tempero, unidade="mol")
    Produto.objects.create(nome="Coentro", sku="TEM-003", preco=0.85, categoria=cat_tempero, unidade="mol")
    Produto.objects.create(nome="Manjericão", sku="TEM-004", preco=1.20, categoria=cat_tempero, unidade="mol")

    # Mercearia
    Produto.objects.create(nome="Azeite de Oliva Extra Virgem", sku="MER-001", preco=5.50, categoria=cat_mercearia, unidade="unid")
    Produto.objects.create(nome="Arroz Agulha", sku="MER-002", preco=1.20, categoria=cat_mercearia, unidade="kg")
    Produto.objects.create(nome="Feijão Preto", sku="MER-003", preco=1.80, categoria=cat_mercearia, unidade="kg")
    Produto.objects.create(nome="Sal Marinho", sku="MER-004", preco=0.90, categoria=cat_mercearia, unidade="kg")
    Produto.objects.create(nome="Massa Esparguete", sku="MER-005", preco=1.10, categoria=cat_mercearia, unidade="unid")

    print("Seed completed successfully!")

if __name__ == '__main__':
    seed()
