from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import UsuarioForm
from .models import Usuario
# Create your views here.

def home(request):
    usuarios_registrados = Usuario.objects.all()
    contexto = {"usuarios": usuarios_registrados}
    return render(request, "usuarios/index.html", contexto)

####### Formulario Crear Usuarios###
def crear_usuarios(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("usuarios:home")
    else:
        form = UsuarioForm()
    return render(request, "usuarios/crear_usuarios.html", {"form": form})

####### Busqueda de Usuarios ####
def buscar_usuarios(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Obtener el término de búsqueda del formulario
        termino_busqueda = request.POST.get('termino_busqueda')
        # Realizar la búsqueda en la base de datos
        usuario = Usuario.objects.filter(nombre__icontains=termino_busqueda)
        # Pasar los resultados de la búsqueda al contexto
        context = {'usuarios': usuario}
        return render(request, 'usuarios/buscar_usuarios.html', context)
    else:
        return render(request, 'usuarios/buscar_usuarios.html')