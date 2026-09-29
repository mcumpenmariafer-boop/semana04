from django.db import models

from config.choices import EstadoGeneral, TipoDocumento


class ClienteQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(estado=EstadoGeneral.ACTIVO)


class Cliente(models.Model):
    tipo_doc = models.CharField('Tipo de documento', max_length=3,
                                choices=TipoDocumento.choices,
                                default=TipoDocumento.DNI)
    nro_doc = models.CharField('Nro. documento', max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    estado = models.IntegerField(choices=EstadoGeneral.choices,
                                 default=EstadoGeneral.ACTIVO)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = ClienteQuerySet.as_manager()

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'