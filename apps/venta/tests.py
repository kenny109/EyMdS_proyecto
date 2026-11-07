from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from productos.models import Categoria, Productos
from venta.models import Vendedor, Venta, VentaProducto


@override_settings(DEFAULT_FROM_EMAIL="tienda@lostios.cl", STORE_EMAIL="reservas@lostios.cl")
class StockVentasTest(TestCase):
    """MR-120: el stock se mueve una sola vez por venta y vuelve al borrar o editar."""

    def setUp(self):
        cat = Categoria.objects.create(nombre="Bebidas", descripcion="d")
        self.p = Productos.objects.create(nombre="Jugo", precio=1000, cantidad=10, categoria=cat, umbral_minimo=3)
        self.otro = Productos.objects.create(nombre="Agua", precio=500, cantidad=10, categoria=cat, umbral_minimo=1)
        vendedor = Vendedor.objects.create(usuario=User.objects.create_user("v"), celular="1")
        self.venta = Venta.objects.create(vendedor=vendedor)

    def stock(self, producto=None):
        producto = producto or self.p
        producto.refresh_from_db()
        return producto.cantidad

    def test_validar_varias_veces_no_descuenta(self):
        vp = VentaProducto(venta=self.venta, producto=self.p, cantidad=2)
        vp.full_clean()
        vp.full_clean()
        self.assertEqual(self.stock(), 10)
        vp.save()
        self.assertEqual(self.stock(), 8)

    def test_editar_cantidad_ajusta_la_diferencia(self):
        vp = VentaProducto.objects.create(venta=self.venta, producto=self.p, cantidad=2)
        vp.cantidad = 5
        vp.full_clean()
        vp.save()
        self.assertEqual(self.stock(), 5)
        vp.cantidad = 1
        vp.save()
        self.assertEqual(self.stock(), 9)

    def test_cambiar_de_producto_devuelve_al_anterior(self):
        vp = VentaProducto.objects.create(venta=self.venta, producto=self.p, cantidad=2)
        vp.producto = self.otro
        vp.save()
        self.assertEqual((self.stock(), self.stock(self.otro)), (10, 8))

    def test_borrar_linea_o_venta_devuelve_stock(self):
        vp = VentaProducto.objects.create(venta=self.venta, producto=self.p, cantidad=4)
        VentaProducto.objects.create(venta=self.venta, producto=self.otro, cantidad=1)
        vp.delete()
        self.assertEqual(self.stock(), 10)
        self.venta.delete()  # borrado en cascada desde el admin
        self.assertEqual(self.stock(self.otro), 10)

    def test_no_permite_vender_mas_que_el_stock(self):
        with self.assertRaises(ValidationError):
            VentaProducto(venta=self.venta, producto=self.p, cantidad=11).full_clean()
        vp = VentaProducto.objects.create(venta=self.venta, producto=self.p, cantidad=8)
        vp.cantidad = 10  # sube 2 y quedan 2 en stock: es válido
        vp.full_clean()
        vp.cantidad = 11
        with self.assertRaises(ValidationError):
            vp.full_clean()

    def test_aviso_de_stock_bajo_una_sola_vez(self):
        vp = VentaProducto(venta=self.venta, producto=self.p, cantidad=7)
        vp.full_clean()
        vp.full_clean()
        vp.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.venta.precio_total, 7000)

    def test_falla_del_correo_no_impide_la_venta(self):
        from unittest.mock import patch
        import smtplib
        with patch("venta.models.enviar_notificacion_stock_bajo", side_effect=smtplib.SMTPException("caído")):
            VentaProducto.objects.create(venta=self.venta, producto=self.p, cantidad=8)
        self.assertEqual(self.stock(), 2)
