from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
    ### Este sirve para ingresar
from django.contrib.auth.models import User
    ### Este sirve para crear el usuario

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password", "email")
        ## Los campos los puedo ver en la BD
        ## En la parte auth_usr
        widgets = {
            "username": forms.TextInput(attrs={"class":"form-control"}),
            "email": forms.TextInput(attrs={"class":"form-control"}),
            "password": forms.PasswordInput(attrs={"class":"form-control"}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        help_text = {k: "" for k in fields}
        widgets = {
            "username": forms.TextInput(attrs={"class":"form-control"}),
            "email": forms.TextInput(attrs={"class":"form-control"}),
            "password1": forms.PasswordInput(attrs={"class":"form-control"}),
            "password2": forms.PasswordInput(attrs={"class":"form-control"}),
        }