# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Personalizar los títulos del Admin
admin.site.site_header = 'Sistema de Gestión de Encomiendas'
admin.site.site_title = 'Encomiendas Admin'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('envios.urls')),   # dashboard, encomiendas, login, logout, perfil
]

# En DEBUG=True, Django sirve los archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)