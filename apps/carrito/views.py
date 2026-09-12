from django.shortcuts import redirect, render
from carrito.cart import Carrito

from productos.models import Productos

from django.core.mail import send_mail
from django.shortcuts import render, redirect

from django.http import HttpResponseBadRequest, HttpResponseRedirect

from django.conf import settings
import requests

def carrito(request):
    productos = Productos.objects.all()
    return render(request, "carrito/index.html",{"productos": productos})

def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)

    mensaje = carrito.agregar_prod(producto)
    if mensaje == "No hay mas stock de este producto.":
        return render(request, 'productos/index.html', {'mensaje': mensaje})

    return redirect("productos:index")

def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("productos:index")

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Productos.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("productos:index")

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("productos:index")


def enviar_correo(request):
    if request.method == "POST":
        if 'carrito' not in request.session or not request.session['carrito']:
            error_message = "<div style='text-align: center'>"
            error_message += "<h1 style='color: red'>No puedes reservar un carrito vacío</h1>"
            error_message += "<a href='/productos'><button style='btn; background-color: #f44336; color: white'>Volver Atrás</button></a>"
            error_message += "</div>"
            return HttpResponseBadRequest(error_message)
        
        # Obtener la dirección de correo del formulario
        correo = request.POST.get("correo")  

       # Validación de reCAPTCHA
        captcha_response = request.POST.get('g-recaptcha-response')
        secret_key = settings.RECAPTCHA_PRIVATE_KEY
        data = {
            'secret': secret_key,
            'response': captcha_response
        }
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()
        
        # Verificar si el campo de reCAPTCHA está presente y no está vacío
        captcha_response = request.POST.get('g-recaptcha-response')
        if not captcha_response:
            # Si el campo de reCAPTCHA no está presente o está vacío, muestra un mensaje de error o toma la acción correspondiente
            return HttpResponseRedirect('/productos')
    
        # Recopilar la información del carrito
        carrito_info = ""
        total = 0

        for key, value in request.session['carrito'].items():
            carrito_info += f"Producto: {value['nombre']}\n"
            carrito_info += f"Precio: ${value['precio']}\n"
            carrito_info += f"Cantidad: {value['cantidad']}\n"
            carrito_info += f"Subtotal: ${value['acumulado']}\n\n"
            
            # Sumar el subtotal al total
            total += value['acumulado']

        # Cuerpo del mensaje
        mensaje_1 = f"Tus productos escogidos son: \n\n{carrito_info} \n Total de tu reserva: ${total} \n ¡Tienes 24 horas para acercarte al local y pagar para obtener tus productos!"
        mensaje_2 = f"El cliente de correo: {correo}, solicitó la reserva de los siguientes productos: \n\n{carrito_info} \n Total de la reserva: ${total} \n El cliente llegará dentro de las próximas 24 horas."

        # Enviar el correo
        send_mail(
            "Detalles del carrito de compras - Minimarket Los Tios",
            mensaje_1,
            correo,  # Remitente
            [correo],  # Destinatario
            fail_silently=False
        )

        send_mail(
            "¡Un cliente ha solicitado una reserva!",
            mensaje_2,
            correo,  # Remitente
            ["minimarket.lostios@gmail.com"],  # Destinatario
            fail_silently=False
        )

        carrito = Carrito(request)

        # Limpiar Carrito
        carrito.limpiar()

    return render(request, "carrito/confirmacion.html")
