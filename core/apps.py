# core/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_roles(sender, **kwargs):
    # Importamos aquí para evitar AppRegistryNotReady
    from django.contrib.auth.models import Group, Permission

    roles = {
        'Dueño': [
            'add_trabajo','change_trabajo','delete_trabajo','view_trabajo',
            'add_servicio','change_servicio','delete_servicio','view_servicio',
            'add_cliente','change_cliente','delete_cliente','view_cliente',
            'add_vehiculo','change_vehiculo','delete_vehiculo','view_vehiculo',
        ],
        'Técnico': [
            'add_trabajo','change_trabajo','view_trabajo',
            'add_servicio','change_servicio','view_servicio',
        ],
    }
    for role_name, perm_codenames in roles.items():
        group, created = Group.objects.get_or_create(name=role_name)
        for codename in perm_codenames:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Conectar señal para crear grupos tras migraciones
        post_migrate.connect(create_roles, sender=self)
