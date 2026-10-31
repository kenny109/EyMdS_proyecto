from django.contrib import admin

from . import models


@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "correo", "edad",)
    list_filter = ("nombre", "apellido", "edad",)
    search_fields = ("nombre", "apellido", "correo", "edad",)


@admin.register(models.Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """MR-115: clientes registrados desde el sitio."""
    list_display = ("usuario", "nombre_completo", "correo", "telefono", "total_reservas", "fecha_registro")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "usuario__email", "telefono")
    list_filter = ("fecha_registro",)
    readonly_fields = ("fecha_registro",)

    @admin.display(description="Nombre")
    def nombre_completo(self, obj):
        return obj.usuario.get_full_name()

    @admin.display(description="Reservas")
    def total_reservas(self, obj):
        return obj.reservas.count()
