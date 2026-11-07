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


# --------------------------------------------------------------------------- #
#  MR-117 / MR-118: pantalla de tiendas con minimapa
# --------------------------------------------------------------------------- #
import json

from home.models import Tienda


class TiendasTest(TestCase):
    def test_migracion_carga_las_tres_tiendas(self):
        self.assertEqual(
            list(Tienda.objects.values_list("nombre", flat=True)),
            ["Tienda Santiago", "Tienda Puerto Montt", "Tienda Viña del Mar"],
        )

    def test_pantalla_propia_con_datos_del_mapa(self):
        respuesta = self.client.get(reverse("Home:tiendas"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'id="mapa-tiendas"')
        self.assertContains(respuesta, "leaflet@1.9.4")
        puntos = respuesta.context["puntos"]
        self.assertEqual(len(puntos), 3)
        self.assertAlmostEqual(puntos[0]["lat"], -33.4378, places=3)
        self.assertIn("google.com/maps/dir", puntos[0]["ruta"])
        # los datos del mapa viajan en un <script type="application/json"> (sin inyección de HTML)
        self.assertContains(respuesta, 'id="puntos-tiendas" type="application/json"')

    def test_tienda_inactiva_no_se_muestra(self):
        Tienda.objects.filter(nombre="Tienda Puerto Montt").update(activa=False)
        respuesta = self.client.get(reverse("Home:tiendas"))
        self.assertNotContains(respuesta, "Tienda Puerto Montt")
        self.assertEqual(len(respuesta.context["puntos"]), 2)

    def test_navbar_e_inicio_enlazan_a_la_pantalla(self):
        respuesta = self.client.get(reverse("Home:home"))
        self.assertContains(respuesta, f'href="{reverse("Home:tiendas")}"')
        self.assertContains(respuesta, "Tienda Viña del Mar")


# --------------------------------------------------------------------------- #
#  MR-119: recuperar y cambiar contraseña
# --------------------------------------------------------------------------- #
import re

from django.core import mail
from django.test import override_settings


@override_settings(DEFAULT_FROM_EMAIL="tienda@lostios.cl")
class RecuperarPasswordTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("maria", email="maria@correo.com", password="Vieja-clave-1")

    def test_flujo_completo_por_correo(self):
        respuesta = self.client.post(reverse("Home:password_reset"), {"email": "maria@correo.com"})
        self.assertRedirects(respuesta, reverse("Home:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        enlace = re.search(r"http://testserver(\S+)", mail.outbox[0].body).group(1)
        # el enlace lleva al formulario de nueva contraseña
        formulario = self.client.get(enlace, follow=True)
        self.assertTrue(formulario.context["validlink"])
        url_form = formulario.redirect_chain[-1][0]
        final = self.client.post(url_form, {"new_password1": "Nueva-clave-2026", "new_password2": "Nueva-clave-2026"})
        self.assertRedirects(final, reverse("Home:password_reset_complete"))
        self.assertTrue(self.client.login(username="maria", password="Nueva-clave-2026"))

    def test_correo_desconocido_no_revela_nada(self):
        respuesta = self.client.post(reverse("Home:password_reset"), {"email": "nadie@correo.com"})
        self.assertRedirects(respuesta, reverse("Home:password_reset_done"))  # misma respuesta
        self.assertEqual(len(mail.outbox), 0)

    def test_enlace_alterado_no_es_valido(self):
        respuesta = self.client.get(
            reverse("Home:password_reset_confirm", args=["MQ", "token-falso"]), follow=True
        )
        self.assertFalse(respuesta.context["validlink"])

    def test_login_ofrece_recuperar(self):
        self.assertContains(self.client.get(reverse("Home:login")), reverse("Home:password_reset"))

    def test_cambiar_password_con_sesion(self):
        self.assertEqual(self.client.get(reverse("Home:password_change")).status_code, 302)  # requiere sesión
        self.client.login(username="maria", password="Vieja-clave-1")
        malo = self.client.post(reverse("Home:password_change"), {
            "old_password": "incorrecta", "new_password1": "Otra-clave-2026", "new_password2": "Otra-clave-2026"})
        self.assertEqual(malo.status_code, 200)  # la contraseña actual es obligatoria
        ok = self.client.post(reverse("Home:password_change"), {
            "old_password": "Vieja-clave-1", "new_password1": "Otra-clave-2026", "new_password2": "Otra-clave-2026"})
        self.assertRedirects(ok, reverse("Home:password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Otra-clave-2026"))
