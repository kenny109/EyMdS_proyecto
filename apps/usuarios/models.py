from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=20, null=False)
    apellido = models.CharField(max_length=20, null=False)
    correo = models.CharField(max_length=50, null=False)
    edad = models.IntegerField()
    def __str__(self):
        return f'{self.nombre} {self.apellido}. {self.correo}. Tiene {self.edad} años'
    
