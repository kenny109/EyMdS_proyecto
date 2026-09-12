from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from .models import Productos
from django.http import HttpRequest, HttpResponse

from .forms import ProductosForm
from .forms import CategoriaForm
from . import models

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail

def index(request):
    productos_registrados = Productos.objects.all()
    contexto = {"productos": productos_registrados}
    return render(request, "productos/index.html", contexto)


####### Formulario Ingresar Productos###
def ingreso_productos(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("productos:home")
    else:
        form = ProductosForm()
    return render(request, "productos/ingresar_productos.html", {"form": form})

####### Busqueda de Productos ####
def buscar_productos(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Obtener el término de búsqueda del formulario
        termino_busqueda = request.POST.get('termino_busqueda')
        # Realizar la búsqueda en la base de datos
        productos = Productos.objects.filter(nombre__icontains=termino_busqueda)
        # Pasar los resultados de la búsqueda al contexto
        context = {'productos': productos}
        return render(request, 'productos/buscar_productos.html', context)
    else:
        return render(request, 'productos/buscar_productos.html')
    
## Clase Listar Categorias
class CategoriaList(ListView):
    model = models.Categoria

## Clase Crear Categorias
class CategoriaCreate(CreateView):
    model = models.Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("productos:categoria_list")

### Clase Ver Detalles Categorias
class CategoriaDetail(DetailView):
    model = models.Categoria

# Clase Actualizar Categorias
class CategoriaUpdate(UpdateView):
    model = models.Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("productos:categoria_list")

# Clase Eliminar Categorias
class CategoriaDelete(DeleteView):
    model = models.Categoria
    success_url = reverse_lazy("productos:categoria_list")

# ---------------------------------------#

## Clase Listar Productos
class ProductosList(ListView):
    model = models.Productos

    def get_queryset(self):
        if self.request.GET.get("consulta"):
            consulta = self.request.GET.get("consulta")
            object_list = models.Productos.objects.filter(nombre__icontains = consulta)
        else:
            object_list = models.Productos.objects.all()
        return object_list ## Es un objeto Query Set

## Clase Crear Productos
class ProductosCreate(CreateView):
    model = models.Productos
    form_class = ProductosForm
    success_url = reverse_lazy("productos:productos_list")

### Clase Ver Detalles Productos
class ProductosDetail(DetailView):
    model = models.Productos

# Clase Actualizar Productos
class ProductosUpdate(UpdateView):
    model = models.Productos
    form_class = ProductosForm
    success_url = reverse_lazy("productos:productos_list")

# Clase Eliminar Productos
class ProductosDelete(DeleteView):
    model = models.Productos
    success_url = reverse_lazy("productos:productos_list")


def enviar_notificacion_stock_bajo(producto):
    subject = 'Notificación de stock bajo'
    message = f'El stock del producto {producto.nombre} ha caído por debajo del umbral mínimo.\nEl stock actual es de: {producto.cantidad} \n\n ¡Reabastece este producto!'
    from_email = 'minimarket.lostios@gmail.com' 
    recipient_list = ['minimarket.lostios@gmail.com']  # Correo del destinatario

    # Envio del correo electrónico
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

