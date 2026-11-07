from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from carrito.models import Reserva
from home.permissions import staff_required

from .forms import PerfilClienteForm, RegistroClienteForm, UsuarioForm
from .models import Cliente, Usuario


# --------------------------------------------------------------------------- #
#  Portal interno del personal (MR-110)
# --------------------------------------------------------------------------- #
@staff_required
def home(request):
    usuarios_registrados = Usuario.objects.all()
    contexto = {"usuarios": usuarios_registrados, "total_clientes": Cliente.objects.count()}
    return render(request, "usuarios/index.html", contexto)


####### Formulario Crear Usuarios###
@staff_required
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
@staff_required
def buscar_usuarios(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        termino_busqueda = request.POST.get('termino_busqueda')
        usuario = Usuario.objects.filter(nombre__icontains=termino_busqueda)
        context = {'usuarios': usuario}
        return render(request, 'usuarios/buscar_usuarios.html', context)
    else:
        return render(request, 'usuarios/buscar_usuarios.html')


# --------------------------------------------------------------------------- #
#  Cuentas de cliente (MR-115)
# --------------------------------------------------------------------------- #
def registro_cliente(request: HttpRequest) -> HttpResponse:
    """Registro público: crea el usuario + su ficha de cliente e inicia sesión."""
    if request.user.is_authenticated:
        return redirect("usuarios:mi_cuenta")

    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"¡Bienvenido, {user.first_name}! Tu cuenta de cliente quedó creada.")
            if siguiente and url_has_allowed_host_and_scheme(
                siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(siguiente)
            return redirect("productos:index")
    else:
        form = RegistroClienteForm()
    return render(request, "usuarios/registro_cliente.html", {"form": form, "next": siguiente})


def _cliente_de(request):
    """Devuelve el Cliente del usuario conectado (lo crea si la cuenta no tenía ficha)."""
    cliente, _ = Cliente.objects.get_or_create(usuario=request.user)
    return cliente


@login_required
def mi_cuenta(request: HttpRequest) -> HttpResponse:
    Reserva.vencer_pendientes()  # MR-121
    cliente = _cliente_de(request)
    if request.method == "POST":
        form = PerfilClienteForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos se actualizaron.")
            return redirect("usuarios:mi_cuenta")
    else:
        form = PerfilClienteForm(instance=request.user)
    ultimas = cliente.reservas.prefetch_related("detalles")[:3]
    return render(request, "usuarios/mi_cuenta.html", {"form": form, "cliente": cliente, "ultimas": ultimas})


@login_required
def mis_reservas(request: HttpRequest) -> HttpResponse:
    Reserva.vencer_pendientes()  # MR-121
    cliente = _cliente_de(request)
    reservas = cliente.reservas.prefetch_related("detalles")
    return render(request, "usuarios/mis_reservas.html", {"reservas": reservas})


@login_required
def mi_reserva(request: HttpRequest, codigo: str) -> HttpResponse:
    Reserva.vencer_pendientes()  # MR-121
    # Permiso (MR-116): un cliente solo puede ver sus propias reservas; las de otros dan 404.
    reserva = get_object_or_404(
        Reserva.objects.prefetch_related("detalles"), codigo=codigo, cliente__usuario=request.user
    )
    return render(request, "usuarios/mi_reserva.html", {"reserva": reserva})


@require_POST
@login_required
def cancelar_mi_reserva(request: HttpRequest, codigo: str) -> HttpResponse:
    """MR-121: el cliente cancela una reserva propia que siga pendiente y dentro de plazo."""
    reserva = get_object_or_404(Reserva, codigo=codigo, cliente__usuario=request.user)
    if not reserva.puede_cancelar_cliente:
        messages.error(request, "Esta reserva ya no se puede cancelar.")
        return redirect("usuarios:mi_reserva", codigo=codigo)
    reserva.estado = Reserva.Estado.CANCELADA
    reserva.save(update_fields=["estado", "actualizada"])
    # Aviso a la tienda; si el correo falla, la cancelación igual queda registrada
    send_mail(
        f"Reserva {reserva.codigo} cancelada por el cliente",
        f"El cliente {reserva.cliente} ({reserva.correo}) canceló la reserva {reserva.codigo} "
        f"por ${reserva.total}. Ya no es necesario apartar sus productos.",
        settings.DEFAULT_FROM_EMAIL,
        [settings.STORE_EMAIL],
        fail_silently=True,
    )
    messages.success(request, f"Cancelaste la reserva {reserva.codigo}.")
    return redirect("usuarios:mi_reserva", codigo=codigo)
