from django.db import migrations
from decimal import Decimal

def populate_missing_data(apps, schema_editor):
    Banner = apps.get_model('api', 'Banner')
    RegraFrete = apps.get_model('api', 'RegraFrete')
    Configuracao = apps.get_model('api', 'Configuracao')
    Cupom = apps.get_model('api', 'Cupom')

    # Banners
    if not Banner.objects.exists():
        Banner.objects.create(titulo="A Época do Morango Chegou!", imagem="/static/web/images/banners/morango.png", link="/promocoes/", ordem=1, ativo=True)
        Banner.objects.create(titulo="Frescura Direta do Campo", imagem="/static/web/images/banners/alface.png", link="/categorias/?tipo=verdura", ordem=2, ativo=True)
        Banner.objects.create(titulo="Seleção 100% Orgânica", imagem="/static/web/images/banners/organico.png", link="/categorias/?tipo=legume", ordem=3, ativo=True)
    else:
        # Se os banners já existem, atualiza o caminho da imagem
        for banner in Banner.objects.all():
            nome_img = str(banner.imagem)
            if 'morango' in nome_img:
                banner.imagem = "/static/web/images/banners/morango.png"
            elif 'alface' in nome_img:
                banner.imagem = "/static/web/images/banners/alface.png"
            elif 'organico' in nome_img:
                banner.imagem = "/static/web/images/banners/organico.png"
            banner.save()

    # Configuracao
    if not Configuracao.objects.exists():
        Configuracao.objects.create(nome_loja="Horta Viva")

    # RegraFrete
    if not RegraFrete.objects.exists():
        RegraFrete.objects.create(cidade="Lisboa", estado="PT", valor_frete=Decimal('5.00'), frete_gratis_acima_de=Decimal('50.00'), pedido_minimo=Decimal('10.00'), prazo_dias=1)
        RegraFrete.objects.create(cidade="Porto", estado="PT", valor_frete=Decimal('6.50'), frete_gratis_acima_de=Decimal('60.00'), pedido_minimo=Decimal('15.00'), prazo_dias=2)

    # Cupom
    if not Cupom.objects.exists():
        Cupom.objects.create(codigo="BEMVINDO10", desconto_percentual=Decimal('10.00'), limite_usos=100, ativo=True)

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0015_auto_update_images'),
    ]

    operations = [
        migrations.RunPython(populate_missing_data),
    ]
