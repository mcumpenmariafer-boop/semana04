# envios/views_cbv.py — Vistas basadas en clases (CBV)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from config.choices import EstadoEnvio

from .forms import EncomiendaForm
from .models import Empleado, Encomienda


class EncomiendaListView(LoginRequiredMixin, ListView):
    model = Encomienda
    template_name = 'envios/lista.html'
    context_object_name = 'encomiendas'
    paginate_by = 15
    ordering = ['-fecha_registro']

    def get_queryset(self):
        qs = Encomienda.objects.con_relaciones()
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados'] = EstadoEnvio.choices
        ctx['estado_activo'] = self.request.GET.get('estado', '')
        return ctx


class EncomiendaDetailView(LoginRequiredMixin, DetailView):
    model = Encomienda
    template_name = 'envios/detalle.html'
    context_object_name = 'encomienda'

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['historial'] = self.object.historial.select_related('empleado')
        return ctx


class EncomiendaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Encomienda
    form_class = EncomiendaForm
    template_name = 'envios/form.html'
    success_message = 'Encomienda %(codigo)s creada correctamente.'
    extra_context = {'titulo': 'Nueva Encomienda (CBV)'}

    def get_success_url(self):
        return reverse_lazy('encomienda_detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Asignar el empleado antes de guardar
        form.instance.empleado_registro = Empleado.desde_usuario(self.request.user)
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % {'codigo': self.object.codigo}


class EncomiendaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Encomienda
    form_class = EncomiendaForm
    template_name = 'envios/form.html'
    success_message = 'Encomienda actualizada correctamente.'
    extra_context = {'titulo': 'Editar Encomienda (CBV)'}

    def get_success_url(self):
        return reverse_lazy('encomienda_detalle', kwargs={'pk': self.object.pk})