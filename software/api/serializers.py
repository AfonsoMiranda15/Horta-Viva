from rest_framework import serializers
from .models import (
    Categoria, Produto, ImagemProduto, Atributo, TermoAtributo, 
    Cliente, Endereco, Cartao, RegraFrete, Pedido, ItemPedido, Pagamento,
    Cupom, Banner, Notificacao, MovimentacaoEstoque, Configuracao
)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ImagemProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemProduto
        fields = ['id', 'imagem', 'ordem']

class AtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atributo
        fields = '__all__'

class TermoAtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermoAtributo
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    galeria = ImagemProdutoSerializer(many=True, read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    variacoes_detalhes = TermoAtributoSerializer(source='variacoes', many=True, read_only=True)
    imagem_principal = serializers.SerializerMethodField()

    class Meta:
        model = Produto
        fields = '__all__'

    def get_imagem_principal(self, obj):
        if not obj.imagem_principal:
            return None
        nome_imagem = str(obj.imagem_principal)
        if nome_imagem.startswith('/static/'):
            return nome_imagem
        return obj.imagem_principal.url

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ['cliente']

class ClienteSerializer(serializers.ModelSerializer):
    enderecos = EnderecoSerializer(many=True, read_only=True)
    cartoes = CartaoSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    total_gasto = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_total_gasto(self, obj):
        from django.db.models import Sum
        total = obj.pedidos.filter(status='entregue').aggregate(Sum('total_pedido'))['total_pedido__sum']
        return round(total, 2) if total else 0.00

class RegraFreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegraFrete
        fields = '__all__'

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'produto_nome', 'nome_produto', 'quantidade', 'preco_unitario']

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    pagamento = PagamentoSerializer(read_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'


class CupomSerializer(serializers.ModelSerializer):
    valido = serializers.SerializerMethodField()

    class Meta:
        model = Cupom
        fields = '__all__'

    def get_valido(self, obj):
        return obj.is_valido()

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = '__all__'

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'
