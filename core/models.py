from django.db import models
from django.utils import timezone
from datetime import timedelta

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    placa = models.CharField(max_length=20)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveSmallIntegerField(verbose_name="Año")
    kilometraje_actual = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.marca} {self.modelo} – {self.placa}"

class Trabajo(models.Model):
    TIPOS = [
        ('GEN', 'Genérico'),
        ('ACE', 'Cambio de aceite'),
    ]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    tecnico = models.CharField(max_length=100)
    tipo = models.CharField(max_length=3, choices=TIPOS, default='GEN')
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    kilometraje_registrado = models.PositiveIntegerField(null=True, blank=True)
    descripcion = models.TextField()
    costo_partes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def ganancia(self):
        return self.precio_cobrado - (self.costo_partes + self.costo_mano_obra)

    def __str__(self):
        return f"Trabajo #{self.id} – {self.get_tipo_display()}"

class CambioAceite(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha_cambio = models.DateField()
    km_cambio = models.PositiveIntegerField()
    intervalo_km = models.PositiveIntegerField(default=5000)
    intervalo_meses = models.PositiveSmallIntegerField(default=3)

    @property
    def proximo_km(self):
        return self.km_cambio + self.intervalo_km

    @property
    def proxima_fecha(self):
        return self.fecha_cambio + timedelta(days=30*self.intervalo_meses)

    def __str__(self):
        return f"Cambio de aceite #{self.id} – {self.vehiculo}"
