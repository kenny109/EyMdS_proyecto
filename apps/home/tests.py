from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from productos.models import Categoria, Productos


class AutenticacionTest(TestCase):
    """MR-111: login con redirección, logout por POST (Django 5) y plantillas en minúscula."""

    def setUp(self):
        self.user = User.objects.create_user("vendedor", password="clave-segura-123")

    def test_login_correcto_redirige_al_inicio(self):
        respuesta = self.client.post(
            reverse("Home:login"), {"username": "vendedor", "password": "clave-segura-123"}
        )
        self.assertRedirects(respuesta, reverse("Home:home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_incorrecto_muestra_error(self):
        respuesta = self.client.post(reverse("Home:login"), {"username": "vendedor", "password": "mala"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(respuesta.context["form"].errors)

    def test_login_respeta_next(self):
        destino = reverse("productos:productos_list")
        respuesta = self.client.post(
            reverse("Home:login"),
            {"username": "vendedor", "password": "clave-segura-123", "next": destino},
        )
        self.assertRedirects(respuesta, destino)

    def test_login_ignora_next_externo(self):
        respuesta = self.client.post(
            reverse("Home:login"),
            {"username": "vendedor", "password": "clave-segura-123", "next": "https://sitio-malicioso.com"},
        )
        self.assertRedirects(respuesta, reverse("Home:home"))

    def test_logout_por_post_cierra_sesion(self):
        self.client.login(username="vendedor", password="clave-segura-123")
        respuesta = self.client.post(reverse("Home:logout"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "home/logout.html")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_navbar_usa_formulario_post_para_logout(self):
        self.client.login(username="vendedor", password="clave-segura-123")
        respuesta = self.client.get(reverse("Home:home"))
        self.assertContains(respuesta, f'<form method="post" action="{reverse("Home:logout")}"', html=False)


class PaginasPublicasTest(TestCase):
    """MR-111 / MR-113: todas las páginas públicas cargan en un sistema de archivos
    que distingue mayúsculas (estas pruebas corren en Linux)."""

    def setUp(self):
        cat = Categoria.objects.create(nombre="Bebidas", descripcion="Jugos")
        Productos.objects.create(nombre="Jugo", precio=990, cantidad=5, categoria=cat)

    def test_paginas_publicas_responden_200(self):
        for nombre in ("Home:home", "Home:about", "Home:login", "productos:index", "carrito:index"):
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_inicio_muestra_categorias_y_destacados(self):
        respuesta = self.client.get(reverse("Home:home"))
        self.assertContains(respuesta, "Compra por categoría")
        self.assertContains(respuesta, "Jugo")

    def test_navbar_muestra_login_y_carrito_a_visitantes(self):
        respuesta = self.client.get(reverse("Home:home"))
        self.assertContains(respuesta, reverse("Home:login"))
        self.assertContains(respuesta, reverse("carrito:index"))
        self.assertNotContains(respuesta, f'href="{reverse("usuarios:home")}"')  # portal interno oculto
        self.assertContains(respuesta, reverse("usuarios:registro"))  # MR-115: enlace para crear cuenta

    def test_contador_del_carrito(self):
        producto = Productos.objects.get(nombre="Jugo")
        self.client.get(reverse("carrito:agregar_producto", args=[producto.id]))
        self.client.get(reverse("carrito:agregar_producto", args=[producto.id]))
        respuesta = self.client.get(reverse("Home:home"))
        self.assertEqual(respuesta.context["cantidad_items"], 2)
        self.assertContains(respuesta, '<span class="lt-cart-badge">2</span>', html=True)
