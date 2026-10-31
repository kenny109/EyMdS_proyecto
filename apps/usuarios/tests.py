from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Cliente


class RegistroClienteTest(TestCase):
    """MR-115: creación de cuentas de cliente."""

    datos = {
        "username": "maria.perez", "first_name": "María", "last_name": "Pérez",
        "email": "maria@correo.com", "telefono": "+56911112222",
        "password1": "Reserva-2026!", "password2": "Reserva-2026!",
    }

    def test_registro_crea_usuario_y_cliente_e_inicia_sesion(self):
        respuesta = self.client.post(reverse("usuarios:registro"), self.datos)
        self.assertRedirects(respuesta, reverse("productos:index"))
        user = User.objects.get(username="maria.perez")
        self.assertFalse(user.is_staff)
        self.assertEqual(user.cliente.telefono, "+56911112222")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_correo_duplicado_es_rechazado(self):
        User.objects.create_user("otro", email="maria@correo.com", password="x-Clave-123")
        respuesta = self.client.post(reverse("usuarios:registro"), self.datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("email", respuesta.context["form"].errors)
        self.assertFalse(Cliente.objects.exists())

    def test_registro_respeta_next(self):
        datos = dict(self.datos, next=reverse("carrito:index"))
        respuesta = self.client.post(reverse("usuarios:registro"), datos)
        self.assertRedirects(respuesta, reverse("carrito:index"))

    def test_cliente_no_accede_a_la_gestion(self):
        self.client.post(reverse("usuarios:registro"), self.datos)
        self.assertEqual(self.client.get(reverse("productos:productos_create")).status_code, 403)
        self.assertEqual(self.client.get(reverse("usuarios:home")).status_code, 403)

    def test_mi_cuenta_requiere_sesion_y_actualiza_datos(self):
        self.assertEqual(self.client.get(reverse("usuarios:mi_cuenta")).status_code, 302)
        self.client.post(reverse("usuarios:registro"), self.datos)
        respuesta = self.client.post(reverse("usuarios:mi_cuenta"), {
            "first_name": "María José", "last_name": "Pérez", "email": "mj@correo.com", "telefono": "+56933334444",
        })
        self.assertRedirects(respuesta, reverse("usuarios:mi_cuenta"))
        user = User.objects.get(username="maria.perez")
        self.assertEqual((user.first_name, user.email, user.cliente.telefono), ("María José", "mj@correo.com", "+56933334444"))
