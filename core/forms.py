from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Vehiculo, Trabajo, Servicio

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'direccion']

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'placa', 'marca', 'modelo', 'anio', 'kilometraje_actual']

class TrabajoForm(forms.ModelForm):
    class Meta:
        model = Trabajo
        fields = ['vehiculo', 'tecnico', 'fecha_ingreso', 'fecha_salida', 'kilometraje_registrado']

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['tipo', 'descripcion', 'costo_partes', 'costo_mano_obra']

ServicioFormSet = inlineformset_factory(
    Trabajo, Servicio,
    form=ServicioForm,
    extra=1,    # número de formularios en blanco
    can_delete=True
)
