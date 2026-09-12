from django.contrib.staticfiles.urls import staticfiles_urlpatterns
## Con esa importación, maneja archivos estáticos
from django.urls import path
    #! Include sirve para traer URLS de las apps
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from . import views

app_name = "Home"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_request, name="login"),
    path("logout/", LogoutView.as_view(template_name="Home/logout.html"), name="logout"),
    path("about/", TemplateView.as_view(template_name="Home/about.html"), name="about"),
    path("register/", views.register, name="register"),
]

urlpatterns += staticfiles_urlpatterns()
### Con esto, le agrego los statics files al URL PATTERNS
### Ahora puedo llamar o manipular los archivos staticos
### Desde el HTML, desde los Templates