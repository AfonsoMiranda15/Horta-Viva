from rest_framework import serializers
from .models import (
    Categoria, Produto, ImagemProduto, Atributo, TermoAtributo, 
    Cliente, Endereco, RegraFrete, Pedido, ItemPedido, Pagamento
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

    class Meta:
        model = Produto
        fields = '__all__'

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    enderecos = EnderecoSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

class RegraFreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegraFrete
        fields = '__all__'

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario']

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
