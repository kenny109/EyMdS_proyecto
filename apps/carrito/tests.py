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