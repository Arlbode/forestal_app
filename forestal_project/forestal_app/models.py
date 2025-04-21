from django.db import models
from django.contrib.auth.models import User

class Especie(models.Model):
    nombre_comun = models.CharField(max_length=100)
    nombre_cientifico = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_comun

class Postura(models.Model):
    ESTADOS = [
        ('Adquirida','Adquirida'),
        ('En Transporte','En Transito'),
        ('Almacenada','Almacenada'),
        ('Sembrada','Sembrada'),
    ]
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    fecha_siembra = models.DateField(null=True, blank=True)
    estado = models.CharField(choices=ESTADOS, default='Adquirida')
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.id} - {self.especie.nombre_comun}"
