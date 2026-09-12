from django.urls import path
    #! Include sirve para traer URLS de las apps
from django.conf import settings
from django.conf.urls.static import static
from .views import home, crear_usuarios, buscar_usuarios

app_name = "usuarios"

urlpatterns = [
    path("", home, name="home"),
    path("crear_usuarios", crear_usuarios, name="crear_usuarios"),
    path('buscar_usuarios/', buscar_usuarios, name='buscar_usuarios'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)