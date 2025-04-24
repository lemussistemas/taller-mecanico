# core/views.py
from django.shortcuts import render
from django.views.generic import ListView
from .models import Trabajo, CambioAceite, Cliente, Vehiculo
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from .forms import ClienteForm, VehiculoForm, TrabajoForm
from .models import Cliente, Vehiculo, Trabajo, CambioAceite
from django.utils import timezone
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponse
import csv


def exportar_mantenimientos_csv(request):
    # Generamos la respuesta como CSV
    ahora = timezone.now().date().isoformat()
    filename = f"mantenimientos_{ahora}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'

    writer = csv.writer(response)
    # Cabecera
    writer.writerow(['Vehículo', 'Cliente', 'Próximo km', 'Km restantes', 'Próx. fecha'])

    # Datos
    for cambio in CambioAceite.objects.select_related('vehiculo__cliente'):
        veh = cambio.vehiculo
        cliente = veh.cliente.nombre
        proximo = cambio.proximo_km
        km_rest = proximo - veh.kilometraje_actual
        prox_fecha = cambio.proxima_fecha.isoformat()
        writer.writerow([f"{veh.marca} {veh.modelo} ({veh.placa})",
                         cliente, proximo, km_rest, prox_fecha])

    return response

class ClienteList(ListView):
    model = Cliente
    template_name = 'core/cliente_list.html'
    context_object_name = 'clientes'
    ordering = ['nombre']
    paginate_by = 10

class VehiculoList(ListView):
    model = Vehiculo
    template_name = 'core/vehiculo_list.html'
    context_object_name = 'vehiculos'
    ordering = ['placa']
    paginate_by = 10



# Para Clientes
class ClienteUpdate(SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'core/cliente_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Cliente «%(nombre)s» actualizado correctamente."

class ClienteDelete(DeleteView):
    model = Cliente
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Cliente «{obj.nombre}» eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

# Para Vehículos
class VehiculoUpdate(SuccessMessageMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'core/vehiculo_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Vehículo «%(placa)s» actualizado correctamente."

class VehiculoDelete(DeleteView):
    model = Vehiculo
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Vehículo «{obj.placa}» eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

# Para Trabajos
class TrabajoUpdate(SuccessMessageMixin, CreateView):
    model = Trabajo
    form_class = TrabajoForm
    template_name = 'core/trabajo_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Trabajo #{object.id} creado correctamente."

class TrabajoDelete(CreateView):
    model = Trabajo
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Trabajo #{object.id} actualizado correctamente."
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Trabajo #{obj.id} eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

class ListaTrabajos(ListView):
    model = Trabajo
    template_name = 'core/lista_trabajos.html'
    context_object_name = 'trabajos'
    ordering = ['-fecha_ingreso']
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        tecnico = self.request.GET.get('tecnico', '').strip()
        fecha_desde = self.request.GET.get('fecha_desde', '').strip()
        fecha_hasta = self.request.GET.get('fecha_hasta', '').strip()

        # Filtrar por técnico
        if tecnico:
            qs = qs.filter(tecnico__icontains=tecnico)

        # Filtrar por fecha desde
        if fecha_desde:
            try:
                d = datetime.strptime(fecha_desde, '%Y-%m-%d')
                qs = qs.filter(fecha_ingreso__date__gte=d)
            except ValueError:
                pass

        # Filtrar por fecha hasta
        if fecha_hasta:
            try:
                h = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                qs = qs.filter(fecha_ingreso__date__lte=h)
            except ValueError:
                pass

        return qs
    
class MantenimientoList(ListView):
    template_name = 'core/mantenimientos.html'
    context_object_name = 'mantenimientos'

    def get_queryset(self):
        mantenimientos = []
        # Recorre cada registro de cambio de aceite
        for cambio in CambioAceite.objects.select_related('vehiculo__cliente'):
            veh = cambio.vehiculo
            km_restantes = cambio.proximo_km - veh.kilometraje_actual
            # Calcula meses restantes (aprox.)
            dias = (cambio.proxima_fecha - cambio.fecha_cambio).days
            meses_restantes = dias / 30
            mantenimientos.append({
                'vehiculo': f"{veh.marca} {veh.modelo} ({veh.placa})",
                'cliente': veh.cliente,
                'proximo_km': cambio.proximo_km,
                'km_restantes': km_restantes,
                'proxima_fecha': cambio.proxima_fecha,
                'meses_restantes': round(meses_restantes, 1),
            })
        return mantenimientos

# Create your views here.
class ClienteCreate(SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'core/cliente_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Cliente «%(nombre)s» creado correctamente."

class VehiculoCreate(SuccessMessageMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'core/vehiculo_form.html'
    success_url = reverse_lazy('lista_trabajos')

class TrabajoCreate(SuccessMessageMixin, CreateView):
    model = Trabajo
    form_class = TrabajoForm
    template_name = 'core/trabajo_form.html'
    success_url = reverse_lazy('lista_trabajos')

    def form_valid(self, form):
        # Al guardar el trabajo, actualiza kilometraje y crea CambioAceite si aplica
        trabajo = form.save(commit=False)
        trabajo.fecha_ingreso = timezone.now()
        trabajo.save()
        # Actualizar kilometraje del vehículo
        veh = trabajo.vehiculo
        if trabajo.kilometraje_registrado and trabajo.kilometraje_registrado > veh.kilometraje_actual:
            veh.kilometraje_actual = trabajo.kilometraje_registrado
            veh.save()
        # Si es cambio de aceite, registrar también en CambioAceite
        if trabajo.tipo == 'ACE':
            CambioAceite.objects.create(
                vehiculo=veh,
                fecha_cambio=trabajo.fecha_salida or timezone.now().date(),
                km_cambio=trabajo.kilometraje_registrado or veh.kilometraje_actual
            )
        return super().form_valid(form)