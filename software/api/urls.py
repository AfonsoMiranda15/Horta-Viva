from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CategoriaViewSet, ProdutoViewSet, ClienteViewSet, EnderecoViewSet,
    RegraFreteViewSet, PedidoViewSet, PagamentoViewSet,
    DashboardView, RelatoriosView, RegisterView, PasswordResetView,
    CupomViewSet, BannerViewSet, NotificacaoViewSet, CartaoViewSet,
    ForceSeederView
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'enderecos', EnderecoViewSet, basename='endereco')
router.register(r'cartoes', CartaoViewSet, basename='cartao')
router.register(r'fretes', RegraFreteViewSet)
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'pagamentos', PagamentoViewSet)
router.register(r'cupons', CupomViewSet, basename='cupom')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('rest_framework.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('relatorios/', RelatoriosView.as_view(), name='relatorios'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('force-seeder/', ForceSeederView.as_view(), name='force_seeder'),
]
