
from django.urls import path
    #! Include sirve para traer URLS de las apps
from . import views

app_name = "carrito"

urlpatterns = [
    path("", views.carrito, name="index"),
    path("agregar/<int:producto_id>/", views.agregar_producto, name="agregar_producto"),
    path("eliminar/<int:producto_id>/", views.eliminar_producto, name="eliminar_producto"),
    path("restar/<int:producto_id>/", views.restar_producto, name="restar_producto"),
    path("limpiar/", views.limpiar_carrito, name="limpiar_carrito"),
    path("enviar/", views.enviar_correo, name="enviar_correo"),
    # Panel de reservas del personal (MR-116)
    path("reservas/", views.panel_reservas, name="panel_reservas"),
    path("reservas/<str:codigo>/", views.detalle_reserva, name="detalle_reserva"),
    path("reservas/<str:codigo>/estado/", views.cambiar_estado_reserva, name="cambiar_estado_reserva"),
] 