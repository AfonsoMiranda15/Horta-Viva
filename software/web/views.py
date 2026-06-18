from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.views.generic import TemplateView

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Sessão iniciada com sucesso!')
            return redirect('minha-conta')
        else:
            messages.error(request, 'Nome de utilizador ou password incorretos.')
    else:
        form = AuthenticationForm()
    return render(request, 'web/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Sessão terminada.')
    return redirect('index')

# Para cadastro simplificado usando o UserCreationForm nativo do Django
# Idealmente podes customizar este form para pedir o Nome, NIF, etc.
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('minha-conta')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'web/cadastro.html', {'form': form})
