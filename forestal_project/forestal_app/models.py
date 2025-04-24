from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.core.files import File

import qrcode
from io import BytesIO

# — Validadores personalizados
def validar_latitud(value):
    if not -90 <= value <= 90:
        raise ValidationError('La latitud debe estar entre -90 y 90.')

def validar_longitud(value):
    if not -180 <= value <= 180:
        raise ValidationError('La longitud debe estar entre -180 y 180.')

# — Modelo: Especie
class Especie(models.Model):
    nombre_comun = models.CharField("Nombre común", max_length=100)
    nombre_cientifico = models.CharField("Nombre científico", max_length=150)

    class Meta:
        verbose_name = "Especie"
        verbose_name_plural = "Especies"

    def __str__(self):
        return self.nombre_comun

# — Modelo: Postura
class Postura(models.Model):
    ESTADOS = [
        ('Adquirida', 'Adquirida'),
        ('En Transporte', 'En Transporte'),
        ('Almacenada', 'Almacenada'),
        ('Sembrada', 'Sembrada'),
    ]

    especie = models.ForeignKey(Especie, on_delete=models.CASCADE)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_latitud])
    longitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_longitud])
    fecha_adquisicion = models.DateField(null=True, blank=True)
    fecha_siembra = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Adquirida')
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    class Meta:
        verbose_name = "Postura"
        verbose_name_plural = "Posturas"
        ordering = ['-fecha_adquisicion']

    def __str__(self):
        return f"{self.id} — {self.especie.nombre_comun} ({self.estado})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Generar QR si es nueva o no tiene QR
        if is_new or not self.qr_code:
            current_site = Site.objects.get_current()
            qr_data = f"{current_site.domain}/escanear/?id={self.id}"

            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            filename = f'qr_postura_{self.id}.png'

            self.qr_code.save(filename, File(buffer), save=False)
            super().save(update_fields=['qr_code'])

    def guardar_historial_estado(self, nuevo_estado, usuario, latitud=None, longitud=None):
        """Registra un cambio de estado con ubicación si está disponible."""
        HistorialEstado.objects.create(
            postura=self,
            estado=nuevo_estado,
            usuario=usuario,
            latitud=latitud,
            longitud=longitud
        )
        self.estado = nuevo_estado
        self.save(update_fields=['estado'])

# — Modelo: Historial de Estado
class HistorialEstado(models.Model):
    postura = models.ForeignKey(Postura, related_name='historial_estados', on_delete=models.CASCADE)
    estado = models.CharField("Estado", max_length=20)
    fecha_cambio = models.DateTimeField("Fecha de cambio", auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historiales de Estado"
        ordering = ['-fecha_cambio']

    def __str__(self):
        fecha = self.fecha_cambio.strftime('%d/%m/%Y %H:%M')
        return f"{self.estado} — {fecha} por {self.usuario.username}"

# — Modelo: Escaneo de Postura
class EscaneoPostura(models.Model):
    postura = models.ForeignKey(Postura, related_name='escaneos', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_latitud])
    longitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_longitud])
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Escaneo de Postura"
        verbose_name_plural = "Escaneos de Postura"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Escaneo #{self.id} — Postura {self.postura.id} en {self.fecha_hora:%d/%m/%Y %H:%M}"
