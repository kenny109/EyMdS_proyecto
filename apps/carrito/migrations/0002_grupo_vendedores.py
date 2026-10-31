"""MR-116: grupo "Vendedores" con los permisos para atender reservas.

Un usuario staff en este grupo puede ver todas las reservas y cambiar su estado
(retirada / cancelada / vencida) sin ser superusuario.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

PERMISOS = [
    ("carrito", "view_reserva"),
    ("carrito", "change_reserva"),
    ("carrito", "gestionar_reservas"),
    ("carrito", "view_detallereserva"),
    ("usuarios", "view_cliente"),
]


def crear_grupo(apps, schema_editor):
    # Los permisos se crean normalmente después de migrar; se fuerzan aquí para poder asignarlos.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    grupo, _ = Group.objects.get_or_create(name="Vendedores")
    for app_label, codename in PERMISOS:
        perm = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if perm:
            grupo.permissions.add(perm)


def borrar_grupo(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name="Vendedores").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("carrito", "0001_initial"),
        ("usuarios", "0002_cliente"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]
    operations = [migrations.RunPython(crear_grupo, borrar_grupo)]
