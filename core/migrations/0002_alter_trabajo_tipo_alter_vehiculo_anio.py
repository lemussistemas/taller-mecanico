# Generated by Django 5.2 on 2025-04-24 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajo',
            name='tipo',
            field=models.CharField(choices=[('GEN', 'Genérico'), ('ACE', 'Cambio de aceite'), ('FRE', 'Cambio de frenos'), ('PAR', 'Cambio de pastillas de freno'), ('DIS', 'Cambio de discos de freno'), ('BAL', 'Balanceo'), ('ALI', 'Alineación'), ('COR', 'Cambio de correa de distribución'), ('FLT', 'Cambio de filtro de aire'), ('FCO', 'Cambio de filtro de combustible'), ('FOI', 'Cambio de filtro de aceite'), ('SUS', 'Revisión de suspensión'), ('AMO', 'Ajuste de motor'), ('RMO', 'Reparación de motor'), ('ABS', 'Inspección del sistema ABS'), ('EMI', 'Emisión de gases'), ('ELE', 'Reparación eléctrica'), ('ACD', 'Carga de aire acondicionado'), ('ESC', 'Revisión de escape'), ('LUB', 'Lubricación general'), ('INJ', 'Limpieza de inyectores')], default='GEN', max_length=3),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='anio',
            field=models.PositiveSmallIntegerField(verbose_name='Año'),
        ),
    ]
