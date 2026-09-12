from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate

from . import forms

# Create your views here.
def home(request): 
    return render(request, "home/index.html")  

### Login
def login_request(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get("username")
            contraseña = form.cleaned_data.get("password")
            user = authenticate(username=usuario, password=contraseña)
            if user is not None:
                login(request, user)
                return render(request, "Home/index.html", {"mensaje": "Inicio de sesión correcto"})
    else:
        form = forms.CustomAuthenticationForm()
    return render(request, "home/login.html", {"form":form})

### Registro
from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required
def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get("username")
            form.save()
            return render(request, "Home/index.html", {"mensaje": "Registro de Usuario exitoso"})
    else:
        form = forms.CustomUserCreationForm()
    return render(request, "home/register.html", {"form":form})