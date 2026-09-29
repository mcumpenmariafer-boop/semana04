from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nro_doc', 'apellidos', 'nombres', 'telefono', 'email', 'estado')
    list_filter = ('tipo_doc', 'estado')
    search_fields = ('nro_doc', 'apellidos', 'nombres', 'email')