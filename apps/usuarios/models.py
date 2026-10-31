from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=20, null=False)
    apellido = models.CharField(max_length=20, null=False)
    correo = models.CharField(max_length=50, null=False)
    edad = models.IntegerField()
    def __str__(self):
        return f'{self.nombre} {self.apellido}. {self.correo}. Tiene {self.edad} años'
    


class Cliente(models.Model):
    """Cuenta de cliente de la tienda (MR-115).

    Se apoya en el usuario de Django (auth.User) para el inicio de sesión;
    aquí se guardan los datos propios del cliente. Un cliente nunca es staff.
    """
    usuario = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="cliente"
    )
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    fecha_registro = models.DateTimeField("fecha de registro", auto_now_add=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ("-fecha_registro",)

    def __str__(self):
        nombre = self.usuario.get_full_name()
        return f"{nombre} ({self.usuario.username})" if nombre else self.usuario.username

    @property
    def correo(self):
        return self.usuario.email
