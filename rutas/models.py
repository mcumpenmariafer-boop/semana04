from django.db import models

from config.choices import EstadoGeneral


class RutaQuerySet(models.QuerySet):
    def activas(self):
        return self.filter(estado=EstadoGeneral.ACTIVO)


class Ruta(models.Model):
    codigo = models.CharField('Código', max_length=10, unique=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    precio_base = models.DecimalField('Precio base (S/)', max_digits=8,
                                      decimal_places=2, default=0)
    dias_estimados = models.PositiveIntegerField('Días estimados', default=1)
    estado = models.IntegerField(choices=EstadoGeneral.choices,
                                 default=EstadoGeneral.ACTIVO)

    objects = RutaQuerySet.as_manager()

    class Meta:
        ordering = ['origen', 'destino']
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'

    def __str__(self):
        return f'{self.origen} → {self.destino}'