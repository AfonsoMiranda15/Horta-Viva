import re
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, F, Avg, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib.auth.models import User

from .models import (
    Categoria, Produto, Cliente, Endereco, RegraFrete, Pedido, Pagamento
)
from .serializers import (
    CategoriaSerializer, ProdutoSerializer, ClienteSerializer, EnderecoSerializer,
    RegraFreteSerializer, PedidoSerializer, PagamentoSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filterset_fields = ['categoria', 'produto_ativo', 'produto_em_destaque']

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Cliente.objects.all()
        return Cliente.objects.filter(user=user)

class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Endereco.objects.all()
        if hasattr(user, 'cliente'):
            return Endereco.objects.filter(cliente=user.cliente)
        return Endereco.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'cliente'):
            serializer.save(cliente=user.cliente)
            
    @action(detail=True, methods=['post'])
    def tornar_principal(self, request, pk=None):
        endereco = self.get_object()
        user = request.user
        
        if hasattr(user, 'cliente') and endereco.cliente == user.cliente:
            # Desmarcar as outras
            Endereco.objects.filter(cliente=user.cliente).update(is_principal=False)
            # Marcar esta
            endereco.is_principal = True
            endereco.save()
            return Response({'status': 'Morada atualizada para principal com sucesso.'})
        return Response({'erro': 'Ação não permitida.'}, status=status.HTTP_403_FORBIDDEN)

