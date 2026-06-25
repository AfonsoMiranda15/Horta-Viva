from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    categoria_pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

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
        ('pe', 'Pé'),
        ('lata', 'Lata'),
    ]

    nome = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    codigo_interno = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos')
    variacoes = models.ManyToManyField(TermoAtributo, blank=True, related_name='produtos', help_text="Selecione as variações deste produto (ex: Tamanho Médio, Cor Vermelha)")
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
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

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

class VariacaoProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='precos_variacao')
    termo = models.ForeignKey(TermoAtributo, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('produto', 'termo')
        verbose_name_plural = "Variações de Preço"
        
    def __str__(self):
        return f"{self.produto.nome} - {self.termo.valor}"

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
    cielo_token = models.CharField(max_length=100, blank=True, help_text="Token do cartão de crédito na Cielo")
    produtos_favoritos = models.ManyToManyField('Produto', blank=True, related_name='favoritados_por')

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

class Cartao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cartoes')
    numero = models.CharField(max_length=20)
    nome_cartao = models.CharField(max_length=100)
    validade = models.CharField(max_length=7) # MM/AAAA
    cvv = models.CharField(max_length=4)
    is_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"Cartão terminado em {self.numero[-4:]}"

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
        return f"{self.cidade}/{self.estado} - R$ {self.valor_frete}"

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
        ('boleto', 'Boleto'),
        ('cartao', 'Cartão de Crédito'),
    ]

    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    cupom = models.ForeignKey('Cupom', null=True, blank=True, on_delete=models.SET_NULL, related_name='pedidos')
    total_produtos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PGTO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    observacoes = models.TextField(blank=True)
    historico_status = models.TextField(blank=True)
    receber_notificacoes = models.BooleanField(default=False)
    is_recorrente = models.BooleanField(default=False)
    frequencia_dias = models.PositiveIntegerField(default=0, help_text="A cada quantos dias o pedido deve se repetir?")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.numero} - {self.cliente.nome}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('Produto', on_delete=models.PROTECT)
    nome_produto = models.CharField(max_length=255, blank=True, help_text="Nome do produto no momento da compra, incluindo variações (ex: Banana (Verde))")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        nome = self.nome_produto if self.nome_produto else self.produto.nome
        return f"{self.quantidade}x {nome} (Pedido {self.pedido.numero})"

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

class Cupom(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Desconto em %")
    desconto_fixo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Desconto em valor fixo")
    limite_usos = models.PositiveIntegerField(null=True, blank=True, help_text="Quantas vezes pode ser usado no total")
    usos_atuais = models.PositiveIntegerField(default=0)
    data_validade = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def is_valido(self):
        from django.utils import timezone
        if not self.ativo:
            return False
        if self.limite_usos and self.usos_atuais >= self.limite_usos:
            return False
        if self.data_validade and timezone.now() > self.data_validade:
            return False
        return True

    def __str__(self):
        return self.codigo

class Banner(models.Model):
    titulo = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.titulo

class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=255, default='Notificação')
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Notificação para {self.usuario.username}"

class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste Manual'),
    ]
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)
    pedido = models.ForeignKey('Pedido', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentacoes_estoque')

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} ({self.quantidade})"

class Configuracao(models.Model):
    nome_loja = models.CharField(max_length=255, default='Horta Viva')
    email_contato = models.EmailField(default='contato@hortaviva.com')
    telefone_contato = models.CharField(max_length=20, blank=True)
    endereco_loja = models.TextField(blank=True)
    pedido_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    meta_title_global = models.CharField(max_length=255, blank=True, help_text="SEO Title padrão da loja")
    meta_description_global = models.TextField(blank=True, help_text="SEO Description padrão da loja")
    
    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def save(self, *args, **kwargs):
        # Garante que seja um Singleton (só pode haver uma instância)
        if not self.pk and Configuracao.objects.exists():
            return Configuracao.objects.first()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configurações Globais"

class RelatorioProxy(Pedido):
    class Meta:
        proxy = True
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
