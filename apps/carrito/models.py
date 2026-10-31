import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone

PLAZO_RETIRO = timedelta(hours=24)


def generar_codigo():
    """Código corto y legible para que el cliente lo muestre en la tienda: LT-7F3K9Q."""
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para evitar confusiones
    return "LT-" + "".join(secrets.choice(alfabeto) for _ in range(6))


class Reserva(models.Model):
    """Registro de cada solicitud de reserva enviada desde el carrito (MR-116)."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de retiro"
        RETIRADA = "retirada", "Retirada"
        CANCELADA = "cancelada", "Cancelada"
        VENCIDA = "vencida", "Vencida"

    codigo = models.CharField("código", max_length=12, unique=True, default=generar_codigo, editable=False)
    cliente = models.ForeignKey(
        "usuarios.Cliente", on_delete=models.SET_NULL, null=True, blank=True, related_name="reservas"
    )
    correo = models.EmailField("correo del cliente")
    total = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    creada = models.DateTimeField("creada el", default=timezone.now, editable=False)
    vence = models.DateTimeField("vence el", editable=False)
    actualizada = models.DateTimeField("última actualización", auto_now=True)
    gestionada_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reservas_gestionadas",
        verbose_name="gestionada por",
    )

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ("-creada",)
        permissions = [
            ("gestionar_reservas", "Puede marcar reservas como retiradas, canceladas o vencidas"),
        ]

    def __str__(self):
        return f"{self.codigo} · {self.correo}"

    def save(self, *args, **kwargs):
        if not self.vence:
            self.vence = (self.creada or timezone.now()) + PLAZO_RETIRO
        super().save(*args, **kwargs)

    @property
    def esta_vencida(self):
        """Pendiente y con el plazo de 24 h cumplido (aún no marcada como vencida)."""
        return self.estado == self.Estado.PENDIENTE and timezone.now() > self.vence

    @property
    def cantidad_items(self):
        return sum(d.cantidad for d in self.detalles.all())


class DetalleReserva(models.Model):
    """Un producto dentro de una reserva. Guarda nombre y precio del momento de la reserva."""

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey("productos.Productos", on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    precio = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = "producto reservado"
        verbose_name_plural = "productos reservados"

    def __str__(self):
        return f"{self.cantidad} x {self.nombre}"

    @property
    def subtotal(self):
        return self.precio * self.cantidad
