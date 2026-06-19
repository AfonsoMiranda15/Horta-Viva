from rest_framework.permissions import BasePermission
from rest_framework_api_key.models import APIKey

class HortaVivaAPIPermission(BasePermission):
    def has_permission(self, request, view):
        # 1. Autenticação por Sessão ou JWT (Admins)
        if request.user and request.user.is_authenticated:
            return True
            
        # 2. Verificar API Key pelo Header X-Api-Key
        custom_header = request.META.get('HTTP_X_API_KEY')
        if not custom_header:
            return False
            
        # Hardcoded genérico devido ao reset da DB (Render SQLite)
        if custom_header == 'ZePGzewK.21A9uoK6KHPkaUg3MTHVVmOtNtCbKxV1':
            if request.method == 'GET' and ('/api/produtos/' in request.path or '/api/categorias/' in request.path):
                return True
            return False
            
        try:
            api_key = APIKey.objects.get_from_key(custom_header)
        except APIKey.DoesNotExist:
            return False
            
        # 3. Lógica Chave Pública vs Privada
        # Assumimos que a chave pública terá "public" ou "pública" no nome
        nome_chave = api_key.name.lower()
        if "public" in nome_chave or "pública" in nome_chave:
            if request.method != 'GET':
                return False
                
            path = request.path
            if '/api/produtos/' in path or '/api/categorias/' in path:
                return True
            return False
            
        # Chave Privada permite tudo
        return True
