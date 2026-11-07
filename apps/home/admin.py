from django.contrib import admin

from .models import Tienda


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    """MR-117: las tiendas se administran sin tocar el código."""
    list_display = ("nombre", "ciudad", "direccion", "telefono", "activa", "orden")
    list_editable = ("activa", "orden")
    list_filter = ("activa", "ciudad")
    search_fields = ("nombre", "ciudad", "direccion")
    fieldsets = (
        (None, {"fields": ("nombre", "ciudad", "direccion", "descripcion", "telefono", "activa", "orden")}),
        ("Horario", {"fields": ("horario_semana", "horario_sabado", "horario_domingo")}),
        ("Ubicación en el mapa (MR-118)", {"fields": ("latitud", "longitud"),
                                           "description": "Coordenadas en grados decimales (clic derecho en Google Maps → copiar)."}),
        ("Imagen", {"fields": ("foto", "foto_estatica")}),
    )
