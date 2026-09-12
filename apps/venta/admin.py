from django.contrib import admin
from .models import Venta, VentaProducto, Vendedor
from . import models

@admin.register(models.Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    ...

class VentaProductoInline(admin.TabularInline):
    model = VentaProducto

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_productos', 'get_cantidad', 'precio_total', 'fecha_venta')

    def get_productos(self, obj):
        return ", ".join([vp.producto.nombre for vp in obj.ventaproducto_set.all()])
    get_productos.short_description = 'Productos'

    def get_cantidad(self, obj):
        return ", ".join([str(vp.cantidad) for vp in obj.ventaproducto_set.all()])
    get_cantidad.short_description = 'Cantidad'

    inlines = [
        VentaProductoInline,
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.actualizar_precio_total()  # Actualizar precio_total después de agregar los productos
        form.instance.save()

admin.site.register(Venta, VentaAdmin)
