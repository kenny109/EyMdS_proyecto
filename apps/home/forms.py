from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User


def _estilizar(form, placeholders):
    """Aplica clases de Bootstrap a todos los campos del formulario.

    AuthenticationForm no es un ModelForm y los campos password1/password2 de
    UserCreationForm no son campos del modelo, por eso los `widgets` de Meta no
    tenían efecto; los atributos se asignan aquí.
    """
    for nombre, campo in form.fields.items():
        clases = "form-control form-control-lg"
        campo.widget.attrs.update({"class": clases, "placeholder": placeholders.get(nombre, campo.label)})


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password"].label = "Contraseña"
        _estilizar(self, {"username": "Tu nombre de usuario", "password": "Tu contraseña"})
        self.fields["username"].widget.attrs["autofocus"] = True


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repite la contraseña"
        _estilizar(
            self,
            {
                "username": "Nombre de usuario",
                "email": "correo@ejemplo.com",
                "password1": "Mínimo 8 caracteres",
                "password2": "Repite la contraseña",
            },
        )


# --------------------------------------------------------------------------- #
#  Recuperación y cambio de contraseña (MR-119)
# --------------------------------------------------------------------------- #


class RecuperarPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico de tu cuenta"
        _estilizar(self, {"email": "nombre@correo.com"})
        self.fields["email"].widget.attrs["autofocus"] = True


class NuevaPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password2"].label = "Repite la nueva contraseña"
        self.fields["new_password1"].help_text = ""
        _estilizar(self, {"new_password1": "Mínimo 8 caracteres", "new_password2": "Repite la contraseña"})


class CambiarPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Contraseña actual"
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password2"].label = "Repite la nueva contraseña"
        self.fields["new_password1"].help_text = ""
        _estilizar(self, {"old_password": "Tu contraseña actual", "new_password1": "Mínimo 8 caracteres",
                          "new_password2": "Repite la contraseña"})
