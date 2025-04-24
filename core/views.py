# core/views.py
from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Trabajo, CambioAceite, Cliente, Vehiculo
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from .forms import ClienteForm, VehiculoForm, TrabajoForm
from .models import Cliente, Vehiculo, Trabajo, CambioAceite
from django.utils import timezone
from django.views.generic import UpdateView, DeleteView
from django.db.models import Q
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponse
import csv
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.utils import timezone
from .models import Trabajo
from .forms import ServicioFormSet
from django.views.generic import DeleteView
def generar_factura(request, pk):
    trabajo = get_object_or_404(Trabajo, pk=pk)
    cliente = trabajo.vehiculo.cliente
    vehiculo = trabajo.vehiculo

    # Preparamos la respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{trabajo.id}.pdf"'

    # Cargo el logo desde static/img/logo.png
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')

    # Lienzo ReportLab
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Dibujo el logo (200x50px) en la esquina superior izquierda
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 50, height - 80, width=200, height=50, preserveAspectRatio=True)

    # Título
    p.setFont("Helvetica-Bold", 18)
    p.drawString(270, height - 60, "Factura de Servicio")

    # Línea separadora
    p.setLineWidth(1)
    p.line(50, height - 90, width - 50, height - 90)

    # Información básica (salto de 30)
    y = height - 120
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Factura #: {trabajo.id}")
    p.drawString(300, y, f"Fecha: {timezone.now().date().isoformat()}")
    y -= 30

    # Datos del cliente
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Cliente:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(70, y, f"{cliente.nombre} | {cliente.telefono}")
    y -= 20
    p.drawString(70, y, cliente.direccion)
    y -= 30

    # Datos del vehículo
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Vehículo:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(70, y, f"{vehiculo.marca} {vehiculo.modelo} (Placa: {vehiculo.placa})")
    y -= 30

    # Detalle de servicio
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Detalle del Servicio:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(70, y, f"{trabajo.get_tipo_display()}: {trabajo.descripcion[:40]}{'...' if len(trabajo.descripcion)>40 else ''}")
    y -= 30

    # Costos y total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Resumen de Costos:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(70, y, f"Partes: L {trabajo.costo_partes:.2f}")
    y -= 20
    p.drawString(70, y, f"Mano de obra: L {trabajo.costo_mano_obra:.2f}")
    y -= 30

    total = trabajo.costo_partes + trabajo.costo_mano_obra
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total a Pagar: L {total:.2f}")

    # Finaliza y guarda
    p.showPage()
    p.save()

    return response



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
class VehiculoUpdate(UpdateView):
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
class TrabajoUpdate(UpdateView):
    model = Trabajo
    fields = ['vehiculo', 'tecnico', 'fecha_ingreso', 'fecha_salida']
    template_name = 'core/trabajo_form.html'
    success_url = reverse_lazy('lista_trabajos')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['servicios'] = ServicioFormSet(self.request.POST, instance=self.object)
        else:
            data['servicios'] = ServicioFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        self.object = form.save()
        servicios = ServicioFormSet(self.request.POST, instance=self.object)
        if servicios.is_valid():
            servicios.save()
        return redirect(self.success_url)

class TrabajoDelete(DeleteView):
    model = Trabajo
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')

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
        for cambio in CambioAceite.objects.select_related('vehiculo__cliente'):
            veh = cambio.vehiculo
            km_restantes = cambio.proximo_km - veh.kilometraje_actual
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        due = 0
        for m in context['mantenimientos']:
            if m['km_restantes'] <= 500 or m['meses_restantes'] <= 1:
                due += 1
        context['due_count'] = due
        return context

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

class TrabajoCreate(CreateView):
    model = Trabajo
    fields = ['vehiculo', 'tecnico', 'fecha_ingreso', 'fecha_salida']
    template_name = 'core/trabajo_form.html'
    success_url = reverse_lazy('lista_trabajos')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['servicios'] = ServicioFormSet(self.request.POST)
        else:
            data['servicios'] = ServicioFormSet()
        return data

    def form_valid(self, form):
        self.object = form.save()
        servicios = ServicioFormSet(self.request.POST, instance=self.object)
        if servicios.is_valid():
            servicios.save()
        return redirect(self.success_url)