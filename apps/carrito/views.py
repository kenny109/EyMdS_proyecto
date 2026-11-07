import logging
import smtplib

import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from carrito.cart import Carrito
from carrito.models import DetalleReserva, Reserva
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

    # 4. Registrar la reserva (MR-116). La transacción es corta: no se mantiene abierta
    #    mientras se envían los correos, para no bloquear la base SQLite.
    cliente = getattr(request.user, "cliente", None) if request.user.is_authenticated else None
    with transaction.atomic():
        reserva = Reserva.objects.create(cliente=cliente, correo=correo)
        total = 0
        for key, item in carrito_sesion.items():
            DetalleReserva.objects.create(
                reserva=reserva,
                producto=en_bd.get(int(key)),
                nombre=item["nombre"],
                precio=item["precio"],
                cantidad=item["cantidad"],
            )
            total += item["precio"] * item["cantidad"]
        reserva.total = total
        reserva.save(update_fields=["total"])

    # 5. Enviar los correos. Si fallan, la reserva se elimina y el carrito se conserva.
    try:
        _enviar_correos_reserva(reserva)
    except (smtplib.SMTPException, OSError) as error:
        logger.exception("Error al enviar el correo de reserva")
        reserva.delete()
        mensaje = "No pudimos enviar el correo en este momento. Tu carrito se mantuvo; inténtalo más tarde."
        if settings.DEBUG:
            # Solo en desarrollo: muestra la causa para diagnosticar la configuración SMTP del .env
            detalle = "credenciales de correo rechazadas (revisa EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en .env)" \
                if isinstance(error, smtplib.SMTPAuthenticationError) else f"{type(error).__name__}: {error}"
            mensaje += f" [DEBUG: {detalle}]"
        messages.error(request, mensaje)
        return redirect("carrito:index")

    Carrito(request).limpiar()
    return render(request, "carrito/confirmacion.html", {"reserva": reserva, "correo": correo, "total": reserva.total})


def _detalle_texto(reserva):
    lineas = ""
    for d in reserva.detalles.all():
        lineas += f"Producto: {d.nombre}\nPrecio: ${d.precio}\nCantidad: {d.cantidad}\nSubtotal: ${d.subtotal}\n\n"
    return lineas


def _enviar_correos_reserva(reserva):
    """Envía el detalle al cliente y el aviso a la tienda. El remitente es siempre la tienda (MR-112)."""
    detalle = _detalle_texto(reserva)
    vence = timezone.localtime(reserva.vence).strftime("%d/%m/%Y %H:%M")
    mensaje_cliente = (
        f"Tu código de reserva es: {reserva.codigo}\n\n"
        f"Tus productos escogidos son: \n\n{detalle} \n Total de tu reserva: ${reserva.total} \n"
        f" ¡Tienes hasta el {vence} para acercarte al local, mostrar tu código y pagar para obtener tus productos!"
    )
    mensaje_tienda = (
        f"Reserva {reserva.codigo}\n"
        f"El cliente de correo: {reserva.correo}"
        + (f" (cliente registrado: {reserva.cliente})" if reserva.cliente else "")
        + f", solicitó la reserva de los siguientes productos: \n\n{detalle} \n Total de la reserva: ${reserva.total} \n"
        f" Vence el {vence}. Gestiónala en el panel de reservas."
    )
    EmailMessage(
        f"Reserva {reserva.codigo} - Minimarket Los Tios",
        mensaje_cliente,
        settings.DEFAULT_FROM_EMAIL,
        [reserva.correo],
    ).send(fail_silently=False)
    EmailMessage(
        f"¡Nueva reserva {reserva.codigo}!",
        mensaje_tienda,
        settings.DEFAULT_FROM_EMAIL,
        [settings.STORE_EMAIL],
        reply_to=[reserva.correo],
    ).send(fail_silently=False)


# --------------------------------------------------------------------------- #
#  Panel de reservas del personal (MR-116)
#  Ver: permiso carrito.view_reserva · Cambiar estado: carrito.gestionar_reservas
# --------------------------------------------------------------------------- #
@permission_required("carrito.view_reserva", raise_exception=True)
def panel_reservas(request):
    reservas = Reserva.objects.select_related("cliente__usuario").prefetch_related("detalles")
    estado = request.GET.get("estado", "")
    if estado in Reserva.Estado.values:
        reservas = reservas.filter(estado=estado)
    consulta = request.GET.get("q", "").strip()
    if consulta:
        reservas = reservas.filter(Q(codigo__icontains=consulta) | Q(correo__icontains=consulta))
    conteo = {e: Reserva.objects.filter(estado=e).count() for e in Reserva.Estado.values}
    return render(request, "carrito/panel_reservas.html", {
        "reservas": reservas[:200],
        "estados": Reserva.Estado.choices,
        "estado_activo": estado,
        "consulta": consulta,
        "conteo": conteo,
        "por_vencer": sum(1 for r in Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE) if r.esta_vencida),
    })


@permission_required("carrito.view_reserva", raise_exception=True)
def detalle_reserva(request, codigo):
    reserva = get_object_or_404(Reserva.objects.prefetch_related("detalles"), codigo=codigo)
    return render(request, "carrito/detalle_reserva.html", {"reserva": reserva, "estados": Reserva.Estado.choices})


TRANSICIONES = {
    Reserva.Estado.PENDIENTE: {Reserva.Estado.RETIRADA, Reserva.Estado.CANCELADA, Reserva.Estado.VENCIDA},
    Reserva.Estado.VENCIDA: {Reserva.Estado.RETIRADA, Reserva.Estado.CANCELADA},
}


@require_POST
@permission_required("carrito.gestionar_reservas", raise_exception=True)
def cambiar_estado_reserva(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)
    nuevo = request.POST.get("estado")
    if nuevo not in TRANSICIONES.get(reserva.estado, set()):
        messages.error(request, f"La reserva {reserva.codigo} no puede pasar de «{reserva.get_estado_display()}» a ese estado.")
    else:
        reserva.estado = nuevo
        reserva.gestionada_por = request.user
        reserva.save(update_fields=["estado", "gestionada_por", "actualizada"])
        messages.success(request, f"Reserva {reserva.codigo}: {reserva.get_estado_display()}.")
    return _volver(request, "carrito:panel_reservas")
