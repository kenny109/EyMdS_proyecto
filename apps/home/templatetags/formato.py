from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """Formatea un entero como peso chileno: 1290 -> '1.290'."""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor
