from django.contrib import admin
from .models import (
    Categoria, Atributo, TermoAtributo, Produto, ImagemProduto,
    Cliente, Endereco, RegraFrete, Pedido, ItemPedido, Pagamento,
    Cupom, Banner, Notificacao, MovimentacaoEstoque, Configuracao, RelatorioProxy
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

@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'desconto_fixo', 'ativo', 'data_validade')
    list_filter = ('ativo',)
    search_fields = ('codigo',)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('titulo',)

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'lida', 'data_criacao')
    list_filter = ('lida',)
    search_fields = ('titulo', 'usuario__username')

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade', 'tipo', 'data_movimentacao')
    list_filter = ('tipo', 'data_movimentacao')
    search_fields = ('produto__nome',)

@admin.register(Configuracao)
class ConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ('nome_loja', 'email_contato', 'telefone_contato', 'pedido_minimo')
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(RelatorioProxy)
class RelatorioAdmin(admin.ModelAdmin):
    change_list_template = 'admin/relatorios.html'
    
    def has_add_permission(self, request):
        return False
        
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Sum
        
        total_vendas = Pedido.objects.filter(status='entregue').aggregate(Sum('total_pedido'))['total_pedido__sum'] or 0
        total_pedidos = Pedido.objects.filter(status='entregue').count()
        ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0
        
        extra_context = extra_context or {}
        extra_context['total_vendas'] = total_vendas
        extra_context['total_pedidos'] = total_pedidos
        extra_context['ticket_medio'] = ticket_medio
        
        return super().changelist_view(request, extra_context=extra_context)
