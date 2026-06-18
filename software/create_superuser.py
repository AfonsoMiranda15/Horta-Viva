import os

from django.contrib.auth.models import User  # type: ignore


def create_superuser():
    """Cria ou sincroniza o superusuário padrão do ambiente."""

    usuario = os.getenv("DJANGO_SUPERUSUARIO")
    email = os.getenv("DJANGO_EMAIL_SUPERUSUARIO")
    senha = os.getenv("DJANGO_SENHA_SUPERUSUARIO")

    if not usuario:
        print("Nome de usuário padrão não configurado.")
        return

    if not senha:
        print("Senha do superusuário padrão não configurada.")
        return

    usuario_existente = User.objects.filter(username=usuario).first()
    if not usuario_existente:
        print("Superusuário não encontrado, criando um novo...")
        User.objects.create_superuser(username=usuario, email=email, password=senha)
    else:
        alterado = False

        if email and usuario_existente.email != email:
            usuario_existente.email = email
            alterado = True

        if not usuario_existente.is_staff:
            usuario_existente.is_staff = True
            alterado = True

        if not usuario_existente.is_superuser:
            usuario_existente.is_superuser = True
            alterado = True

        if alterado:
            usuario_existente.save(update_fields=["email", "is_staff", "is_superuser"])
            print("Superusuário sincronizado com configurações do ambiente.")
        else:
            print("Superusuário já existe.")
