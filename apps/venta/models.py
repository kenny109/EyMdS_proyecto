import logging
import smtplib

from django.db import models, transaction
from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from productos.models import Productos
from productos.views import enviar_notificacion_stock_bajo

logger = logging.getLogger(__name__)

class Vendedor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendedor")  
    celular = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)

    def __str__(self):
        return self.usuario.username

class Venta(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING)
    precio_total = models.PositiveIntegerField(editable=False, null=True)
    fecha_venta = models.DateTimeField(default=timezone.now, editable=False)

    def actualizar_precio_total(self):
        if self.pk is not None:  # Verifica si ya tiene una clave primaria asignada
            precio_total = sum(vp.precio_por_cantidad() for vp in self.ventaproducto_set.all())
            self.precio_total = precio_total if precio_total else 0

    def save(self, *args, **kwargs):
        if not self.id:  # Si es una nueva venta
            self.actualizar_precio_total()
        super(Venta, self).save(*args, **kwargs)

    def __str__(self):
        productos = ", ".join([vp.producto.nombre for vp in self.ventaproducto_set.all()])
        return f'Venta #{self.id} - {productos}'

    class Meta:
        ordering = ("-fecha_venta",)

class VentaProducto(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey("productos.Productos", on_delete=models.DO_NOTHING)
    cantidad = models.PositiveIntegerField(null=False, blank=False)

    def precio_por_cantidad(self):
        return self.producto.precio * self.cantidad

    # ------------------------------------------------------------------ MR-120
    # Antes el stock se descontaba dentro de clean() (la validación del formulario):
    # cada validación repetida volvía a descontar y borrar/editar una venta no devolvía nada.
    # Ahora clean() solo valida y el movimiento de stock ocurre una sola vez, al guardar.

    def _cantidad_previa(self):
        """Cantidad ya descontada de ESTE producto por esta línea (0 si es nueva o cambió de producto)."""
        if not self.pk:
            return 0
        anterior = VentaProducto.objects.filter(pk=self.pk).values("producto_id", "cantidad").first()
        if not anterior or anterior["producto_id"] != self.producto_id:
            return 0
        return anterior["cantidad"]

    def clean(self):
        if not self.cantidad:
            raise ValidationError("No puedes vender 0 productos")
        if self.producto_id is None:
            return
        adicional = self.cantidad - self._cantidad_previa()
        if adicional > self.producto.cantidad:
            raise ValidationError(
                f"La cantidad solicitada es mayor al stock disponible ({self.producto.cantidad} unidades)"
            )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            anterior = None
            if self.pk:
                anterior = VentaProducto.objects.select_for_update().filter(pk=self.pk).values(
                    "producto_id", "cantidad").first()
            if anterior and anterior["producto_id"] != self.producto_id:
                # Cambió el producto: se devuelve el stock al anterior y se descuenta completo del nuevo
                Productos.objects.filter(pk=anterior["producto_id"]).update(cantidad=F("cantidad") + anterior["cantidad"])
                delta = self.cantidad
            else:
                delta = self.cantidad - (anterior["cantidad"] if anterior else 0)
            super().save(*args, **kwargs)
            if delta:
                Productos.objects.filter(pk=self.producto_id).update(cantidad=F("cantidad") - delta)
                self.producto.refresh_from_db(fields=["cantidad"])
        if delta > 0:
            self._avisar_stock_bajo()
        self.venta.actualizar_precio_total()
        self.venta.save()

    def _avisar_stock_bajo(self):
        umbral = self.producto.umbral_minimo
        if umbral is not None and self.producto.cantidad <= umbral:
            try:
                enviar_notificacion_stock_bajo(self.producto)
            except (smtplib.SMTPException, OSError):
                # Un problema con el correo no debe impedir registrar la venta
                logger.exception("No se pudo enviar el aviso de stock bajo de %s", self.producto)

    def __str__(self):
        return f'{self.venta.id} - {self.producto.nombre} - Cantidad: {self.cantidad}'


@receiver(pre_delete, sender=VentaProducto)
def devolver_stock(sender, instance, **kwargs):
    """MR-120: al borrar una línea (o la venta completa) el stock vuelve al producto."""
    Productos.objects.filter(pk=instance.producto_id).update(cantidad=F("cantidad") + instance.cantidad)
