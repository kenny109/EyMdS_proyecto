from django.conf import settings


def total_carrito(request):
    """Datos del carrito disponibles en todas las plantillas.

    - total_boleta: suma de subtotales del carrito.
    - cantidad_items: unidades en el carrito (contador del navbar, MR-113).
    - recaptcha_site_key: clave pública de reCAPTCHA leída desde .env (MR-112).
    """
    total = 0
    cantidad = 0
    carrito = request.session.get("carrito") or {}
    for value in carrito.values():
        total += int(value.get("acumulado", 0))  # Manejo de valores faltantes
        cantidad += int(value.get("cantidad", 0))

    return {
        "total_boleta": total,
        "cantidad_items": cantidad,
        "recaptcha_site_key": settings.RECAPTCHA_PUBLIC_KEY,
    }
