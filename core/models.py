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
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    tecnico = models.CharField(max_length=100)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    kilometraje_registrado = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Trabajo #{self.id} – {self.vehiculo}"

    @property
    def ganancia(self):
        # Suma el total de cada servicio asociado
        return sum(servicio.total for servicio in self.servicios.all())

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

class Servicio(models.Model):
    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name='servicios'
    )
    tipo = models.CharField(
        max_length=3,
        choices=[
            ('GEN', 'Genérico'),
            ('ACE', 'Cambio de aceite'),
            ('FRE', 'Cambio de frenos'),
            ('PAR', 'Cambio de pastillas de freno'),
            ('DIS', 'Cambio de discos de freno'),
            ('BAL', 'Balanceo'),
            ('ALI', 'Alineación'),
            ('COR', 'Cambio de correa de distribución'),
            ('FLT', 'Cambio de filtro de aire'),
            ('FCO', 'Cambio de filtro de combustible'),
            ('FOI', 'Cambio de filtro de aceite'),
            ('SUS', 'Revisión de suspensión'),
            ('AMO', 'Ajuste de motor'),
            ('RMO', 'Reparación de motor'),
            ('ABS', 'Inspección del sistema ABS'),
            ('ELE', 'Reparación eléctrica'),
            ('ACD', 'Carga de aire acondicionado'),
            ('ESC', 'Revisión de escape'),
            ('LUB', 'Lubricación general'),
            ('INJ', 'Limpieza de inyectores'),
        ],
    )
    descripcion = models.TextField(blank=True)
    costo_partes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total(self):
        return self.costo_partes + self.costo_mano_obra

    def __str__(self):
        return f"{self.get_tipo_display()} (#{self.pk})"