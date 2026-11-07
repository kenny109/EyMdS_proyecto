from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from productos.models import Categoria, Productos

from . import forms
from .models import Tienda


def home(request: HttpRequest) -> HttpResponse:
    """Página de inicio (MR-113): categorías y productos destacados desde la BD."""
    contexto = {
        "categorias": Categoria.objects.order_by("nombre"),
        "destacados": Productos.objects.select_related("categoria")
        .filter(cantidad__gt=0)
        .order_by("-fecha_ingreso", "-id")[:4],
        "tiendas": Tienda.objects.filter(activa=True),
    }
    return render(request, "home/index.html", contexto)


def tiendas(request: HttpRequest) -> HttpResponse:
    """Pantalla propia de tiendas (MR-117) con minimapa de ubicaciones (MR-118)."""
    lista = list(Tienda.objects.filter(activa=True))
    puntos = [
        {"id": t.id, "nombre": t.nombre, "direccion": t.direccion,
         "lat": float(t.latitud), "lng": float(t.longitud), "ruta": t.como_llegar_url}
        for t in lista
    ]
    return render(request, "home/tiendas_page.html", {"tiendas": lista, "puntos": puntos})


### Login (MR-111: patrón Post/Redirect/Get + mensajes, rutas en minúscula)
def login_request(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("Home:home")

    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        form = forms.CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Hola, {user.username}! Iniciaste sesión correctamente.")
            if siguiente and url_has_allowed_host_and_scheme(
                siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(siguiente)
            return redirect("Home:home")
    else:
        form = forms.CustomAuthenticationForm(request)
    return render(request, "home/login.html", {"form": form, "next": siguiente})


### Registro (solo personal)
@staff_member_required
def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f"Usuario «{usuario.username}» registrado correctamente.")
            return redirect("Home:register")
    else:
        form = forms.CustomUserCreationForm()
    return render(request, "home/register.html", {"form": form})
