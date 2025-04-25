# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.ListaTrabajos.as_view(), name='lista_trabajos'),
    path('mantenimientos/', views.MantenimientoList.as_view(), name='mantenimientos'),

 

    # Listados
    path('clientes/', views.ClienteList.as_view(), name='cliente_list'),
    path('vehiculos/', views.VehiculoList.as_view(), name='vehiculo_list'),

    # Nuevo
    path('clientes/nuevo/', views.ClienteCreate.as_view(), name='cliente_nuevo'),
    path('vehiculos/nuevo/', views.VehiculoCreate.as_view(), name='vehiculo_nuevo'),
    path('trabajos/nuevo/', views.TrabajoCreate.as_view(), name='trabajo_nuevo'),

    # Editar
    path('clientes/<int:pk>/editar/', views.ClienteUpdate.as_view(), name='cliente_edit'),
    path('vehiculos/<int:pk>/editar/', views.VehiculoUpdate.as_view(), name='vehiculo_edit'),
    path('trabajos/<int:pk>/editar/', views.TrabajoUpdate.as_view(), name='trabajo_edit'),

    # Eliminar
    path('clientes/<int:pk>/eliminar/', views.ClienteDelete.as_view(), name='cliente_delete'),
    path('vehiculos/<int:pk>/eliminar/', views.VehiculoDelete.as_view(), name='vehiculo_delete'),
    path('trabajos/<int:pk>/eliminar/', views.TrabajoDelete.as_view(), name='trabajo_delete'),

    #exportar
    path('mantenimientos/exportar/', views.exportar_mantenimientos_csv, name='mantenimientos_exportar'),

#factura
path('trabajos/<int:pk>/factura/', views.generar_factura, name='trabajo_factura'),
]


