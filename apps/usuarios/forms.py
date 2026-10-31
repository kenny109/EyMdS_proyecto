from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Cliente, Usuario


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"


def _bootstrap(form):
    for campo in form.fields.values():
        campo.widget.attrs.setdefault("class", "form-control form-control-lg")


class RegistroClienteForm(UserCreationForm):
    """Registro público de clientes (MR-115). Crea el auth.User y su Cliente."""

    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(label="Teléfono (opcional)", max_length=20, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].help_text = "Letras, números y @ . + - _"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repite la contraseña"
        self.fields["password2"].help_text = ""
        placeholders = {"username": "ej. maria.perez", "email": "nombre@correo.com", "telefono": "+56 9 1234 5678"}
        _bootstrap(self)
        for nombre, texto in placeholders.items():
            self.fields[nombre].widget.attrs["placeholder"] = texto

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = False  # un cliente nunca accede a la gestión
        if commit:
            user.save()
            Cliente.objects.create(usuario=user, telefono=self.cleaned_data.get("telefono", ""))
        return user


class PerfilClienteForm(forms.ModelForm):
    """Edición de los datos del cliente en 'Mi cuenta'."""

    telefono = forms.CharField(label="Teléfono", max_length=20, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "Nombre", "last_name": "Apellido", "email": "Correo electrónico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        if hasattr(self.instance, "cliente"):
            self.fields["telefono"].initial = self.instance.cliente.telefono
        _bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otra cuenta con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            cliente, _ = Cliente.objects.get_or_create(usuario=user)
            cliente.telefono = self.cleaned_data.get("telefono", "")
            cliente.save()
        return user
