# forestal_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from .models import Postura, HistorialEstado

User = get_user_model()

@receiver(post_save, sender=Postura)
def crear_historial_estado_inicial(sender, instance, created, **kwargs):
    if created:
        HistorialEstado.objects.create(
            postura=instance,
            estado=instance.estado,  # o Estado.objects.get(nombre='Adquirido') si lo querés forzar
            fecha_cambio=now(),
            usuario=instance.responsable
        )
