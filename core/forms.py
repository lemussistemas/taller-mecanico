from django import forms
from .models import Cliente, Vehiculo, Trabajo

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
        fields = [
            'vehiculo', 'tecnico', 'tipo', 'kilometraje_registrado',
            'descripcion', 'costo_partes', 'costo_mano_obra', 'precio_cobrado'
        ]
