from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    # Portal interno del personal
    path("", views.home, name="home"),
    path("crear_usuarios", views.crear_usuarios, name="crear_usuarios"),
    path("buscar_usuarios/", views.buscar_usuarios, name="buscar_usuarios"),
    # Cuentas de cliente (MR-115) y sus reservas (MR-116)
    path("registro/", views.registro_cliente, name="registro"),
    path("mi-cuenta/", views.mi_cuenta, name="mi_cuenta"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("mis-reservas/<str:codigo>/", views.mi_reserva, name="mi_reserva"),
    path("mis-reservas/<str:codigo>/cancelar/", views.cancelar_mi_reserva, name="cancelar_mi_reserva"),
]
