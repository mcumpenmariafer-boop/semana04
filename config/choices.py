"""Opciones (choices) compartidas por todas las apps del proyecto."""
from django.db import models


class EstadoGeneral(models.IntegerChoices):
    INACTIVO = 0, 'Inactivo'
    ACTIVO = 1, 'Activo'


class EstadoEnvio(models.TextChoices):
    PENDIENTE = 'PE', 'Pendiente'
    EN_TRANSITO = 'TR', 'En tránsito'
    ENTREGADO = 'EN', 'Entregado'
    CANCELADO = 'CA', 'Cancelado'


class TipoDocumento(models.TextChoices):
    DNI = 'DNI', 'DNI'
    RUC = 'RUC', 'RUC'
    CE = 'CE', 'Carné de extranjería'


class Cargo(models.TextChoices):
    ADMINISTRADOR = 'ADM', 'Administrador'
    OPERADOR = 'OPE', 'Operador'
    COURIER = 'COU', 'Courier'