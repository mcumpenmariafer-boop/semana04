"""
Carga datos de prueba: clientes, rutas, un empleado y 25 encomiendas.
Uso:  python manage.py cargar_datos
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from clientes.models import Cliente
from config.choices import Cargo, EstadoEnvio
from envios.models import Empleado, Encomienda, HistorialEstado
from rutas.models import Ruta

CLIENTES = [
    ('70123456', 'Carlos', 'Ramírez Torres'), ('70234567', 'Ana', 'Flores Díaz'),
    ('70345678', 'Luis', 'Mendoza Castro'), ('70456789', 'María', 'Quispe Huamán'),
    ('70567890', 'Jorge', 'Vásquez Rojas'), ('70678901', 'Rosa', 'Chávez Paredes'),
    ('70789012', 'Pedro', 'Sánchez Gómez'), ('70890123', 'Lucía', 'Torres Vega'),
]
RUTAS = [
    ('LIM-CIX', 'Lima', 'Chiclayo', '25.00', 2), ('CIX-LIM', 'Chiclayo', 'Lima', '25.00', 2),
    ('CIX-PIU', 'Chiclayo', 'Piura', '15.00', 1), ('LIM-TRU', 'Lima', 'Trujillo', '20.00', 1),
    ('LIM-AQP', 'Lima', 'Arequipa', '35.00', 3),
]
DESCRIPCIONES = ['Caja con ropa', 'Documentos legales', 'Repuestos de auto',
                 'Laptop', 'Libros universitarios', 'Productos de limpieza',
                 'Medicinas', 'Artesanías']
CAMINO = [EstadoEnvio.PENDIENTE, EstadoEnvio.EN_TRANSITO, EstadoEnvio.ENTREGADO]


class Command(BaseCommand):
    help = 'Carga datos de prueba para el Sistema de Encomiendas'

    def handle(self, *args, **options):
        random.seed(4)
        clientes = [Cliente.objects.get_or_create(
            nro_doc=doc, defaults={'nombres': n, 'apellidos': a,
                                   'telefono': f'9{doc[1:]}'})[0]
            for doc, n, a in CLIENTES]
        rutas = [Ruta.objects.get_or_create(
            codigo=c, defaults={'origen': o, 'destino': d,
                                'precio_base': Decimal(p), 'dias_estimados': dias})[0]
            for c, o, d, p, dias in RUTAS]
        empleado, _ = Empleado.objects.get_or_create(
            codigo='EMP-0001',
            defaults={'nombres': 'Juan', 'apellidos': 'Mendoza',
                      'email': 'juan@encomiendas.pe', 'cargo': Cargo.OPERADOR})

        if Encomienda.objects.exists():
            self.stdout.write(self.style.WARNING('Ya existen encomiendas; no se crean nuevas.'))
            return

        hoy = timezone.localdate()
        for i in range(25):
            remitente, destinatario = random.sample(clientes, 2)
            ruta = random.choice(rutas)
            enc = Encomienda.objects.create(
                descripcion=random.choice(DESCRIPCIONES),
                peso_kg=Decimal(random.randint(5, 250)) / 10,
                remitente=remitente, destinatario=destinatario, ruta=ruta,
                empleado_registro=empleado,
                costo_envio=ruta.precio_base + random.randint(0, 20),
                # Algunas con fecha vencida para que aparezcan "con retraso"
                fecha_entrega_est=hoy + timedelta(days=random.randint(-4, 5)),
            )
            # Avanzar el estado un número aleatorio de pasos
            pasos = random.choice([0, 0, 1, 1, 1, 2])
            for nuevo in CAMINO[1:pasos + 1]:
                enc.cambiar_estado(nuevo, empleado, 'Carga inicial de datos')
            if i % 9 == 8 and not enc.esta_entregada:
                enc.cambiar_estado(EstadoEnvio.CANCELADO, empleado, 'Cancelado por el cliente')

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Cliente.objects.count()} clientes, {Ruta.objects.count()} rutas, '
            f'{Encomienda.objects.count()} encomiendas, '
            f'{HistorialEstado.objects.count()} cambios de estado.'))