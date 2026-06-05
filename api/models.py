from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    categoria_pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Atributo(models.Model):
    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class TermoAtributo(models.Model):
    atributo = models.ForeignKey(Atributo, on_delete=models.CASCADE, related_name='termos')
    valor = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.valor)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atributo.nome}: {self.valor}"

class Produto(models.Model):
    UNIDADE_CHOICES = [
        ('gr', 'Grama'),
        ('kg', 'Quilograma'),
        ('mol', 'Molho'),
        ('unid', 'Unidade'),
        ('caixa', 'Caixa'),
        ('bandeja', 'Bandeja'),
        ('dz', 'Dúzia'),
        ('sc', 'Saco'),
        ('pe', 'Peça'),
    ]

    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    codigo_interno = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos')
    descricao_curta = models.TextField(blank=True)
    descricao_completa = models.TextField(blank=True)
    imagem_principal = models.ImageField(upload_to='produtos/', blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Peso em Kg ou formatado pela unidade")
    unidade = models.CharField(max_length=10, choices=UNIDADE_CHOICES, default='unid')
    estoque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Flags Booleanas
    produto_ativo = models.BooleanField(default=True)
    produto_em_destaque = models.BooleanField(default=False)
    produto_sazonal = models.BooleanField(default=False)
    produto_organico = models.BooleanField(default=False)
    produto_variavel = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='galeria')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"Imagem {self.ordem} de {self.produto.nome}"

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cliente')
    nome = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco_completo = models.TextField(blank=True)
    historico = models.TextField(blank=True)
    ultima_compra = models.DateTimeField(null=True, blank=True)
    ltv = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.nome

class Endereco(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='enderecos')
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=50)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    is_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.estado}"

class RegraFrete(models.Model):
    cep_inicio = models.CharField(max_length=10, blank=True)
    cep_fim = models.CharField(max_length=10, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2)
    frete_gratis_acima_de = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pedido_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prazo_dias = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cidade}/{self.estado} - € {self.valor_frete}"

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando pagamento'),
        ('pago', 'Pago'),
        ('separacao', 'Em separação'),
        ('saiu_entrega', 'Saiu para entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    FORMA_PGTO_CHOICES = [
        ('pix', 'Pix'),
        ('transferencia', 'Transferência'),
        ('cartao', 'Cartão'),
    ]

    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    total_produtos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PGTO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    observacoes = models.TextField(blank=True)
    historico_status = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.numero} - {self.cliente.nome}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('Produto', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido.numero})"

class Pagamento(models.Model):
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pagamento')
    metodo = models.CharField(max_length=20, choices=Pedido.FORMA_PGTO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default='pendente')
    transacao_id = models.CharField(max_length=100, blank=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pagamento {self.pedido.numero} - {self.get_status_display()}"
