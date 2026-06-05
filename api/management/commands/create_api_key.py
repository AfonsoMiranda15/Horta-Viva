from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey

class Command(BaseCommand):
    help = 'Cria uma nova API Key e exibe no ecrã'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nome da API Key')

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        api_key, key = APIKey.objects.create_key(name=name)
        self.stdout.write(self.style.SUCCESS(f'API Key criada com sucesso: {name}'))
        self.stdout.write(self.style.WARNING(f'A chave secreta é: {key} (Guarde-a agora, não será exibida novamente!)'))
