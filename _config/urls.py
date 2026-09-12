from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", include("home.urls")),
    path("productos/", include("productos.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("carrito/", include("carrito.urls")),
]

######### PARA IMAGENES

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)