class RegraFreteViewSet(viewsets.ModelViewSet):
    queryset = RegraFrete.objects.all()
    serializer_class = RegraFreteSerializer

    @action(detail=False, methods=['post'])
    def validar_cep(self, request):
        cep = request.data.get('cep', '')
        valor_carrinho = request.data.get('valor_carrinho', 0)
        
        cep_limpo = re.sub(r'\D', '', str(cep))
        
        try:
            valor_carrinho = Decimal(str(valor_carrinho))
        except (ValueError, TypeError):
            valor_carrinho = Decimal('0')

        regras = RegraFrete.objects.all()
        regra_encontrada = None
        
        for regra in regras:
            inicio = re.sub(r'\D', '', regra.cep_inicio)
            fim = re.sub(r'\D', '', regra.cep_fim)
            if inicio and fim and inicio <= cep_limpo <= fim:
                regra_encontrada = regra
                break

        if not regra_encontrada:
            return Response({'erro': 'Região não atendida pela Horta Viva'}, status=status.HTTP_400_BAD_REQUEST)
        
        valor_frete = regra_encontrada.valor_frete
        if regra_encontrada.frete_gratis_acima_de and valor_carrinho >= regra_encontrada.frete_gratis_acima_de:
            valor_frete = Decimal('0.00')
            
        return Response({
            'prazo_dias': regra_encontrada.prazo_dias,
            'valor_frete': valor_frete,
            'cidade': regra_encontrada.cidade,
            'estado': regra_encontrada.estado
        })

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    filterset_fields = ['status', 'cliente']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Pedido.objects.all()
        if hasattr(user, 'cliente'):
            return Pedido.objects.filter(cliente=user.cliente)
        return Pedido.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def avancar_status(self, request, pk=None):
        pedido = self.get_object()
        
        fluxo = ['aguardando', 'pago', 'separacao', 'saiu_entrega', 'entregue']
        
        try:
            current_index = fluxo.index(pedido.status)
        except ValueError:
            return Response({'erro': 'Status atual inválido para transição automática.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if current_index + 1 < len(fluxo):
            novo_status = fluxo[current_index + 1]
            pedido.status = novo_status
            
            mensagem_historico = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] Status alterado para {pedido.get_status_display()} pelo admin {request.user.username}.\n"
            pedido.historico_status = (pedido.historico_status or "") + mensagem_historico
            
            pedido.save()
            return Response({'status': novo_status, 'mensagem': 'Status avançado com sucesso.'})
        else:
            return Response({'erro': 'O pedido já se encontra no último status.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recompra_rapida(self, request):
        user = request.user
        if not hasattr(user, 'cliente'):
            return Response({'erro': 'Usuário não tem perfil de cliente associado.'}, status=status.HTTP_400_BAD_REQUEST)
            
        ultimo_pedido = Pedido.objects.filter(cliente=user.cliente, status='entregue').order_by('-criado_em').first()
        
        if not ultimo_pedido:
            return Response({'erro': 'Nenhum pedido entregue encontrado para recompra.'}, status=status.HTTP_404_NOT_FOUND)
            
        itens = ultimo_pedido.itens.all()
        lista_itens = []
        for item in itens:
            lista_itens.append({
                'produto_id': item.produto.id,
                'nome': item.produto.nome,
                'quantidade': item.quantidade,
                'preco_unitario_atual': item.produto.preco
            })
            
        return Response({
            'pedido_origem': ultimo_pedido.numero,
            'data_pedido': ultimo_pedido.criado_em,
            'itens': lista_itens
        })

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer

class DashboardView(APIView):
    def get(self, request):
        hoje = timezone.now().date()
        
        pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje)
        qtd_pedidos = pedidos_hoje.count()
        
        pedidos_validos = pedidos_hoje.exclude(status='cancelado')
        faturamento_hoje = pedidos_validos.aggregate(total=Sum('total_pedido'))['total'] or 0
        
        qtd_validos = pedidos_validos.count()
        ticket_medio = round((faturamento_hoje / qtd_validos), 2) if qtd_validos > 0 else 0
        
        um_dia_atras = timezone.now() - timezone.timedelta(days=1)
        clientes_novos = Cliente.objects.filter(user__date_joined__gte=um_dia_atras).count()
        
        produtos_alerta = Produto.objects.filter(estoque__lte=F('estoque_minimo'))
        alertas_estoque_minimo = [
            {
                "id": p.id,
                "nome": p.nome,
                "estoque_atual": p.estoque,
                "estoque_minimo": p.estoque_minimo
            } for p in produtos_alerta
        ]

        return Response({
            'pedidos_do_dia': qtd_pedidos,
            'faturamento_total_dia': faturamento_hoje,
            'ticket_medio': ticket_medio,
            'clientes_novos': clientes_novos,
            'alertas_estoque_minimo': alertas_estoque_minimo
        })

class RelatoriosView(APIView):
    def get(self, request):
        mes_atual = timezone.now().month
        ano_atual = timezone.now().year
        
        mais_vendidos = Produto.objects.filter(
            itempedido__pedido__criado_em__month=mes_atual,
            itempedido__pedido__criado_em__year=ano_atual,
            itempedido__pedido__status__in=['pago', 'separacao', 'saiu_entrega', 'entregue']
        ).annotate(
            quantidade_vendida=Sum('itempedido__quantidade')
        ).order_by('-quantidade_vendida')[:5]
        
        lista_mais_vendidos = [
            {
                "id": p.id,
                "nome": p.nome,
                "quantidade_vendida": p.quantidade_vendida or 0
            } for p in mais_vendidos
        ]
        
        from django.db.models import DecimalField
        menos_vendidos = Produto.objects.filter(produto_ativo=True).annotate(
            quantidade_vendida=Coalesce(Sum('itempedido__quantidade', filter=Q(
                itempedido__pedido__criado_em__month=mes_atual,
                itempedido__pedido__criado_em__year=ano_atual,
                itempedido__pedido__status__in=['pago', 'separacao', 'saiu_entrega', 'entregue']
            )), 0, output_field=DecimalField())
        ).order_by('quantidade_vendida')[:5]
        
        lista_menos_vendidos = [
            {
                "id": p.id,
                "nome": p.nome,
                "quantidade_vendida": p.quantidade_vendida
            } for p in menos_vendidos
        ]
        
        resumo_fretes_agg = Pedido.objects.filter(
            criado_em__month=mes_atual,
            criado_em__year=ano_atual
        ).aggregate(
            total_arrecadado=Sum('custo_frete'),
            media_frete=Avg('custo_frete')
        )

        return Response({
            'produtos_mais_vendidos': lista_mais_vendidos,
            'produtos_menos_vendidos': lista_menos_vendidos,
            'resumo_fretes': {
                'total_arrecadado': resumo_fretes_agg['total_arrecadado'] or 0,
                'media_frete': round(resumo_fretes_agg['media_frete'] or 0, 2)
            }
        })

class RegisterView(APIView):
    permission_classes = [] # Allow any to register
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        nome = request.data.get('nome')
        cpf_cnpj = request.data.get('cpf_cnpj')
        
        if not all([username, password, email, nome, cpf_cnpj]):
            return Response({'erro': 'Todos os campos são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({'erro': 'Username já em uso.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(email=email).exists():
            return Response({'erro': 'E-mail já em uso.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if Cliente.objects.filter(cpf_cnpj=cpf_cnpj).exists():
            return Response({'erro': 'CPF/CNPJ já cadastrado.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            cliente = Cliente.objects.create(
                user=user,
                nome=nome,
                cpf_cnpj=cpf_cnpj,
                email=email
            )
            return Response({'mensagem': 'Conta criada com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
