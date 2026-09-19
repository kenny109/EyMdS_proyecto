from django.contrib import admin
from rangefilter.filters import NumericRangeFilterBuilder, DateRangeFilterBuilder

from . import models

admin.site.site_title = "Productos"

@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion",)
    list_filter = ("nombre",)
    search_fields = ("nombre", "descripcion",)


@admin.register(models.Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "cantidad", "umbral_minimo", "fecha_ingreso", "imagen",)
    list_display_links = ("nombre",)
    list_filter = (
        "categoria",
        ("precio", NumericRangeFilterBuilder()),
        "cantidad",
        ("fecha_ingreso", DateRangeFilterBuilder()),
    )
    search_fields = ("nombre", "categoria__nombre",)
    ordering = ("nombre", "categoria", "fecha_ingreso")