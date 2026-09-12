from django.db import models
from django.utils import timezone

# Create your models here.

class Categoria (models.Model):
    nombre = models.CharField(max_length=20, null=False)
    descripcion = models.CharField(max_length=20, null=True)
    imagen = models.ImageField(upload_to="imgprod",blank=False, null=True)

    def __str__(self):
        return self.nombre
        

class Productos(models.Model):
    nombre = models.CharField(max_length=50, null=False)
    precio = models.PositiveIntegerField(null=False)
    cantidad = models.PositiveIntegerField(null=False)
    fecha_ingreso = models.DateField(default=timezone.now, null=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    umbral_minimo = models.PositiveIntegerField(null=True, blank=False)
    imagen = models.ImageField(upload_to="imgprod",blank=False, null=True)
    
    def __str__(self):
        return f'{self.nombre} - ${self.precio}.'
    
