from django.db import migrations
import os
from django.utils.text import slugify

def map_images(apps, schema_editor):
    Produto = apps.get_model('api', 'Produto')
    
    # fix_images3.py data
    produtos_data = [
        {"nome": "Maçã Gala", "imagem": "/static/web/images/Frutas/maca-fruta-hortaviva.jpg"},
        {"nome": "Banana Prata", "imagem": "/static/web/images/Frutas/banana-prata-fruta-hortaviva.jpg"},
        {"nome": "Laranja Pera", "imagem": "/static/web/images/Frutas/laranja-pera-fruta-hortaviva.jpg"},
        {"nome": "Morango", "imagem": "/static/web/images/Frutas/morango-fruta-hortaviva.jpg"},
        {"nome": "Cenoura", "imagem": "/static/web/images/Legumes/cenoura-legumes-hortaviva.jpg"},
        {"nome": "Batata Inglesa", "imagem": "/static/web/images/Legumes/batata-legumes-hortaviva.jpg"},
        {"nome": "Cebola", "imagem": "/static/web/images/Legumes/cebola-legumes-hortaviva.jpg"},
        {"nome": "Tomate Carmem", "imagem": "/static/web/images/Legumes/tomate-legumes-hortaviva.jpg"},
        {"nome": "Alface Crespa", "imagem": "/static/web/images/Verduras/alface-crespa-verdura-hortaviva.jpg"},
        {"nome": "Couve Manteiga", "imagem": "/static/web/images/Verduras/couve-folha-verdura-hortaviva.jpg"},
        {"nome": "Rúcula", "imagem": "/static/web/images/Verduras/rucula-verdura-hortaviva.jpg"},
        {"nome": "Espinafre", "imagem": "/static/web/images/Verduras/espinafre-verdura-hortaviva.jpg"},
        {"nome": "Salsa", "imagem": "/static/web/images/Verduras/salsa-verdura-hortaviva.jpg"},
        {"nome": "Cebolinha", "imagem": "/static/web/images/Verduras/cebolinha-verdura-hortaviva.jpg"},
        {"nome": "Manjericão", "imagem": "/static/web/images/Verduras/manjericao-verdura-hortaviva.jpg"}
    ]

    for data in produtos_data:
        try:
            produto = Produto.objects.filter(nome__icontains=data["nome"]).first()
            if produto:
                produto.imagem_principal = data["imagem"]
                produto.save()
        except Exception:
            pass

    # fix_images.py / fix_images2.py automatic data
    static_images_dir = '/app/software/static/web/images/'
    all_images = []
    
    try:
        for root, dirs, files in os.walk(static_images_dir):
            for file in files:
                if file.endswith('.jpg') or file.endswith('.png'):
                    rel_path = os.path.relpath(os.path.join(root, file), '/app/software')
                    all_images.append('/' + rel_path)
    except Exception:
        pass
        
    for p in Produto.objects.exclude(nome__icontains='wenderson'):
        slug = slugify(p.nome)
        slug_parts = slug.split('-')
        
        best_match = None
        for img in all_images:
            img_filename = os.path.basename(img)
            if slug in img_filename:
                best_match = img
                break
                
        if not best_match and len(slug_parts) > 0:
            for img in all_images:
                img_filename = os.path.basename(img)
                first_word = slug_parts[0]
                if first_word and len(first_word) > 2 and first_word in img_filename:
                    best_match = img
                    break

        if best_match:
            p.imagem_principal = best_match
            p.save()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0014_variacaoproduto'),
    ]

    operations = [
        migrations.RunPython(map_images),
    ]
