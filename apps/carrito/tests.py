from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from productos.models import Productos, Categoria
from carrito.cart import Carrito


class CarritoTestCase(TestCase):
    def setUp(self):
        # Creamos una request "falsa" con sesión, porque Carrito la necesita
        self.factory = RequestFactory()

        self.request = self.factory.get("/")
        SessionMiddleware(lambda r: None).process_request(self.request)
        self.request.session.save()

        # Categoria es obligatoria en el modelo Productos (ForeignKey)
        self.categoria = Categoria.objects.create(
            nombre="Test", descripcion="Categoria de prueba"
        )

        self.producto = Productos.objects.create(
            nombre="Producto test",
            precio=1000,
            cantidad=5,
            categoria=self.categoria,
            umbral_minimo=1,
        )

    def test_agregar_producto_nuevo(self):
        carrito = Carrito(self.request)
        carrito.agregar_prod(self.producto)
        item = carrito.carrito[str(self.producto.id)]
        self.assertEqual(item["cantidad"], 1)
        self.assertEqual(item["precio"], self.producto.precio)

    def test_agregar_producto_respeta_stock_maximo(self):
        carrito = Carrito(self.request)
        # cantidad en stock es 5, agregamos 5 veces
        for _ in range(5):
            carrito.agregar_prod(self.producto)
        item = carrito.carrito[str(self.producto.id)]
        self.assertEqual(item["cantidad"], 5)
        # el sexto intento no debe superar el stock
        resultado = carrito.agregar_prod(self.producto)
        self.assertEqual(resultado, "No hay mas stock de este producto.")
        self.assertEqual(carrito.carrito[str(self.producto.id)]["cantidad"], 5)

    def test_restar_elimina_cuando_llega_a_cero(self):
        carrito = Carrito(self.request)
        carrito.agregar_prod(self.producto)
        carrito.restar(self.producto)
        self.assertNotIn(str(self.producto.id), carrito.carrito)

    def test_eliminar_producto(self):
        carrito = Carrito(self.request)
        carrito.agregar_prod(self.producto)
        carrito.eliminar(self.producto)
        self.assertNotIn(str(self.producto.id), carrito.carrito)

    def test_limpiar_carrito(self):
        carrito = Carrito(self.request)
        carrito.agregar_prod(self.producto)
        carrito.limpiar()
        self.assertEqual(carrito.carrito, {})
    def test_no_agrega_producto_sin_stock(self):
        # MR-112: antes un producto con stock 0 se agregaba igual con cantidad 1
        agotado = Productos.objects.create(
            nombre="Agotado", precio=500, cantidad=0, categoria=self.categoria, umbral_minimo=1
        )
        carrito = Carrito(self.request)
        resultado = carrito.agregar_prod(agotado)
        self.assertEqual(resultado, "No hay mas stock de este producto.")
        self.assertNotIn(str(agotado.id), carrito.carrito)


# --------------------------------------------------------------------------- #
#  MR-112: reserva con verificación real de reCAPTCHA y manejo de errores
# --------------------------------------------------------------------------- #
from unittest.mock import MagicMock, patch

from django.core import mail
from django.test import override_settings
from django.urls import reverse


@override_settings(DEFAULT_FROM_EMAIL="tienda@lostios.cl", STORE_EMAIL="reservas@lostios.cl")
class ReservaCarritoTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre="Bebidas", descripcion="Jugos")
        self.producto = Productos.objects.create(
            nombre="Jugo", precio=990, cantidad=3, categoria=categoria, umbral_minimo=1
        )
        self.client.get(reverse("carrito:agregar_producto", args=[self.producto.id]))

    def _google(self, success):
        respuesta = MagicMock()
        respuesta.json.return_value = {"success": success}
        return patch("carrito.views.requests.post", return_value=respuesta)

    def _reservar(self, correo="cliente@correo.com", token="token"):
        return self.client.post(
            reverse("carrito:enviar_correo"), {"correo": correo, "g-recaptcha-response": token}
        )

    def test_token_falso_es_rechazado(self):
        with self._google(False):
            respuesta = self._reservar()
        self.assertRedirects(respuesta, reverse("carrito:index"))
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(self.client.session["carrito"])  # el carrito se conserva

    def test_sin_token_es_rechazado_sin_consultar_a_google(self):
        with self._google(True) as google:
            self._reservar(token="")
        google.assert_not_called()
        self.assertEqual(len(mail.outbox), 0)

    def test_correo_invalido_es_rechazado(self):
        with self._google(True):
            self._reservar(correo="no-es-un-correo")
        self.assertEqual(len(mail.outbox), 0)

    def test_reserva_valida_envia_dos_correos_desde_la_tienda(self):
        with self._google(True):
            respuesta = self._reservar()
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "carrito/confirmacion.html")
        self.assertEqual(len(mail.outbox), 2)
        cliente, tienda = mail.outbox
        self.assertEqual(cliente.from_email, "tienda@lostios.cl")
        self.assertEqual(cliente.to, ["cliente@correo.com"])
        self.assertEqual(tienda.to, ["reservas@lostios.cl"])
        self.assertEqual(tienda.reply_to, ["cliente@correo.com"])
        self.assertFalse(self.client.session["carrito"])  # se vacía tras reservar

    def test_stock_cambiado_bloquea_la_reserva(self):
        self.producto.cantidad = 0
        self.producto.save()
        with self._google(True):
            respuesta = self._reservar()
        self.assertRedirects(respuesta, reverse("carrito:index"))
        self.assertEqual(len(mail.outbox), 0)

    def test_get_no_permitido(self):
        self.assertEqual(self.client.get(reverse("carrito:enviar_correo")).status_code, 405)

    def test_producto_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("carrito:agregar_producto", args=[999])).status_code, 404)

    def test_sin_stock_redirige_con_mensaje(self):
        for _ in range(5):
            respuesta = self.client.get(reverse("carrito:agregar_producto", args=[self.producto.id]), follow=True)
        mensajes = [str(m) for m in respuesta.context["messages"]]
        self.assertTrue(any("No hay más stock" in m for m in mensajes))
        self.assertEqual(self.client.session["carrito"][str(self.producto.id)]["cantidad"], 3)

    def test_next_externo_es_ignorado(self):
        respuesta = self.client.get(
            reverse("carrito:agregar_producto", args=[self.producto.id]), {"next": "https://evil.com"}
        )
        self.assertRedirects(respuesta, reverse("productos:index"))
