# Login

En Home: 

colocar el url/path 
    from . import views
    path('login/', views.login_request, name="login")
    

en views, hay poner
    from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
    from django.contrib.auth import login, logout, authenticate

hay que crear un forms.py:
    from django import forms
    from django.contrib.auth.forms import AuthenticationForm
        ### Este sirve para ingresar
    from django.contrib.auth.models import User
        ### Este sirve para crear el usuario

    y crear la clase, con meta, model user, fields los datos y widgter
    que sirve para personalizar los datos

en views, crear la función login_request:
    from . import forms
    y todos los datos
    en el último se puede crear un mensaje que se verá en el index.html

crear login.html:
    e incluir un form tipo Post
    
# Logout

en URL.py:
    from django.contrib.auth.views import LogoutView

    path("logout/", LogoutView.as_view(template_name="Home/logout.html"), name="logout")

crear un logout.html

# Mixin y Decoradores

Sirve para que solo personas con login puedan ver secciones de páginas
Su función es validar lógica en las Views

    En views.py (productos)
    
    from django.contrib.auth.mixins import LoginRequiredMixin
    

# Registro
en forms.py
    class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        field = ["username", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class":"form-control"}),
            "password1": forms.PasswordInput(attrs={"class":"form-control"}),
            "password2": forms.PasswordInput(attrs={"class":"form-control"}),
        }

en views.py:
    