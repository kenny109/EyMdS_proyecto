import logging
import smtplib

import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from carrito.cart import Carrito
from productos.models import Productos

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
MENSAJE_SIN_STOCK = "No hay mas stock de este producto."


def _volver(request, por_defecto="productos:index"):
    """Redirige a ?next= si es una URL segura del propio sitio; si no, a `por_defecto`."""
    siguiente = request.GET.get("next") or request.POST.get("next")
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(siguiente)
    return redirect(por_defecto)


def carrito(request):
    """Página del carrito con el formulario de reserva."""
    return render(request, "carrito/index.html")


def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Productos, id=producto_id)

    mensaje = carrito.agregar_prod(producto)
    if mensaje == MENSAJE_SIN_STOCK:
        # Antes se renderizaba productos/index.html sin productos (página vacía)
        messages.warning(request, f"No hay más stock disponible de «{producto.nombre}».")
    else:
        messages.success(request, f"«{producto.nombre}» se agregó al carrito.")
    return _volver(request)


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Productos, id=producto_id)
    carrito.eliminar(producto)
    return _volver(request, "carrito:index")


def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Productos, id=producto_id)
    carrito.restar(producto)
    return _volver(request, "carrito:index")


def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    messages.info(request, "Vaciaste el carrito.")
    return _volver(request, "carrito:index")


def verificar_recaptcha(token, ip=None):
    """Valida el token contra Google. Devuelve True solo si Google responde success=True."""
    if not token:
        return False
    data = {"secret": settings.RECAPTCHA_PRIVATE_KEY, "response": token}
    if ip:
        data["remoteip"] = ip
    try:
        respuesta = requests.post(RECAPTCHA_VERIFY_URL, data=data, timeout=5)
        resultado = respuesta.json()
    except (requests.RequestException, ValueError):
        logger.exception("No se pudo verificar reCAPTCHA")
        return False
    return bool(resultado.get("success"))


@require_POST
def enviar_correo(request):
    carrito_sesion = request.session.get("carrito") or {}
    if not carrito_sesion:
        messages.error(request, "No puedes reservar un carrito vacío.")
        return redirect("carrito:index")

    # 1. Correo válido
    correo = (request.POST.get("correo") or "").strip()
    try:
        validate_email(correo)
    except ValidationError:
        messages.error(request, "Ingresa un correo electrónico válido.")
        return redirect("carrito:index")

    # 2. reCAPTCHA: ahora se comprueba la respuesta de Google (antes se ignoraba)
    if not verificar_recaptcha(request.POST.get("g-recaptcha-response"), request.META.get("REMOTE_ADDR")):
        messages.error(request, "No pudimos verificar que no eres un robot. Inténtalo de nuevo.")
        return redirect("carrito:index")

    # 3. Revalidar stock contra la base de datos al momento de reservar
    ids = [int(k) for k in carrito_sesion.keys()]
    en_bd = {p.id: p for p in Productos.objects.filter(id__in=ids)}
    for key, item in carrito_sesion.items():
        producto = en_bd.get(int(key))
        if producto is None or item["cantidad"] > producto.cantidad:
            nombre = item.get("nombre", "un producto")
            messages.error(request, f"El stock de «{nombre}» cambió. Ajusta tu carrito antes de reservar.")
            return redirect("carrito:index")

    # 4. Armar el detalle
    carrito_info = ""
    total = 0
    for value in carrito_sesion.values():
        carrito_info += f"Producto: {value['nombre']}\n"
        carrito_info += f"Precio: ${value['precio']}\n"
        carrito_info += f"Cantidad: {value['cantidad']}\n"
        carrito_info += f"Subtotal: ${value['acumulado']}\n\n"
        total += value["acumulado"]

    mensaje_cliente = (
        f"Tus productos escogidos son: \n\n{carrito_info} \n Total de tu reserva: ${total} \n"
        " ¡Tienes 24 horas para acercarte al local y pagar para obtener tus productos!"
    )
    mensaje_tienda = (
        f"El cliente de correo: {correo}, solicitó la reserva de los siguientes productos: "
        f"\n\n{carrito_info} \n Total de la reserva: ${total} \n El cliente llegará dentro de las próximas 24 horas."
    )

    # 5. Enviar: el remitente es siempre la cuenta de la tienda (antes era el correo del cliente)
    try:
        EmailMessage(
            "Detalles del carrito de compras - Minimarket Los Tios",
            mensaje_cliente,
            settings.DEFAULT_FROM_EMAIL,
            [correo],
        ).send(fail_silently=False)
        EmailMessage(
            "¡Un cliente ha solicitado una reserva!",
            mensaje_tienda,
            settings.DEFAULT_FROM_EMAIL,
            [settings.STORE_EMAIL],
            reply_to=[correo],
        ).send(fail_silently=False)
    except (smtplib.SMTPException, OSError):
        logger.exception("Error al enviar el correo de reserva")
        messages.error(request, "No pudimos enviar el correo en este momento. Tu carrito se mantuvo; inténtalo más tarde.")
        return redirect("carrito:index")

    Carrito(request).limpiar()
    return render(request, "carrito/confirmacion.html", {"correo": correo, "total": total})
