from django.contrib import admin
from .models import Cliente, Vehiculo, Trabajo, CambioAceite, Servicio, EstimadoReparacion, DetalleEstimado

admin.site.register(Cliente)
admin.site.register(Vehiculo)
admin.site.register(Trabajo)
admin.site.register(CambioAceite)
admin.site.register(Servicio)
admin.site.register(EstimadoReparacion)
admin.site.register(DetalleEstimado)