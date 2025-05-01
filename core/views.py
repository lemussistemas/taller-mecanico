# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import os
import csv
from django.views import View

from .models import Cliente, Vehiculo, Trabajo, CambioAceite, Servicio, EstimadoReparacion, DetalleEstimado
from .forms import ClienteForm, VehiculoForm, TrabajoForm, ServicioFormSet, EstimadoForm, DetalleEstimadoFormSet

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter



@login_required(login_url='login')
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
    # Lista de servicios asociados
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Servicios:")
    y -= 20
    p.setFont("Helvetica", 12)
    for servicio in trabajo.servicios.all():
        # Etiqueta + descripción
        desc = servicio.descripcion or servicio.get_tipo_display()
        p.drawString(70, y, f"- {servicio.get_tipo_display()}: {desc}")
        y -= 15
        # Costos por servicio
        p.drawString(90, y,
            f"Partes: L {servicio.costo_partes:.2f}   "
            f"Mano de obra: L {servicio.costo_mano_obra:.2f}   "
            f"Total: L {servicio.total:.2f}")
        y -= 25
        
   
     # Detalle de servicios y total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Servicios:")
    y -= 20
    p.setFont("Helvetica", 12)
    for servicio in trabajo.servicios.all():
         desc = servicio.descripcion or servicio.get_tipo_display()
         p.drawString(70, y, f"- {servicio.get_tipo_display()}: {desc}")
         y -= 15
         p.drawString(90, y,
             f"Partes: L {servicio.costo_partes:.2f}   "
             f"Mano de obra: L {servicio.costo_mano_obra:.2f}   "
             f"Total: L {servicio.total:.2f}")
         y -= 25

     # Total general (suma de todos los servicios)
    total_general = sum(s.total for s in trabajo.servicios.all())
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Total a Pagar: L {total_general:.2f}")

     # Finaliza y guarda
    p.showPage()
    p.save()

    return response

   

  


@login_required(login_url='login')
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

class ClienteList(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'core/cliente_list.html'
    context_object_name = 'clientes'
    ordering = ['nombre']
    paginate_by = 10

class VehiculoList(LoginRequiredMixin, ListView):
    model = Vehiculo
    template_name = 'core/vehiculo_list.html'
    context_object_name = 'vehiculos'
    ordering = ['placa']
    paginate_by = 10



# Para Clientes
class ClienteUpdate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'core/cliente_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Cliente «%(nombre)s» actualizado correctamente."

class ClienteDelete(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Cliente «{obj.nombre}» eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

# Para Vehículos
class VehiculoUpdate(LoginRequiredMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'core/vehiculo_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Vehículo «%(placa)s» actualizado correctamente."

class VehiculoDelete(LoginRequiredMixin, DeleteView):
    model = Vehiculo
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Vehículo «{obj.placa}» eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

# Para Trabajos
class TrabajoUpdate(LoginRequiredMixin, UpdateView):
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

class TrabajoDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Trabajo
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('lista_trabajos')
    def test_func(self):
        return self.request.user.groups.filter(name='Dueño').exists()

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para eliminar trabajos.")
        return redirect('lista_trabajos')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Trabajo #{obj.id} eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Trabajo #{obj.id} eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
    
class ListaTrabajos(LoginRequiredMixin, ListView):
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
    
class MantenimientoList(LoginRequiredMixin, ListView):
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
class ClienteCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'core/cliente_form.html'
    success_url = reverse_lazy('lista_trabajos')
    success_message = "Cliente «%(nombre)s» creado correctamente."

class VehiculoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'core/vehiculo_form.html'
    success_url = reverse_lazy('lista_trabajos')

class TrabajoCreate(LoginRequiredMixin, CreateView):
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
    

  


    


def generar_estimado_pdf(request, pk):
    estimado = get_object_or_404(EstimadoReparacion, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="estimado_{estimado.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Estimado de Reparación")
    y -= 40

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Cliente: {estimado.cliente.nombre}")
    y -= 20
    p.drawString(50, y, f"Vehículo: {estimado.vehiculo.marca} {estimado.vehiculo.modelo} ({estimado.vehiculo.placa})")
    y -= 20
    p.drawString(50, y, f"Fecha: {estimado.fecha.isoformat()}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Detalles:")
    y -= 20
    p.setFont("Helvetica", 12)

    total = 0
    for detalle in estimado.detalles.all():
        if y < 100:
            p.showPage()
            y = height - 50
        p.drawString(60, y, f"{detalle.descripcion} | Partes: L {detalle.costo_partes:.2f} | Mano de Obra: L {detalle.costo_mano_obra:.2f} | Total: L {detalle.total:.2f}")
        total += detalle.total
        y -= 20

    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"TOTAL: L {total:.2f}")

    p.showPage()
    p.save()
    return response


class EstimadoListView(ListView):
    model = EstimadoReparacion
    template_name = 'core/estimado_list.html'
    context_object_name = 'estimados'

class EstimadoCreateView(View):
    template_name = 'core/estimado_form.html'

    def get(self, request, *args, **kwargs):
        form = EstimadoForm()
        formset = DetalleEstimadoFormSet()
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        form = EstimadoForm(request.POST)
        formset = DetalleEstimadoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            estimado = form.save()
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.estimado = estimado
                detalle.save()
            return redirect('estimado_list')  # o la vista que prefieras
        return render(request, self.template_name, {'form': form, 'formset': formset})
    


class EstimadoUpdateView(UpdateView):
    model = EstimadoReparacion
    form_class = EstimadoForm
    template_name = 'core/estimado_form.html'
    success_url = reverse_lazy('estimado_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetalleEstimadoFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DetalleEstimadoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Estimado actualizado correctamente.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class EstimadoDeleteView(DeleteView):
    model = EstimadoReparacion
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('estimado_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Estimado #{obj.id} eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
