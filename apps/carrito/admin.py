from django.contrib import admin, messages
from django.utils import timezone

from .models import DetalleReserva, Reserva


class DetalleReservaInline(admin.TabularInline):
    model = DetalleReserva
    extra = 0
    can_delete = False
    readonly_fields = ("producto", "nombre", "precio", "cantidad", "subtotal")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """MR-116: registro de reservas en el panel de administración."""
    list_display = ("codigo", "correo", "cliente", "total", "estado", "creada", "vence", "gestionada_por")
    list_filter = ("estado", "creada")
    search_fields = ("codigo", "correo", "cliente__usuario__username", "cliente__usuario__email")
    readonly_fields = ("codigo", "cliente", "correo", "total", "creada", "vence", "actualizada", "gestionada_por")
    inlines = [DetalleReservaInline]
    actions = ["marcar_retirada", "marcar_cancelada", "marcar_vencidas"]
    date_hierarchy = "creada"

    def has_add_permission(self, request):
        return False  # las reservas solo nacen desde el carrito

    def _cambiar(self, request, queryset, estado, permitidos):
        if not request.user.has_perm("carrito.gestionar_reservas"):
            self.message_user(request, "No tienes permiso para gestionar reservas.", messages.ERROR)
            return
        n = queryset.filter(estado__in=permitidos).update(estado=estado, gestionada_por=request.user, actualizada=timezone.now())
        self.message_user(request, f"{n} reserva(s) actualizada(s).", messages.SUCCESS)

    @admin.action(description="Marcar como retirada")
    def marcar_retirada(self, request, queryset):
        self._cambiar(request, queryset, Reserva.Estado.RETIRADA, [Reserva.Estado.PENDIENTE, Reserva.Estado.VENCIDA])

    @admin.action(description="Cancelar reserva")
    def marcar_cancelada(self, request, queryset):
        self._cambiar(request, queryset, Reserva.Estado.CANCELADA, [Reserva.Estado.PENDIENTE, Reserva.Estado.VENCIDA])

    @admin.action(description="Marcar como vencidas las pendientes con más de 24 h")
    def marcar_vencidas(self, request, queryset):
        vencidas = [r.pk for r in queryset.filter(estado=Reserva.Estado.PENDIENTE) if r.esta_vencida]
        self._cambiar(request, queryset.filter(pk__in=vencidas), Reserva.Estado.VENCIDA, [Reserva.Estado.PENDIENTE])
