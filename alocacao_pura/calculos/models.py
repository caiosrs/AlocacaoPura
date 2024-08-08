# models.py

from django.db import models

class CalculoAlocacaoPura(models.Model):
    cargo = models.CharField(max_length=100)
    salario = models.CharField(max_length=10)
    assistencia_medica = models.CharField(max_length=10)
    assistencia_odonto = models.CharField(max_length=10)
    seguro = models.CharField(max_length=10)
    vr = models.CharField(max_length=10)
    va = models.CharField(max_length=10)
    vt = models.CharField(max_length=10)
    gympass = models.CharField(max_length=10)

    def __str__(self):
        return self.cargo
