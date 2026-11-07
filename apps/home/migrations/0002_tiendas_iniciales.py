"""MR-117: carga las 3 tiendas que antes estaban escritas en la plantilla tiendas.html.

Las coordenadas son referenciales (zona descrita en el sitio original) y se pueden
ajustar desde el panel de administración.
"""
from decimal import Decimal

from django.db import migrations

TIENDAS = [
    dict(nombre="Tienda Santiago", ciudad="Santiago", direccion="Centro de Santiago, cerca de la Plaza de Armas",
         descripcion="En pleno centro de Santiago", horario_semana="9:00 – 19:00", horario_sabado="10:00 – 18:00",
         horario_domingo="11:00 – 17:00", latitud=Decimal("-33.437800"), longitud=Decimal("-70.650500"),
         foto_estatica="Home/img/local1.png", orden=1),
    dict(nombre="Tienda Puerto Montt", ciudad="Puerto Montt", direccion="Costanera de Puerto Montt, a pasos del puerto",
         descripcion="A pasos del puerto de la ciudad", horario_semana="8:30 – 19:00", horario_sabado="9:00 – 20:00",
         horario_domingo="10:00 – 17:00", latitud=Decimal("-41.471700"), longitud=Decimal("-72.939600"),
         foto_estatica="Home/img/local2.png", orden=2),
    dict(nombre="Tienda Viña del Mar", ciudad="Viña del Mar", direccion="Av. Perú, costanera de Viña del Mar",
         descripcion="En la costanera", horario_semana="8:30 – 22:30", horario_sabado="9:30 – 22:00",
         horario_domingo="Cerrado", latitud=Decimal("-33.018600"), longitud=Decimal("-71.555400"),
         foto_estatica="Home/img/local3.png", orden=3),
]


def cargar(apps, schema_editor):
    Tienda = apps.get_model("home", "Tienda")
    for datos in TIENDAS:
        Tienda.objects.get_or_create(nombre=datos["nombre"], defaults=datos)


def borrar(apps, schema_editor):
    apps.get_model("home", "Tienda").objects.filter(nombre__in=[t["nombre"] for t in TIENDAS]).delete()


class Migration(migrations.Migration):
    dependencies = [("home", "0001_tienda")]
    operations = [migrations.RunPython(cargar, borrar)]
