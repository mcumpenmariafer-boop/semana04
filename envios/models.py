from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from clientes.models import Cliente
from config.choices import Cargo, EstadoEnvio, EstadoGeneral
from rutas.models import Ruta


# ── Empleado ─────────────────────────────────────────────────────
class Empleado(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='empleado',
                                verbose_name='Usuario del sistema')
    codigo = models.CharField('Código', max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=3, choices=Cargo.choices,
                             default=Cargo.OPERADOR)
    email = models.EmailField(unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    estado = models.IntegerField(choices=EstadoGeneral.choices,
                                 default=EstadoGeneral.ACTIVO)

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    @classmethod
    def desde_usuario(cls, user):
        """
        Devuelve el Empleado asociado al usuario logueado.
        Busca por la relación user, luego por email y, si no existe,
        lo crea automáticamente (útil para el superusuario).
        """
        empleado = cls.objects.filter(user=user).first()
        if empleado:
            return empleado
        if user.email:
            empleado = cls.objects.filter(email=user.email).first()
            if empleado:
                empleado.user = user
                empleado.save(update_fields=['user'])
                return empleado
        return cls.objects.create(
            user=user,
            codigo=f'USR-{user.pk:04d}',
            nombres=user.first_name or user.username,
            apellidos=user.last_name or '',
            email=user.email or f'{user.username}@encomiendas.pe',
            cargo=Cargo.ADMINISTRADOR if user.is_superuser else Cargo.OPERADOR,
        )


# ── Manager personalizado de Encomienda ──────────────────────────
ESTADOS_ACTIVOS = [EstadoEnvio.PENDIENTE, EstadoEnvio.EN_TRANSITO]


class EncomiendaQuerySet(models.QuerySet):
    def activas(self):
        """Encomiendas que aún no se entregan ni se devuelven."""
        return self.filter(estado__in=ESTADOS_ACTIVOS)

    def pendientes(self):
        return self.filter(estado=EstadoEnvio.PENDIENTE)

    def en_transito(self):
        return self.filter(estado=EstadoEnvio.EN_TRANSITO)

    def con_retraso(self):
        """Activas cuya fecha estimada de entrega ya pasó."""
        hoy = timezone.localdate()
        return self.activas().filter(fecha_entrega_est__lt=hoy)

    def con_relaciones(self):
        """Evita el problema N+1 cargando las FK en una sola consulta."""
        return self.select_related('remitente', 'destinatario', 'ruta',
                                   'empleado_registro')


# ── Encomienda ──────────────────────────────────────────────────
class Encomienda(models.Model):
    # Transiciones de estado permitidas
        # Transiciones de estado permitidas
    TRANSICIONES = {
        EstadoEnvio.PENDIENTE: [EstadoEnvio.EN_TRANSITO, EstadoEnvio.CANCELADO],
        EstadoEnvio.EN_TRANSITO: [EstadoEnvio.ENTREGADO, EstadoEnvio.CANCELADO],
        EstadoEnvio.ENTREGADO: [],
        EstadoEnvio.CANCELADO: [],
    }

    codigo = models.CharField('Código de encomienda', max_length=20, unique=True,
                              blank=True,
                              help_text='Déjalo vacío para generarlo automáticamente.')
    descripcion = models.TextField('Descripción')
    peso_kg = models.DecimalField('Peso (kg)', max_digits=8, decimal_places=2)
    volumen_cm3 = models.DecimalField('Volumen (cm³)', max_digits=10,
                                      decimal_places=2, null=True, blank=True)
    remitente = models.ForeignKey(Cliente, on_delete=models.PROTECT,
                                  related_name='envios_enviados')
    destinatario = models.ForeignKey(Cliente, on_delete=models.PROTECT,
                                     related_name='envios_recibidos')
    ruta = models.ForeignKey(Ruta, on_delete=models.PROTECT,
                             related_name='encomiendas')
    empleado_registro = models.ForeignKey(Empleado, on_delete=models.PROTECT,
                                          related_name='encomiendas_registradas',
                                          null=True, blank=True,
                                          verbose_name='Empleado que registró')
    estado = models.CharField(max_length=2, choices=EstadoEnvio.choices,
                              default=EstadoEnvio.PENDIENTE)
    costo_envio = models.DecimalField('Costo de envío (S/)', max_digits=8,
                                      decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_entrega_est = models.DateField('Fecha estimada de entrega',
                                         null=True, blank=True)
    fecha_entrega_real = models.DateField('Fecha de entrega real',
                                          null=True, blank=True)
    observaciones = models.TextField(blank=True)

    objects = EncomiendaQuerySet.as_manager()

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Encomienda'
        verbose_name_plural = 'Encomiendas'

    def __str__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        # Genera el código ENC-AAAA-NNNN si no se indicó
        if not self.codigo:
            anio = timezone.localdate().year
            prefijo = f'ENC-{anio}-'
            ultimo = (Encomienda.objects.filter(codigo__startswith=prefijo)
                      .order_by('-codigo').values_list('codigo', flat=True).first())
            numero = int(ultimo.split('-')[-1]) + 1 if ultimo else 1
            self.codigo = f'{prefijo}{numero:04d}'
        self.codigo = self.codigo.upper()
        super().save(*args, **kwargs)

    # ── Propiedades usadas en los templates ────────────────────
    @property
    def esta_en_transito(self):
        return self.estado == EstadoEnvio.EN_TRANSITO
    
    @property
    def esta_entregada(self):
        """True si ya terminó su ciclo (entregada o cancelada)."""
        return self.estado in (EstadoEnvio.ENTREGADO, EstadoEnvio.CANCELADO)

    @property
    def tiene_retraso(self):
        return (self.estado in ESTADOS_ACTIVOS
                and self.fecha_entrega_est is not None
                and self.fecha_entrega_est < timezone.localdate())

    @property
    def dias_en_transito(self):
        inicio = timezone.localtime(self.fecha_registro).date()
        fin = self.fecha_entrega_real or timezone.localdate()
        return (fin - inicio).days

    def estados_siguientes(self):
        """Lista de (valor, etiqueta) a los que puede pasar."""
        return [(e.value, e.label) for e in self.TRANSICIONES[EstadoEnvio(self.estado)]]

    # ── Lógica de negocio ─────────────────────────────────────
    @transaction.atomic
    def cambiar_estado(self, nuevo_estado, empleado, observacion=''):
        if nuevo_estado not in EstadoEnvio.values:
            raise ValueError('Estado no válido.')
        permitidos = self.TRANSICIONES[EstadoEnvio(self.estado)]
        if nuevo_estado not in permitidos:
            raise ValueError(
                f'No se puede pasar de "{self.get_estado_display()}" a '
                f'"{EstadoEnvio(nuevo_estado).label}".'
            )
        anterior = self.estado
        self.estado = nuevo_estado
        if nuevo_estado == EstadoEnvio.ENTREGADO:
            self.fecha_entrega_real = timezone.localdate()
        self.save()
        HistorialEstado.objects.create(
            encomienda=self, estado_anterior=anterior, estado_nuevo=nuevo_estado,
            empleado=empleado, observacion=observacion,
        )


# ── Historial de cambios de estado ───────────────────────────────
class HistorialEstado(models.Model):
    encomienda = models.ForeignKey(Encomienda, on_delete=models.CASCADE,
                                   related_name='historial')
    estado_anterior = models.CharField(max_length=2, choices=EstadoEnvio.choices)
    estado_nuevo = models.CharField(max_length=2, choices=EstadoEnvio.choices)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT,
                                 related_name='cambios_estado')
    observacion = models.TextField('Observación', blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial de estado'
        verbose_name_plural = 'Historial de estados'

    def __str__(self):
        return f'{self.encomienda} {self.estado_anterior}→{self.estado_nuevo}'