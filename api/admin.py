from django.contrib import admin
from .models import (
    Categoria, Atributo, TermoAtributo, Produto, ImagemProduto,
    Cliente, Endereco, RegraFrete, Pedido, ItemPedido, Pagamento
)

class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria_pai', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)

@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(TermoAtributo)
class TermoAtributoAdmin(admin.ModelAdmin):
    list_display = ('valor', 'atributo', 'slug')
    list_filter = ('atributo',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sku', 'preco', 'estoque', 'produto_ativo', 'produto_organico', 'produto_sazonal')
    list_filter = ('produto_ativo', 'produto_organico', 'produto_sazonal', 'categoria')
    search_fields = ('nome', 'sku')
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [ImagemProdutoInline]
    fieldsets = (
        ('Informação Principal', {
            'fields': ('nome', 'slug', 'sku', 'categoria', 'descricao_curta', 'descricao_completa', 'imagem_principal')
        }),
        ('Preços e Estoque', {
            'fields': ('preco', 'preco_promocional', 'estoque', 'estoque_minimo', 'peso', 'unidade')
        }),
        ('Flags', {
            'fields': ('produto_ativo', 'produto_em_destaque', 'produto_sazonal', 'produto_organico', 'produto_variavel')
        }),
    )

class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 0

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf_cnpj', 'ltv', 'ultima_compra')
    search_fields = ('nome', 'email', 'cpf_cnpj')
    inlines = [EnderecoInline]

@admin.register(RegraFrete)
class RegraFreteAdmin(admin.ModelAdmin):
    list_display = ('cidade', 'estado', 'cep_inicio', 'cep_fim', 'valor_frete', 'frete_gratis_acima_de', 'prazo_dias')
    list_filter = ('estado',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('preco_unitario',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'status', 'total_pedido', 'criado_em')
    list_filter = ('status', 'forma_pagamento', 'criado_em')
    search_fields = ('numero', 'cliente__nome', 'cliente__email')
    readonly_fields = ('total_produtos', 'custo_frete', 'total_pedido', 'criado_em', 'atualizado_em', 'historico_status')
    inlines = [ItemPedidoInline]

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status', 'metodo', 'data_pagamento')
    list_filter = ('status', 'metodo')
