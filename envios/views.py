# envios/views.py — Vistas basadas en funciones (FBV)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from config.choices import EstadoEnvio

from .forms import EncomiendaForm
from .models import Empleado, Encomienda


# ── Dashboard ────────────────────────────────────────────────────
@login_required
def dashboard(request):
    """Vista principal del sistema con estadísticas"""
    hoy = timezone.localdate()
    context = {
        'total_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.en_transito().count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy).count(),
        'ultimas': Encomienda.objects.con_relaciones()[:5],
    }
    return render(request, 'envios/dashboard.html', context)


# ── Listado con filtros y paginación ─────────────────────────────
@require_GET
@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.con_relaciones()

    # Filtros opcionales (parámetros GET)
    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '').strip()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q) |
            Q(remitente__nombres__icontains=q) |
            Q(remitente__apellidos__icontains=q) |
            Q(destinatario__nombres__icontains=q) |
            Q(destinatario__apellidos__icontains=q)
        )

    # Guardar el último filtro en la sesión (ejemplo de request.session)
    request.session['ultimo_filtro_estado'] = estado

    # Paginación: 15 por página
    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    encomiendas = paginator.get_page(page_number)

    return render(request, 'envios/lista.html', {
        'encomiendas': encomiendas,     # objeto Page (iterable)
        'page_obj': encomiendas,        # usado por partials/paginacion.html
        'estados': EstadoEnvio.choices,
        'estado_activo': estado,
        'q': q,
    })


# ── Detalle ──────────────────────────────────────────────────────
@login_required
def encomienda_detalle(request, pk):
    enc = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)
    historial = enc.historial.select_related('empleado')
    return render(request, 'envios/detalle.html', {
        'encomienda': enc,
        'historial': historial,
    })


# ── Crear (patrón GET/POST + Post/Redirect/Get) ──────────────────
@require_http_methods(['GET', 'POST'])
@login_required
def encomienda_crear(request):
    """
    GET  -> muestra el formulario vacío
    POST -> valida, guarda y redirige al detalle
    """
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            enc = form.save(commit=False)       # no guarda aún en BD
            enc.empleado_registro = Empleado.desde_usuario(request.user)
            enc.save()                          # ahora sí guarda
            request.session['ultima_ruta'] = enc.ruta_id
            messages.success(request, f'Encomienda {enc.codigo} registrada correctamente.')
            return redirect('encomienda_detalle', pk=enc.pk)
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        # Preseleccionar la última ruta usada (guardada en sesión)
        form = EncomiendaForm(initial={'ruta': request.session.get('ultima_ruta')})

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })


# ── Editar ───────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
@login_required
def encomienda_editar(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    if enc.esta_entregada:
        messages.warning(request, 'No se puede editar una encomienda finalizada.')
        return redirect('encomienda_detalle', pk=pk)

    form = EncomiendaForm(request.POST or None, instance=enc)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Encomienda {enc.codigo} actualizada correctamente.')
            return redirect('encomienda_detalle', pk=pk)
        messages.error(request, 'Corrige los errores del formulario.')

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': f'Editar {enc.codigo}',
    })


# ── Cambiar estado (solo POST) ───────────────────────────────────
@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    nuevo_estado = request.POST.get('estado')
    observacion = request.POST.get('observacion', '')
    try:
        empleado = Empleado.desde_usuario(request.user)
        enc.cambiar_estado(nuevo_estado, empleado, observacion)
        messages.success(request, f'Estado actualizado a: {enc.get_estado_display()}')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('encomienda_detalle', pk=pk)


# ── Eliminar (con PermissionDenied) ──────────────────────────────
@login_required
def encomienda_eliminar(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    # Regla de negocio: solo se puede eliminar si está pendiente
    if enc.estado != EstadoEnvio.PENDIENTE:
        raise PermissionDenied      # -> 403 Forbidden
    if request.method == 'POST':
        codigo = enc.codigo
        enc.delete()
        messages.success(request, f'Encomienda {codigo} eliminada.')
        return redirect('encomienda_lista')
    return render(request, 'envios/confirmar_eliminar.html', {'enc': enc})


# ── Buscar por código (Http404) ──────────────────────────────────
@login_required
def buscar_por_codigo(request, codigo):
    try:
        enc = Encomienda.objects.get(codigo=codigo.upper())
    except Encomienda.DoesNotExist:
        raise Http404(f'No existe la encomienda {codigo}')
    return redirect('encomienda_detalle', pk=enc.pk)


# ── Endpoint JSON ────────────────────────────────────────────────
@login_required
def encomienda_estado_json(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    return JsonResponse({
        'codigo': enc.codigo,
        'estado': enc.estado,
        'display': enc.get_estado_display(),
        'retraso': enc.tiene_retraso,
        'dias': enc.dias_en_transito,
    })