# envios/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Empleado, Encomienda, HistorialEstado


class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    can_delete = False
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'empleado',
                       'observacion', 'fecha_cambio')


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado
    list_display = ('codigo', 'remitente_nombre', 'destinatario_nombre',
                    'ruta', 'estado_badge', 'peso_kg', 'fecha_registro')
    # Filtros laterales
    list_filter = ('estado', 'ruta', 'fecha_registro')
    # Búsqueda
    search_fields = ('codigo', 'remitente__apellidos',
                     'destinatario__apellidos', 'remitente__nro_doc')
    # Campos de solo lectura
    readonly_fields = ('codigo', 'fecha_registro', 'fecha_entrega_real')
    ordering = ('-fecha_registro',)
    list_per_page = 20
    list_select_related = ('remitente', 'destinatario', 'ruta')
    inlines = [HistorialInline]

    # Organizar los campos en secciones (fieldsets)
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'descripcion', 'peso_kg', 'volumen_cm3')
        }),
        ('Partes', {
            'fields': ('remitente', 'destinatario', 'ruta', 'empleado_registro')
        }),
        ('Estado y fechas', {
            'fields': ('estado', 'costo_envio',
                       'fecha_registro', 'fecha_entrega_est', 'fecha_entrega_real')
        }),
        ('Notas', {
            'classes': ('collapse',),       # sección colapsable
            'fields': ('observaciones',)
        }),
    )

    @admin.display(description='Remitente', ordering='remitente__apellidos')
    def remitente_nombre(self, obj):
        return obj.remitente.nombre_completo

    @admin.display(description='Destinatario', ordering='destinatario__apellidos')
    def destinatario_nombre(self, obj):
        return obj.destinatario.nombre_completo

    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        """Muestra el estado con color"""
        colores = {
            'PE': '#b45309',  # ámbar - pendiente
            'TR': '#1d4ed8',  # azul - en tránsito
            'EN': '#047857',  # verde - entregado
            'CA': '#b91c1c',  # rojo - cancelado
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px">{}</span>',
            color, obj.get_estado_display()
        )


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'cargo', 'email', 'estado')
    list_filter = ('cargo', 'estado')
    search_fields = ('codigo', 'apellidos', 'nombres', 'email')


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('encomienda', 'estado_anterior', 'estado_nuevo',
                    'empleado', 'fecha_cambio')
    readonly_fields = ('encomienda', 'estado_anterior', 'estado_nuevo',
                       'empleado', 'fecha_cambio')
    list_filter = ('estado_nuevo',)
    ordering = ('-fecha_cambio',)