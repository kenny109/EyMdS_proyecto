from django.contrib import admin
from django.db import models

# Register your models here.

from . import models

admin.site.site_title = "Productos"

@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Heredo varias funcionalidades para ver en el panel
    ## Con esta, veo en el panel nombre y descripcion
    list_display = ("nombre", "descripcion",)
    list_filter = ("nombre",)
    search_fields = ("nombre","descripcion",)

@admin.register(models.Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "cantidad","fecha_ingreso","categoria","umbral_minimo","imagen",)
    list_display_links = ("nombre",)
    list_filter = ("nombre","precio","cantidad","fecha_ingreso","categoria",)
    search_fields = ("nombre","precio","cantidad","fecha_ingreso","categoria",)
    ordering = ("nombre", "categoria", "fecha_ingreso")
