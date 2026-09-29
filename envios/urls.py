# envios/urls.py
from django.urls import path

from . import views, views_auth, views_cbv

urlpatterns = [
    # ── Vistas basadas en funciones (FBV) ─────────────────────
    path('', views.dashboard, name='dashboard'),
    path('encomiendas/', views.encomienda_lista, name='encomienda_lista'),
    path('encomiendas/nueva/', views.encomienda_crear, name='encomienda_crear'),
    path('encomiendas/<int:pk>/', views.encomienda_detalle, name='encomienda_detalle'),
    path('encomiendas/<int:pk>/editar/', views.encomienda_editar, name='encomienda_editar'),
    path('encomiendas/<int:pk>/estado/', views.encomienda_cambiar_estado,
         name='encomienda_cambiar_estado'),
    path('encomiendas/<int:pk>/eliminar/', views.encomienda_eliminar,
         name='encomienda_eliminar'),
    path('encomiendas/<int:pk>/json/', views.encomienda_estado_json,
         name='encomienda_estado_json'),
    path('encomiendas/buscar/<str:codigo>/', views.buscar_por_codigo,
         name='buscar_por_codigo'),

    # ── Las mismas pantallas con vistas basadas en clases (CBV) ─
    path('cbv/encomiendas/', views_cbv.EncomiendaListView.as_view(),
         name='cbv_encomienda_lista'),
    path('cbv/encomiendas/<int:pk>/', views_cbv.EncomiendaDetailView.as_view(),
         name='cbv_encomienda_detalle'),
    path('cbv/encomiendas/nueva/', views_cbv.EncomiendaCreateView.as_view(),
         name='cbv_encomienda_crear'),
    path('cbv/encomiendas/<int:pk>/editar/', views_cbv.EncomiendaUpdateView.as_view(),
         name='cbv_encomienda_editar'),

    # ── Autenticación ─────────────────────────────────────────
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('perfil/', views_auth.perfil_view, name='perfil'),
]