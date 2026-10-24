from django import forms
from . import models

class ProductosForm(forms.ModelForm):
    class Meta:
        model = models.Productos
        fields = ["nombre", "precio", "cantidad", "fecha_ingreso", "categoria", "umbral_minimo", "imagen"]
        widgets = {
            "fecha_ingreso": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = models.Categoria
        fields = "__all__"