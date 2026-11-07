from django.db import models


class Tienda(models.Model):
    """Local físico de Almacén Los Tíos (MR-117). Editable desde el panel de administración.

    Las coordenadas se usan para el minimapa de la pantalla de tiendas (MR-118).
    """
    nombre = models.CharField(max_length=80)
    ciudad = models.CharField(max_length=60)
    direccion = models.CharField("dirección", max_length=150)
    descripcion = models.CharField("descripción", max_length=150, blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    horario_semana = models.CharField("lunes a viernes", max_length=40)
    horario_sabado = models.CharField("sábados", max_length=40)
    horario_domingo = models.CharField("domingos", max_length=40)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    foto = models.ImageField(upload_to="tiendas", blank=True, null=True)
    foto_estatica = models.CharField(
        max_length=100, blank=True, help_text="Imagen de respaldo en static/ si no se sube una foto."
    )
    activa = models.BooleanField(default=True, help_text="Desmarcar para ocultarla del sitio.")
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "tienda"
        verbose_name_plural = "tiendas"
        ordering = ("orden", "nombre")

    def __str__(self):
        return self.nombre

    @property
    def como_llegar_url(self):
        """Enlace a Google Maps con la ruta hasta la tienda."""
        return f"https://www.google.com/maps/dir/?api=1&destination={self.latitud},{self.longitud}"
