from django.urls import path
    #! Include sirve para traer URLS de las apps
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.index, name="index"),
    # path("", TemplateView.as_view(template_name="productos/index.html"), name="home"),

    path("ingresar_productos", views.ingreso_productos, name="ingresar_productos"),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    ## Categorias
    path("categoria/list/", views.CategoriaList.as_view(), name="categoria_list"),
    path('categoria/create', views.CategoriaCreate.as_view(), name="categoria_create"),
    path('categoria/details/<int:pk>', views.CategoriaDetail.as_view(), name='categoria_details'),
    path('categoria/update/<int:pk>', views.CategoriaUpdate.as_view(), name='categoria_update'),
    path('categoria/delete/<int:pk>', views.CategoriaDelete.as_view(), name='categoria_delete'),

    ### Productos
    path("productos/list/", views.ProductosList.as_view(), name="productos_list"),
    path('productos/create', views.ProductosCreate.as_view(), name="productos_create"),
    path('productos/details/<int:pk>', views.ProductosDetail.as_view(), name='productos_details'),
    path('productos/update/<int:pk>', views.ProductosUpdate.as_view(), name='productos_update'),
    path('productos/delete/<int:pk>', views.ProductosDelete.as_view(), name='productos_delete'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)