from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from home.permissions import StaffRequiredMixin

from . import models
from .forms import CategoriaForm, ProductosForm
from .models import Categoria, Productos

PRODUCTOS_POR_PAGINA = 12


# --------------------------------------------------------------------------- #
#  Catálogo público (MR-114)
# --------------------------------------------------------------------------- #
def index(request: HttpRequest) -> HttpResponse:
    """Catálogo público con búsqueda, filtro por categoría y paginación."""
    productos = Productos.objects.select_related("categoria").order_by("nombre")

    consulta = request.GET.get("q", "").strip()
    if consulta:
        productos = productos.filter(
            Q(nombre__icontains=consulta) | Q(categoria__nombre__icontains=consulta)
        )

    categoria_activa = None
    categoria_id = request.GET.get("categoria", "")
    if categoria_id.isdigit():
        categoria_activa = Categoria.objects.filter(pk=categoria_id).first()
        if categoria_activa:
            productos = productos.filter(categoria=categoria_activa)

    paginador = Paginator(productos, PRODUCTOS_POR_PAGINA)
    page_obj = paginador.get_page(request.GET.get("page"))

    # Parámetros actuales sin "page", para armar los enlaces de paginación
    params = request.GET.copy()
    params.pop("page", None)

    contexto = {
        "productos": page_obj.object_list,
        "page_obj": page_obj,
        "categorias": Categoria.objects.order_by("nombre"),
        "categoria_activa": categoria_activa,
        "consulta": consulta,
        "total_resultados": paginador.count,
        "query_sin_pagina": params.urlencode(),
    }
    return render(request, "productos/index.html", contexto)


def producto_publico(request: HttpRequest, pk: int) -> HttpResponse:
    """Ficha pública de un producto, con productos relacionados de su categoría."""
    producto = get_object_or_404(Productos.objects.select_related("categoria"), pk=pk)
    relacionados = (
        Productos.objects.filter(categoria=producto.categoria)
        .exclude(pk=producto.pk)
        .order_by("-cantidad")[:4]
    )
    return render(
        request,
        "productos/producto_publico.html",
        {"producto": producto, "relacionados": relacionados},
    )


def buscar_productos(request: HttpRequest) -> HttpResponse:
    """Ruta antigua de búsqueda (POST). Se mantiene por compatibilidad y redirige
    al catálogo, que ahora busca por GET (MR-114)."""
    termino = (request.POST.get("termino_busqueda") or request.GET.get("q") or "").strip()
    url = reverse("productos:index")
    if termino:
        url = f"{url}?{urlencode({'q': termino})}"
    return redirect(url)


def ingreso_productos(request: HttpRequest) -> HttpResponse:
    """Ruta antigua: su plantilla no existía (error 500). Ahora lleva al formulario
    de creación, que está protegido para el personal (MR-110)."""
    return redirect("productos:productos_create")


# --------------------------------------------------------------------------- #
#  Gestión de categorías (lectura pública, escritura solo personal - MR-110)
# --------------------------------------------------------------------------- #
class CategoriaList(ListView):
    model = models.Categoria
    ordering = ("nombre",)


class CategoriaCreate(StaffRequiredMixin, CreateView):
    model = models.Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("productos:categoria_list")


class CategoriaDetail(DetailView):
    model = models.Categoria


class CategoriaUpdate(StaffRequiredMixin, UpdateView):
    model = models.Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("productos:categoria_list")


class CategoriaDelete(StaffRequiredMixin, DeleteView):
    model = models.Categoria
    success_url = reverse_lazy("productos:categoria_list")


# --------------------------------------------------------------------------- #
#  Gestión de productos (lectura pública, escritura solo personal - MR-110)
# --------------------------------------------------------------------------- #
class ProductosList(ListView):
    model = models.Productos

    def get_queryset(self):
        object_list = models.Productos.objects.select_related("categoria").order_by("nombre")
        consulta = self.request.GET.get("consulta")
        if consulta:
            object_list = object_list.filter(nombre__icontains=consulta)
        return object_list  ## Es un objeto Query Set


class ProductosCreate(StaffRequiredMixin, CreateView):
    model = models.Productos
    form_class = ProductosForm
    success_url = reverse_lazy("productos:productos_list")


class ProductosDetail(DetailView):
    model = models.Productos


class ProductosUpdate(StaffRequiredMixin, UpdateView):
    model = models.Productos
    form_class = ProductosForm
    success_url = reverse_lazy("productos:productos_list")


class ProductosDelete(StaffRequiredMixin, DeleteView):
    model = models.Productos
    success_url = reverse_lazy("productos:productos_list")


def enviar_notificacion_stock_bajo(producto):
    subject = 'Notificación de stock bajo'
    message = (
        f'El stock del producto {producto.nombre} ha caído por debajo del umbral mínimo.\n'
        f'El stock actual es de: {producto.cantidad} \n\n ¡Reabastece este producto!'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.STORE_EMAIL],
        fail_silently=False,
    )
