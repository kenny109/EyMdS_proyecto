"""MR-121: marca como vencidas las reservas pendientes con el plazo de 24 h cumplido.

Uso:  python manage.py vencer_reservas
Se puede programar en el Programador de tareas de Windows (o cron en Linux) cada hora.
"""
from django.core.management.base import BaseCommand

from carrito.models import Reserva


class Command(BaseCommand):
    help = "Marca como vencidas las reservas pendientes cuyo plazo de retiro ya pasó."

    def handle(self, *args, **options):
        cantidad = Reserva.vencer_pendientes()
        self.stdout.write(self.style.SUCCESS(f"{cantidad} reserva(s) marcada(s) como vencida(s)."))
