from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from productos.views import enviar_notificacion_stock_bajo

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.venta.actualizar_precio_total()
        self.venta.save()

    def __str__(self):
        return f'{self.venta.id} - {self.producto.nombre} - Cantidad: {self.cantidad}'

    def clean(self):
        if self.cantidad > self.producto.cantidad:
            raise ValidationError("La cantidad solicitada es mayor al stock disponible")
        elif self.cantidad == 0:
            raise ValidationError("No puedes vender 0 productos")
        else: 
            self.producto.cantidad -= self.cantidad
            self.producto.save()
            if self.producto.cantidad <= self.producto.umbral_minimo:
                enviar_notificacion_stock_bajo(self.producto)
