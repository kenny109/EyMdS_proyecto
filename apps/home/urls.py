from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "Home"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_request, name="login"),
    # Desde Django 5.0 LogoutView solo acepta POST: el navbar envía un formulario (MR-111)
    path("logout/", LogoutView.as_view(template_name="home/logout.html"), name="logout"),
    path("about/", TemplateView.as_view(template_name="home/about.html"), name="about"),
    path("register/", views.register, name="register"),
]

urlpatterns += staticfiles_urlpatterns()
### Con esto, le agrego los statics files al URL PATTERNS
### Ahora puedo llamar o manipular los archivos staticos
### Desde el HTML, desde los Templates
