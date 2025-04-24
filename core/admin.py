from django.contrib import admin
from .models import Cliente, Vehiculo, Trabajo, CambioAceite

admin.site.register(Cliente)
admin.site.register(Vehiculo)
admin.site.register(Trabajo)
admin.site.register(CambioAceite)
