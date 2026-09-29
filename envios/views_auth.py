# envios/views_auth.py — Login, logout y perfil
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Empleado


def login_view(request):
    """Vista para el login de empleados"""
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_page = request.POST.get('next') or request.GET.get('next', '')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()      # ya autenticado por el form
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            # Redirigir a la página solicitada (si es segura) o al dashboard
            if next_page and url_has_allowed_host_and_scheme(
                    next_page, allowed_hosts={request.get_host()}):
                return redirect(next_page)
            return redirect('dashboard')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_page})


def logout_view(request):
    """Cierra la sesión del usuario"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def perfil_view(request):
    """Perfil del empleado autenticado"""
    empleado = Empleado.desde_usuario(request.user)
    return render(request, 'accounts/perfil.html', {
        'empleado': empleado,
        'registradas': empleado.encomiendas_registradas.count(),
        'sesion_expira': request.session.get_expiry_date(),
    })