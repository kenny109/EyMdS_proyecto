from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from productos.models import Categoria, Productos


class BaseProductosTest(TestCase):
    def setUp(self):
        self.bebidas = Categoria.objects.create(nombre="Bebidas", descripcion="Jugos y aguas")
        self.lacteos = Categoria.objects.create(nombre="Lacteos", descripcion="Leche y queso")
        self.cola = Productos.objects.create(
            nombre="Coca Cola", precio=2990, cantidad=20, categoria=self.bebidas, umbral_minimo=5
        )
        self.sprite = Productos.objects.create(
            nombre="Sprite", precio=2790, cantidad=2, categoria=self.bebidas, umbral_minimo=4
        )
        self.queso = Productos.objects.create(
            nombre="Queso", precio=2990, cantidad=0, categoria=self.lacteos, umbral_minimo=3
        )
        self.staff = User.objects.create_user("staff", password="clave-segura-123", is_staff=True)
        self.cliente = User.objects.create_user("cliente", password="clave-segura-123")


class PermisosCrudTest(BaseProductosTest):
    """MR-110: las vistas de escritura solo las puede usar el personal."""

    def test_anonimo_no_puede_eliminar_y_es_redirigido_al_login(self):
        url = reverse("productos:productos_delete", args=[self.cola.id])
        respuesta = self.client.post(url)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("Home:login"), respuesta["Location"])
        self.assertTrue(Productos.objects.filter(id=self.cola.id).exists())

    def test_usuario_sin_staff_recibe_403(self):
        self.client.login(username="cliente", password="clave-segura-123")
        for nombre in ("productos_update", "productos_delete"):
            respuesta = self.client.get(reverse(f"productos:{nombre}", args=[self.cola.id]))
            self.assertEqual(respuesta.status_code, 403, nombre)
        self.assertEqual(self.client.get(reverse("productos:categoria_create")).status_code, 403)

    def test_staff_puede_eliminar(self):
        self.client.login(username="staff", password="clave-segura-123")
        respuesta = self.client.post(reverse("productos:productos_delete", args=[self.cola.id]))
        self.assertRedirects(respuesta, reverse("productos:productos_list"))
        self.assertFalse(Productos.objects.filter(id=self.cola.id).exists())

    def test_botones_de_edicion_ocultos_para_publico(self):
        respuesta = self.client.get(reverse("productos:productos_list"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, reverse("productos:productos_delete", args=[self.cola.id]))

    def test_portal_usuarios_restringido(self):
        self.assertEqual(self.client.get(reverse("usuarios:buscar_usuarios")).status_code, 302)
        self.client.login(username="cliente", password="clave-segura-123")
        self.assertEqual(self.client.get(reverse("usuarios:buscar_usuarios")).status_code, 403)


class CatalogoPublicoTest(BaseProductosTest):
    """MR-114: catálogo con búsqueda, filtro por categoría, stock y detalle público."""

    def test_filtro_por_categoria(self):
        respuesta = self.client.get(reverse("productos:index"), {"categoria": self.lacteos.id})
        self.assertEqual(list(respuesta.context["productos"]), [self.queso])

    def test_busqueda_por_nombre(self):
        respuesta = self.client.get(reverse("productos:index"), {"q": "sprite"})
        self.assertEqual(list(respuesta.context["productos"]), [self.sprite])

    def test_indicadores_de_stock(self):
        respuesta = self.client.get(reverse("productos:index"))
        self.assertContains(respuesta, "Agotado")
        self.assertContains(respuesta, "¡Últimas 2!")
        # el producto agotado no ofrece el enlace para agregar
        self.assertNotContains(respuesta, reverse("carrito:agregar_producto", args=[self.queso.id]))

    def test_paginacion(self):
        for i in range(15):
            Productos.objects.create(nombre=f"Agua {i}", precio=500, cantidad=10, categoria=self.bebidas)
        primera = self.client.get(reverse("productos:index"))
        self.assertEqual(len(primera.context["productos"]), 12)
        segunda = self.client.get(reverse("productos:index"), {"page": 2})
        self.assertEqual(len(segunda.context["productos"]), 6)

    def test_detalle_publico(self):
        respuesta = self.client.get(reverse("productos:producto_publico", args=[self.cola.id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Coca Cola")
        self.assertIn(self.sprite, respuesta.context["relacionados"])

    def test_detalle_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("productos:producto_publico", args=[999])).status_code, 404)

    def test_ruta_antigua_de_busqueda_redirige(self):
        respuesta = self.client.post(reverse("productos:buscar_productos"), {"termino_busqueda": "cola"})
        self.assertRedirects(respuesta, reverse("productos:index") + "?q=cola")
