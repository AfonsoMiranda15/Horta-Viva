import re
import uuid
import requests
import logging
from decimal import Decimal
from django.conf import settings
from rest_framework import viewsets, status

logger = logging.getLogger(__name__)
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, F, Avg, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Categoria, Produto, Cliente, Endereco, Cartao, RegraFrete, Pedido, Pagamento,
    Cupom, Banner, Notificacao, MovimentacaoEstoque
)
from .serializers import (
    CategoriaSerializer, ProdutoSerializer, ClienteSerializer, EnderecoSerializer, CartaoSerializer,
    RegraFreteSerializer, PedidoSerializer, PagamentoSerializer,
    CupomSerializer, BannerSerializer, NotificacaoSerializer, MovimentacaoEstoqueSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome', 'descricao_curta', 'descricao_completa']
    ordering_fields = ['preco', 'nome', 'id']
    filterset_fields = {
        'categoria': ['exact'],
        'produto_ativo': ['exact'],
        'produto_em_destaque': ['exact'],
        'preco': ['gte', 'lte'],
    }

    def get_queryset(self):
        queryset = Produto.objects.all()
        em_promocao = self.request.query_params.get('em_promocao', None)
        if em_promocao is not None and em_promocao.lower() == 'true':
            queryset = queryset.filter(preco_promocional__isnull=False, preco_promocional__gt=0)
        return queryset

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Cliente.objects.none()
            
        # Garante que todo utilizador autenticado (incluindo admin) tem um perfil de cliente associado
        # para que possam usar o frontend de forma independente e isolada.
        if not hasattr(user, 'cliente'):
            Cliente.objects.create(
                user=user,
                nome=user.username,
                email=user.email,
                telefone='',
                cpf_cnpj=''
            )
            
        return Cliente.objects.filter(user=user)

    @action(detail=False, methods=['get', 'post'])
    def favoritos(self, request):
        user = request.user
        if not hasattr(user, 'cliente'):
            return Response({'erro': 'Usuário não tem perfil de cliente associado.'}, status=status.HTTP_400_BAD_REQUEST)
            
        cliente = user.cliente
        
        if request.method == 'GET':
            produtos = cliente.produtos_favoritos.all()
            from .serializers import ProdutoSerializer
            return Response(ProdutoSerializer(produtos, many=True).data)
            
        elif request.method == 'POST':
            produto_id = request.data.get('produto_id')
            acao = request.data.get('acao') # 'adicionar' ou 'remover'
            
            if not produto_id or not acao:
                return Response({'erro': 'produto_id e acao são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
                
            from .models import Produto
            try:
                produto = Produto.objects.get(id=produto_id)
            except Produto.DoesNotExist:
                return Response({'erro': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
                
            if acao == 'adicionar':
                cliente.produtos_favoritos.add(produto)
                return Response({'status': 'Produto adicionado aos favoritos.'})
            elif acao == 'remover':
                cliente.produtos_favoritos.remove(produto)
                return Response({'status': 'Produto removido dos favoritos.'})
            else:
                return Response({'erro': 'Ação inválida. Use adicionar ou remover.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='produtos-mais-comprados')
    def produtos_mais_comprados(self, request, pk=None):
        cliente = self.get_object()
        from django.db.models import Sum, Case, When
        from .models import ItemPedido, Produto
        
        # Filtra os itens de pedidos do cliente (incluindo pendentes para facilitar testes)
        itens = ItemPedido.objects.filter(
            pedido__cliente=cliente,
            pedido__status__in=['pendente', 'pago', 'separacao', 'saiu_entrega', 'entregue']
        ).values('produto').annotate(total_comprado=Sum('quantidade')).order_by('-total_comprado')[:5]
        
        produtos_ids = [item['produto'] for item in itens]
        
        if not produtos_ids:
            return Response([])
            
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(produtos_ids)])
        produtos = Produto.objects.filter(id__in=produtos_ids).order_by(preserved)
        
        from .serializers import ProdutoSerializer
        serializer = ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)

class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'cliente'):
            return Endereco.objects.filter(cliente=user.cliente)
        return Endereco.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'cliente'):
            cliente = user.cliente
            is_primeira = not Endereco.objects.filter(cliente=cliente).exists()
            endereco = serializer.save(cliente=cliente)
            
            if is_primeira:
                endereco.is_principal = True
                endereco.save(update_fields=['is_principal'])
            elif endereco.is_principal:
                Endereco.objects.filter(cliente=cliente).exclude(id=endereco.id).update(is_principal=False)
            
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

class CartaoViewSet(viewsets.ModelViewSet):
    serializer_class = CartaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'cliente'):
            return Cartao.objects.filter(cliente=user.cliente)
        return Cartao.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'cliente'):
            serializer.save(cliente=user.cliente)

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
        if hasattr(user, 'cliente'):
            return Pedido.objects.filter(cliente=user.cliente)
        return Pedido.objects.none()

    def perform_update(self, serializer):
        old_status = self.get_object().status
        pedido = serializer.save()
        
        if old_status != pedido.status:
            # Create In-App Notification if user opted in or if it's the final delivery notification
            if pedido.receber_notificacoes or pedido.status == 'entregue':
                from .models import Notificacao
                user = pedido.cliente.user
                if user:
                    Notificacao.objects.create(
                        usuario=user,
                        titulo=f"Atualização da Encomenda #{pedido.numero}",
                        mensagem=f"A sua encomenda está agora: {pedido.get_status_display()}"
                    )



    def create(self, request, *args, **kwargs):
        dados = request.data
        itens_data = dados.pop('itens', [])
        
        # Cielo data
        card_number = dados.pop('card_number', None)
        card_holder = dados.pop('card_holder', None)
        card_expiration = dados.pop('card_expiration', None)
        card_cvv = dados.pop('card_cvv', None)

        if 'numero' not in dados:
            dados['numero'] = str(uuid.uuid4().hex[:10].upper())
            
        cupom_id = dados.pop('cupom_id', None)

        serializer = self.get_serializer(data=dados)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()

        if cupom_id:
            from .models import Cupom
            try:
                cupom = Cupom.objects.get(id=cupom_id)
                pedido.cupom = cupom
                pedido.save(update_fields=['cupom'])
                
                cupom.usos_atuais += 1
                if cupom.limite_usos and cupom.usos_atuais >= cupom.limite_usos:
                    cupom.ativo = False
                cupom.save(update_fields=['usos_atuais', 'ativo'])
            except Cupom.DoesNotExist:
                pass

        from .models import ItemPedido, Produto
        for item in itens_data:
            produto = Produto.objects.get(id=item['produto'])
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                nome_produto=item.get('nome_produto', produto.nome),
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario']
            )

        # Integração Cielo
        forma_pagamento = pedido.forma_pagamento
        cielo_merchant_id = getattr(settings, 'CIELO_MERCHANT_ID', 'f6d4d4dc-65bd-4e3a-b851-bcda96df3d53')
        cielo_merchant_key = getattr(settings, 'CIELO_MERCHANT_KEY', 'WUTVGEFOTDJLUDOQLFYRSRWYCUGJIKKXXQSQMOWT')
        
        headers = {
            'MerchantId': cielo_merchant_id,
            'MerchantKey': cielo_merchant_key,
            'Content-Type': 'application/json'
        }
        
        # Sandbox URL
        cielo_url = "https://apisandbox.cieloecommerce.cielo.com.br/1/sales/"
        
        valor_centavos = int(pedido.total_pedido * 100)
        
        payload_cielo = {
            "MerchantOrderId": str(pedido.numero),
            "Customer": {
                "Name": pedido.cliente.nome
            },
            "Payment": {
                "Type": "CreditCard" if forma_pagamento == 'cartao' else ("Pix" if forma_pagamento == 'pix' else "Boleto"),
                "Amount": valor_centavos,
                "Installments": 1,
            }
        }
        
        if forma_pagamento == 'cartao' and card_number:
            payload_cielo["Payment"]["CreditCard"] = {
                "CardNumber": str(card_number),
                "Holder": str(card_holder),
                "ExpirationDate": str(card_expiration),
                "SecurityCode": str(card_cvv),
                "Brand": "Visa" # Simplificando no sandbox
            }
            # Vamos direto com a captura para cartão
            payload_cielo["Payment"]["Capture"] = True
            
        elif forma_pagamento == 'boleto':
            payload_cielo["Payment"]["Provider"] = "Bradesco2"
            payload_cielo["Payment"]["Address"] = "Rua Teste"
            payload_cielo["Payment"]["BoletoNumber"] = "123"
            payload_cielo["Payment"]["Assignor"] = "Horta Viva"
            payload_cielo["Payment"]["Demonstrative"] = "Compra na Horta Viva"
            payload_cielo["Payment"]["ExpirationDate"] = (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%d")
            payload_cielo["Payment"]["Identification"] = "11884926754"
            payload_cielo["Payment"]["Instructions"] = "Aceitar somente até o vencimento"
        
        transacao_id = ""
        qr_code = ""
        boleto_url = ""
        status_pagamento = "pendente"
        
        try:
            response = requests.post(cielo_url, json=payload_cielo, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Erro Cielo: {response.text}")
                try:
                    res_errors = response.json()
                    erro_msg = "Pagamento recusado pela operadora."
                    if isinstance(res_errors, list) and len(res_errors) > 0:
                        erro_msg = res_errors[0].get('Message', erro_msg)
                except:
                    erro_msg = "Erro ao processar o pagamento na operadora."
                
                pedido.status = 'cancelado'
                pedido.save()
                return Response({'erro': erro_msg}, status=status.HTTP_400_BAD_REQUEST)

            res_data = response.json()
            payment_res = res_data.get('Payment', {})
            transacao_id = payment_res.get('PaymentId', '')
            status_code = payment_res.get('Status')
            
            if status_code in [1, 2]: # Authorized or PaymentConfirmed
                status_pagamento = "aprovado"
                if pedido.status == 'aguardando':
                    pedido.status = 'pago'
                    pedido.save()
                    
                    # Abater stock
                    for item in pedido.itens.all():
                        produto = item.produto
                        quantidade = item.quantidade
                        produto.estoque -= quantidade
                        produto.save()
                        from .models import MovimentacaoEstoque
                        MovimentacaoEstoque.objects.create(
                            produto=produto,
                            quantidade=-quantidade,
                            tipo='saida',
                            observacao=f"Venda - Pedido {pedido.numero}",
                            pedido=pedido
                        )
                    
                # Criar a notificação solicitada
                from .models import Notificacao
                user = pedido.cliente.user
                if user:
                    Notificacao.objects.create(
                        usuario=user,
                        titulo=f"Pagamento Aprovado - Encomenda #{pedido.numero}",
                        mensagem="A sua encomenda foi paga com sucesso e já se encontra em estado de preparação/envio."
                    )
                    

            elif status_code in [3, 10]: # Denied, Voided
                status_pagamento = "recusado"
                pedido.status = 'cancelado'
                pedido.save()
                return Response({'erro': 'Pagamento recusado pela operadora do cartão.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if forma_pagamento == 'pix':
                qr_code = payment_res.get('QrCodeString', '')
            elif forma_pagamento == 'boleto':
                boleto_url = payment_res.get('Url', '')
                
        except Exception as e:
            logger.error(f"Erro ao comunicar com a Cielo: {e}")
            pedido.status = 'cancelado'
            pedido.save()
            return Response({'erro': 'Falha na comunicação com o gateway de pagamento.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        from .models import Pagamento
        Pagamento.objects.create(
            pedido=pedido,
            metodo=forma_pagamento,
            status=status_pagamento,
            transacao_id=transacao_id,
            data_pagamento=timezone.now() if status_pagamento == 'aprovado' else None
        )
        
        headers_res = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['status'] = pedido.status  # Garante que a resposta reflete o status atualizado
        if forma_pagamento == 'pix':
            response_data['qr_code'] = qr_code
        elif forma_pagamento == 'boleto':
            response_data['boleto_url'] = boleto_url
            
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers_res)

    @action(detail=True, methods=['get'])
    def gerar_comprovativo(self, request, pk=None):
        pedido = self.get_object()
        data = {
            "numero_pedido": pedido.numero,
            "data": pedido.criado_em.strftime("%d/%m/%Y %H:%M"),
            "cliente": pedido.cliente.nome,
            "total": str(pedido.total_pedido),
            "status": pedido.get_status_display(),
            "forma_pagamento": pedido.get_forma_pagamento_display(),
        }
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def estornar_pagamento(self, request, pk=None):
        pedido = self.get_object()
        if pedido.status == 'cancelado':
            return Response({"erro": "Pedido já cancelado."}, status=status.HTTP_400_BAD_REQUEST)
        
        cielo_merchant_id = getattr(settings, 'CIELO_MERCHANT_ID', 'f6d4d4dc-65bd-4e3a-b851-bcda96df3d53')
        cielo_merchant_key = getattr(settings, 'CIELO_MERCHANT_KEY', 'WUTVGEFOTDJLUDOQLFYRSRWYCUGJIKKXXQSQMOWT')
        headers = {
            'MerchantId': cielo_merchant_id,
            'MerchantKey': cielo_merchant_key,
        }
        
        try:
            pagamento = pedido.pagamento
            if pagamento.transacao_id:
                cielo_url = f"https://apisandbox.cieloecommerce.cielo.com.br/1/sales/{pagamento.transacao_id}/void"
                response = requests.put(cielo_url, headers=headers)
                if response.status_code in [200, 201]:
                    pedido.status = 'cancelado'
                    pedido.save()
                    pagamento.status = 'estornado'
                    pagamento.save()
                    return Response({"mensagem": "Pagamento estornado com sucesso."})
                else:
                    return Response({"erro": "Falha ao estornar na Cielo."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"erro": "Não foi possível estornar."}, status=status.HTTP_400_BAD_REQUEST)
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
            if novo_status == 'pago' and pedido.status != 'pago':
                # Abater stock
                for item in pedido.itens.all():
                    produto = item.produto
                    quantidade = item.quantidade
                    produto.estoque -= quantidade
                    produto.save()
                    MovimentacaoEstoque.objects.create(
                        produto=produto,
                        quantidade=-quantidade,
                        tipo='saida',
                        observacao=f"Venda - Pedido {pedido.numero}",
                        pedido=pedido
                    )

            pedido.status = novo_status
            
            mensagem_historico = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] Status alterado para {pedido.get_status_display()} pelo admin {request.user.username}.\n"
            pedido.historico_status = (pedido.historico_status or "") + mensagem_historico
            
            pedido.save()

            if pedido.receber_notificacoes or novo_status == 'entregue':
                from .models import Notificacao
                user = pedido.cliente.user
                if user:
                    Notificacao.objects.create(
                        usuario=user,
                        titulo=f"Atualização da Encomenda #{pedido.numero}",
                        mensagem=f"A sua encomenda está agora: {pedido.get_status_display()}"
                    )
                    


            return Response({'status': novo_status, 'mensagem': 'Status avançado com sucesso.'})
        else:
            return Response({'erro': 'O pedido já se encontra no último status.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='recompra-rapida')
    def recompra_rapida(self, request, pk=None):
        user = request.user
        if not hasattr(user, 'cliente'):
            return Response({'erro': 'Usuário não tem perfil de cliente associado.'}, status=status.HTTP_400_BAD_REQUEST)
            
        ultimo_pedido = self.get_object()
        
        if ultimo_pedido.cliente != user.cliente:
            return Response({'erro': 'Não tem permissão para aceder a esta encomenda.'}, status=status.HTTP_403_FORBIDDEN)
            
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
            Cliente.objects.create(
                user=user,
                nome=nome,
                cpf_cnpj=cpf_cnpj,
                email=email
            )
            return Response({'mensagem': 'Conta criada com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetView(APIView):
    permission_classes = [] # Allow any
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'erro': 'E-mail é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            nova_senha = 'HortaViva123!'
            user.set_password(nova_senha)
            user.save()
            return Response({'mensagem': f'Um e-mail de redefinição foi enviado. (Simulado: a nova senha é {nova_senha})'})
        except User.DoesNotExist:
            return Response({'mensagem': 'Se o email existir, um link de redefinição foi enviado.'})

class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer

    @action(detail=False, methods=['post'], permission_classes=[])
    def validar(self, request):
        codigo = request.data.get('codigo')
        if not codigo:
            return Response({'erro': 'Código não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cupom = Cupom.objects.get(codigo__iexact=codigo)
            if cupom.is_valido():
                return Response(CupomSerializer(cupom).data)
            else:
                return Response({'erro': 'Cupom expirado ou inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Cupom.DoesNotExist:
            return Response({'erro': 'Cupom não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(ativo=True).order_by('ordem')
    serializer_class = BannerSerializer
    permission_classes = [] # Allow reading banners without auth

class NotificacaoViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacao.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'], url_path='marcar-lida')
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        return Response({'status': 'Notificação marcada como lida.'})
