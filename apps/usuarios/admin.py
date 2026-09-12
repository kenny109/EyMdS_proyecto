from django.contrib import admin

# Register your models here.

from . import models

@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre","apellido","correo","edad",)
    list_filter = ("nombre","apellido","edad",)
    search_fields = ("nombre","apellido","correo","edad",)