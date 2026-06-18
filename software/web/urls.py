from django.urls import path, re_path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='web/index.html'), name='index'),
    path('cadastro/', views.register_view, name='cadastro'),
    path('carrinho/', TemplateView.as_view(template_name='web/carrinho.html'), name='carrinho'),
    path('categorias/', TemplateView.as_view(template_name='web/categorias.html'), name='categorias'),
    path('checkout/', TemplateView.as_view(template_name='web/checkout.html'), name='checkout'),
    path('contato/', TemplateView.as_view(template_name='web/contato.html'), name='contato'),
    path('detalhes-conta/', TemplateView.as_view(template_name='web/detalhes-conta.html'), name='detalhes-conta'),
    path('favoritos/', TemplateView.as_view(template_name='web/favoritos.html'), name='favoritos'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('minha-conta/', TemplateView.as_view(template_name='web/minha-conta.html'), name='minha-conta'),
    path('moradas/', TemplateView.as_view(template_name='web/moradas.html'), name='moradas'),
    path('produto/', TemplateView.as_view(template_name='web/produto.html'), name='produto'),
    path('promocoes/', TemplateView.as_view(template_name='web/promocoes.html'), name='promocoes'),
    path('quem-somos/', TemplateView.as_view(template_name='web/quem-somos.html'), name='quem-somos'),
    
    # Redirecionador automático: Remove o .html de qualquer link
    re_path(r'^(?P<url_path>.*)\.html$', RedirectView.as_view(url='/%(url_path)s/', permanent=True)),
]
