from django.http import HttpResponse
from django.shortcuts import render
import pywhatkit as kit
from datetime import datetime

from productos.models import Productos

class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            self.session["carrito"] = {}
            self.carrito = self.session["carrito"]
        else:
            self.carrito = carrito
    
    def agregar_prod(self, Productos):
        id = str(Productos.id)
        if id not in self.carrito:
            self.carrito[id] = {
                "producto_id": Productos.id,
                "nombre": Productos.nombre,
                "acumulado": Productos.precio,
                "precio": Productos.precio,
                "cantidad": 1,
            }
        else:
            if self.carrito[id]["cantidad"] < Productos.cantidad:
                self.carrito[id]["cantidad"] += 1
                self.carrito[id]["acumulado"] += Productos.precio
            else:
                return "No hay mas stock de este producto."

        self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True
    
    def eliminar(self,Productos):
        id = str(Productos.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, Productos):
        id = str(Productos.id)
        if id in self.carrito.keys():
            self.carrito[id]["cantidad"] -= 1
            self.carrito[id]["acumulado"] -= Productos.precio
            if self.carrito[id]["cantidad"] <= 0: self.eliminar(Productos)
            self.guardar_carrito()
    
    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    