"""Control de acceso para el personal de la tienda (MR-110).

- Visitante sin sesión  -> se redirige a la página de inicio de sesión.
- Usuario sin is_staff  -> 403 (prohibido).
- Usuario con is_staff  -> acceso permitido.
"""
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para vistas basadas en clases que solo puede usar el personal."""

    raise_exception = False  # anónimos -> login; usuarios normales -> 403 (ver handle_no_permission)

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Solo el personal de la tienda puede realizar esta acción.")
        return super().handle_no_permission()


def staff_required(view_func):
    """Decorador equivalente a StaffRequiredMixin para vistas basadas en funciones."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            raise PermissionDenied("Solo el personal de la tienda puede realizar esta acción.")
        return view_func(request, *args, **kwargs)

    return _wrapped
