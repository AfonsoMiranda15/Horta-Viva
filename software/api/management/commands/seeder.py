from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from api.models import (
    Categoria, Produto, Cliente, Endereco, RegraFrete, Pedido, ItemPedido, Pagamento
)

class Command(BaseCommand):
    help = 'Popula a base de dados com massa de testes (Seeder)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando base de dados...")
        Pagamento.objects.all().delete()
        ItemPedido.objects.all().delete()
        Pedido.objects.all().delete()
        Endereco.objects.all().delete()
        Cliente.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Produto.objects.all().delete()
        Categoria.objects.all().delete()
        RegraFrete.objects.all().delete()

        self.stdout.write("Criando Categorias...")
        cat_frutas = Categoria.objects.create(nome="Frutas")
        cat_legumes = Categoria.objects.create(nome="Legumes")
        cat_verduras = Categoria.objects.create(nome="Verduras")
        cat_temperos = Categoria.objects.create(nome="Temperos")

        self.stdout.write("Criando Produtos...")
        produtos_data = [
            {"nome": "Maçã Gala", "sku": "FRT-MAC-01", "cat": cat_frutas, "preco": "2.50", "est": 50, "min": 10, "imagem": "/static/web/images/Frutas/maca-fruta-hortaviva.jpg"},
            {"nome": "Banana Prata", "sku": "FRT-BAN-01", "cat": cat_frutas, "preco": "1.80", "est": 5, "min": 10, "org": True, "imagem": "/static/web/images/Frutas/banana-prata-fruta-hortaviva.jpg"},
            {"nome": "Laranja Pera", "sku": "FRT-LAR-01", "cat": cat_frutas, "preco": "3.00", "est": 100, "min": 20, "imagem": "/static/web/images/Frutas/laranja-pera-fruta-hortaviva.jpg"},
            {"nome": "Morango", "sku": "FRT-MOR-01", "cat": cat_frutas, "preco": "5.50", "est": 8, "min": 15, "saz": True, "imagem": "/static/web/images/Frutas/morango-fruta-hortaviva.jpg"},
            {"nome": "Cenoura", "sku": "LEG-CEN-01", "cat": cat_legumes, "preco": "1.20", "est": 80, "min": 10, "imagem": "/static/web/images/Legumes/cenoura-legumes-hortaviva.jpg"},
            {"nome": "Batata Inglesa", "sku": "LEG-BAT-01", "cat": cat_legumes, "preco": "3.50", "est": 200, "min": 50, "imagem": "/static/web/images/Legumes/batata-legumes-hortaviva.jpg"},
            {"nome": "Cebola", "sku": "LEG-CEB-01", "cat": cat_legumes, "preco": "2.00", "est": 150, "min": 30, "imagem": "/static/web/images/Legumes/cebola-legumes-hortaviva.jpg"},
            {"nome": "Tomate Carmem", "sku": "LEG-TOM-01", "cat": cat_legumes, "preco": "4.00", "est": 20, "min": 15, "imagem": "/static/web/images/Legumes/tomate-legumes-hortaviva.jpg"},
            {"nome": "Alface Crespa", "sku": "VER-ALF-01", "cat": cat_verduras, "preco": "1.50", "est": 40, "min": 10, "org": True, "imagem": "/static/web/images/Verduras/alface-crespa-verdura-hortaviva.jpg"},
            {"nome": "Couve Manteiga", "sku": "VER-COU-01", "cat": cat_verduras, "preco": "2.00", "est": 35, "min": 10, "imagem": "/static/web/images/Verduras/couve-folha-verdura-hortaviva.jpg"},
            {"nome": "Rúcula", "sku": "VER-RUC-01", "cat": cat_verduras, "preco": "2.50", "est": 12, "min": 15, "org": True, "imagem": "/static/web/images/Verduras/rucula-verdura-hortaviva.jpg"},
            {"nome": "Espinafre", "sku": "VER-ESP-01", "cat": cat_verduras, "preco": "3.00", "est": 30, "min": 10, "imagem": "/static/web/images/Verduras/espinafre-verdura-hortaviva.jpg"},
            {"nome": "Salsa", "sku": "TEM-SAL-01", "cat": cat_temperos, "preco": "1.00", "est": 100, "min": 20, "imagem": "/static/web/images/Verduras/salsa-verdura-hortaviva.jpg"},
            {"nome": "Cebolinha", "sku": "TEM-CEB-01", "cat": cat_temperos, "preco": "1.00", "est": 90, "min": 20, "imagem": "/static/web/images/Verduras/cebolinha-verdura-hortaviva.jpg"},
            {"nome": "Manjericão", "sku": "TEM-MAN-01", "cat": cat_temperos, "preco": "2.50", "est": 50, "min": 10, "org": True, "imagem": "/static/web/images/Verduras/manjericao-verdura-hortaviva.jpg"},
        ]

        produtos_objs = []
        for p in produtos_data:
            obj = Produto.objects.create(
                nome=p["nome"],
                sku=p["sku"],
                categoria=p["cat"],
                preco=Decimal(p["preco"]),
                estoque=Decimal(str(p["est"])),
                estoque_minimo=Decimal(str(p["min"])),
                produto_organico=p.get("org", False),
                produto_sazonal=p.get("saz", False),
                imagem_principal=p.get("imagem", "")
            )
            produtos_objs.append(obj)

        self.stdout.write("Criando Clientes e Endereços...")
        clientes_data = [
            {"nome": "João Silva", "email": "joao@email.com", "cpf": "11122233344", "rua": "Rua A", "cidade": "Lisboa"},
            {"nome": "Maria Santos", "email": "maria@email.com", "cpf": "55566677788", "rua": "Rua B", "cidade": "Porto"},
            {"nome": "Carlos Costa", "email": "carlos@email.com", "cpf": "99900011122", "rua": "Rua C", "cidade": "Coimbra"},
        ]

        clientes_objs = []
        for i, c in enumerate(clientes_data):
            user = User.objects.create_user(username=f"user{i}", email=c["email"], password="password123")
            cliente = Cliente.objects.create(user=user, nome=c["nome"], email=c["email"], cpf_cnpj=c["cpf"])
            Endereco.objects.create(cliente=cliente, rua=c["rua"], numero="123", bairro="Centro", cidade=c["cidade"], estado="PT", cep="1000-000", is_principal=True)
            clientes_objs.append(cliente)

        self.stdout.write("Criando Pedidos...")
        status_list = ['aguardando', 'pago', 'separacao', 'saiu_entrega', 'entregue']
        for i in range(5):
            cliente = clientes_objs[i % len(clientes_objs)]
            pedido = Pedido.objects.create(
                numero=f"PED-{1000+i}",
                cliente=cliente,
                forma_pagamento='cartao',
                status=status_list[i % len(status_list)],
                custo_frete=Decimal('5.00')
            )
            
            # Adicionar itens
            p1 = produtos_objs[i % len(produtos_objs)]
            p2 = produtos_objs[(i+1) % len(produtos_objs)]
            
            ItemPedido.objects.create(pedido=pedido, produto=p1, quantidade=Decimal('2'), preco_unitario=p1.preco)
            ItemPedido.objects.create(pedido=pedido, produto=p2, quantidade=Decimal('1'), preco_unitario=p2.preco)
            
            # Atualizar totais
            total_prod = (Decimal('2') * p1.preco) + (Decimal('1') * p2.preco)
            pedido.total_produtos = total_prod
            pedido.total_pedido = total_prod + pedido.custo_frete
            pedido.save()

            Pagamento.objects.create(pedido=pedido, metodo='cartao', status='aprovado' if pedido.status != 'aguardando' else 'pendente')

        self.stdout.write(self.style.SUCCESS("Seeder executado com sucesso! Dados inseridos."))
